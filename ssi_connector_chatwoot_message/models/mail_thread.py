# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_compute_recipients(self, message, msg_vals):
        """Route customer and portal recipients to Chatwoot when asked.

        Standard Odoo falls back to ``email`` for a partner without
        user. Partners that ticked ``chatwoot_notify`` are switched to
        ``chatwoot``. Recipients of type ``user`` are left untouched:
        their channel comes from ``res.users.notification_type``.

        When the context holds ``chatwoot_force_inbox_id`` (set by the
        composer), every recipient listed in the partners of the message
        is switched to ``chatwoot``, whatever its type. The other
        followers keep their own preference.

        :param message: ``mail.message`` being notified
        :param msg_vals: values of the message, or False
        :return: recipients data, see ``_notify_thread``
        :rtype: dict
        """
        recipient_data = super()._notify_compute_recipients(message, msg_vals)
        if self.env.context.get("chatwoot_force_inbox_id"):
            forced_ids = set(message.sudo().partner_ids.ids)
            for data in recipient_data["partners"]:
                if data["id"] in forced_ids:
                    data["notif"] = "chatwoot"
        candidates = [
            data
            for data in recipient_data["partners"]
            if data["type"] in ("customer", "portal") and data["notif"] != "chatwoot"
        ]
        if not candidates:
            return recipient_data
        enabled_ids = set(
            self.env["res.partner"]
            .sudo()
            .search(
                [
                    ("id", "in", [data["id"] for data in candidates]),
                    ("chatwoot_notify", "=", True),
                ]
            )
            .ids
        )
        for data in candidates:
            if data["id"] in enabled_ids:
                data["notif"] = "chatwoot"
        return recipient_data

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        """Notify recipients, then those who chose Chatwoot.

        :param message: ``mail.message`` to notify
        :param msg_vals: values of the message, or False
        :return: recipients data computed by the standard method
        :rtype: dict
        """
        recipients_data = super()._notify_thread(message, msg_vals=msg_vals, **kwargs)
        self._notify_record_by_chatwoot(
            message, recipients_data, msg_vals=msg_vals, **kwargs
        )
        return recipients_data

    def _notify_record_by_chatwoot(
        self, message, recipients_data, msg_vals=False, **kwargs
    ):
        """Notification method: Chatwoot.

        Creates one ``mail.notification`` of type ``chatwoot`` and one
        message binding per recipient. The inbox is the one in the
        ``chatwoot_force_inbox_id`` context key for the partners of the
        message, else the preference of the recipient. The binding is exported by a
        queue job. A recipient without a usable inbox gets an
        ``exception`` notification and no job.

        :param message: ``mail.message`` to notify
        :param recipients_data: see ``_notify_thread``
        :param msg_vals: values of the message, or False
        :return: True
        :rtype: bool
        """
        partners_data = [
            data for data in recipients_data["partners"] if data["notif"] == "chatwoot"
        ]
        if not partners_data:
            return True
        users = self.env["res.users"].sudo()
        partners = self.env["res.partner"].sudo()
        forced_inbox = (
            self.env["chatwoot.inbox"]
            .sudo()
            .browse(self.env.context.get("chatwoot_force_inbox_id"))
        )
        forced_ids = set(message.sudo().partner_ids.ids) if forced_inbox else set()
        for data in partners_data:
            if data["id"] in forced_ids:
                inbox = forced_inbox
            elif data["type"] == "user":
                user = users.search([("partner_id", "=", data["id"])], limit=1)
                inbox = user.chatwoot_inbox_id
            else:
                inbox = partners.browse(data["id"]).chatwoot_inbox_id
            self._notify_chatwoot_create_notification(message, data["id"], inbox)
        return True

    def _notify_chatwoot_create_notification(self, message, partner_id, inbox):
        """Create the notification and binding of one recipient.

        :param message: ``mail.message`` to notify
        :param partner_id: ID of the recipient partner
        :param inbox: ``chatwoot.inbox`` chosen by the recipient, may be
            empty
        :return: the created ``mail.notification``
        """
        values = {
            "mail_message_id": message.id,
            "res_partner_id": partner_id,
            "notification_type": "chatwoot",
            "notification_status": "ready",
            "is_read": True,
        }
        usable = (
            inbox
            and inbox.active
            and inbox.allow_outgoing
            and inbox.chatwoot_id
            and inbox.backend_id.active
        )
        if not usable:
            values.update(
                {
                    "notification_status": "exception",
                    "failure_type": "chatwoot_inbox",
                    "failure_reason": "The recipient has no usable Chatwoot inbox.",
                }
            )
        notification = self.env["mail.notification"].sudo().create(values)
        if usable:
            self.env["chatwoot.mail.notification"].sudo().create(
                {"odoo_id": notification.id, "inbox_id": inbox.id}
            )
        return notification

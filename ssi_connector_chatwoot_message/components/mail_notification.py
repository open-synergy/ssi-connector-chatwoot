# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Chatwoot Message Components
===========================

Adapter, binder, export mapper, exporter and listener of the
``chatwoot.mail.notification`` binding.
"""

import logging

import requests

from odoo import _
from odoo.tools import html2plaintext

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)


class ChatwootMailNotificationAdapter(Component):
    """Adapter for the Chatwoot messages API."""

    _name = "chatwoot.mail.notification.adapter"
    _inherit = "chatwoot.backend.adapter"
    _apply_on = ["chatwoot.mail.notification"]
    _usage = "backend.adapter"

    # pylint: disable=W8106
    def create(self, conversation_id, data):
        """Post a message in a Chatwoot conversation.

        Calls ``POST /api/v1/accounts/{id}/conversations/{cid}/messages``.
        A message without attachment is sent as JSON; a message with
        attachments is sent as ``multipart/form-data`` with one
        ``attachments[]`` part per file.

        :param conversation_id: Chatwoot conversation numeric ID
        :param data: dict with ``content``, ``message_type`` and
            optionally ``attachment_ids`` (``ir.attachment`` IDs)
        :return: response dict (contains the message ``id``)
        :rtype: dict
        """
        path = "conversations/{}/messages".format(conversation_id)
        payload = dict(data)
        attachments = (
            self.env["ir.attachment"].sudo().browse(payload.pop("attachment_ids", []))
        )
        if not attachments:
            return self._request("post", path, json=payload)
        # The multipart boundary is part of the Content-Type, which
        # ``requests`` must build itself.
        headers = {
            key: value
            for key, value in self._headers.items()
            if key.lower() != "content-type"
        }
        form = {
            key: str(value).lower() if isinstance(value, bool) else value
            for key, value in payload.items()
        }
        files = [
            (
                "attachments[]",
                (
                    attachment.name,
                    attachment.raw or b"",
                    attachment.mimetype or "application/octet-stream",
                ),
            )
            for attachment in attachments
        ]
        return self._request("post", path, data=form, files=files, headers=headers)


class ChatwootMailNotificationBinder(Component):
    """Binder for chatwoot.mail.notification."""

    _name = "chatwoot.mail.notification.binder"
    _inherit = "chatwoot.binder"
    _apply_on = ["chatwoot.mail.notification"]


class ChatwootMailNotificationExportMapper(Component):
    """Map a message binding to the Chatwoot payload."""

    _name = "chatwoot.mail.notification.export.mapper"
    _inherit = "base.export.mapper"
    _apply_on = ["chatwoot.mail.notification"]
    _collection = "chatwoot.backend"
    _usage = "export.mapper"

    @mapping
    def content(self, record):
        """Map the text of the message.

        The first line holds the author and the document name, then
        come the body as plain text and a link to the document.

        :param record: the ``chatwoot.mail.notification`` binding
        :return: dict with the ``content`` key
        """
        message = record.odoo_id.mail_message_id.sudo()
        title = " - ".join(
            part for part in (message.author_id.name, message.record_name) if part
        )
        lines = [title, html2plaintext(message.body or "")]
        link = self._get_record_link(message)
        if link:
            lines.append(link)
        return {"content": "\n\n".join(line for line in lines if line)}

    @mapping
    def message_type(self, record):
        """Map the direction of the message.

        :param record: the ``chatwoot.mail.notification`` binding
        :return: dict with the ``message_type`` key
        """
        return {"message_type": "outgoing", "private": False}

    @mapping
    def attachment_ids(self, record):
        """Map the attachments of the message.

        :param record: the ``chatwoot.mail.notification`` binding
        :return: dict with the ``attachment_ids`` key, the IDs of the
            ``ir.attachment`` records sent along with the message
        """
        message = record.odoo_id.mail_message_id.sudo()
        return {"attachment_ids": message.attachment_ids.ids}

    def _get_record_link(self, message):
        """Build the absolute link to the document of the message.

        :param message: ``mail.message`` being sent
        :return: the URL, or an empty string when the message has no
            document
        :rtype: str
        """
        if not message.model or not message.res_id:
            return ""
        document = self.env[message.model].sudo().browse(message.res_id).exists()
        if not document or not hasattr(document, "_notify_get_action_link"):
            return ""
        base_url = (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url") or ""
        )
        return base_url.rstrip("/") + document._notify_get_action_link("view")


class ChatwootMailNotificationExporter(Component):
    """Export a message binding to Chatwoot."""

    _name = "chatwoot.mail.notification.exporter"
    _inherit = "generic.exporter"
    _apply_on = ["chatwoot.mail.notification"]
    _collection = "chatwoot.backend"
    _usage = "exporter"

    _default_binding_field = "chatwoot_bind_ids"

    def run(self, binding, *args, **kwargs):
        """Export the binding and record the outcome on the notification.

        A permanent error is stored on the ``mail.notification`` and not
        raised again: the notification is the source of truth for the
        failure. A retryable error is raised again so that the job is
        retried, except on the last attempt where it is stored too.

        :param binding: the ``chatwoot.mail.notification`` binding
        :return: result message of the export
        """
        if binding.chatwoot_id:
            return _("Already exported.")
        try:
            return super().run(binding, *args, **kwargs)
        except RetryableJobError as exc:
            if not self._is_last_attempt():
                raise
            self._mark_exception(str(exc))
        except (requests.exceptions.HTTPError, ValueError) as exc:
            self._mark_exception(str(exc))
        return _("Notification marked as exception.")

    def _is_last_attempt(self):
        """Tell whether the running queue job has no retry left.

        The retry counter is stored before the job runs, so the current
        attempt is ``retry + 1``.

        :return: True when this attempt is the last one allowed
        :rtype: bool
        """
        job_uuid = self.env.context.get("job_uuid")
        if not job_uuid:
            return False
        job = self.env["queue.job"].sudo().search([("uuid", "=", job_uuid)], limit=1)
        return bool(job.max_retries) and job.retry + 1 >= job.max_retries

    def _mark_exception(self, reason):
        """Store a server error on the notification of the binding.

        :param reason: text of the error
        """
        _logger.warning(
            "Chatwoot message binding id=%s failed: %s", self.binding.id, reason
        )
        self.binding.odoo_id.sudo().write(
            {
                "notification_status": "exception",
                "failure_type": "chatwoot_server",
                "failure_reason": reason,
            }
        )

    def _export_dependencies(self):
        """Export the contact, the contact inbox and the conversation.

        Missing bindings are created, then exported in this order.
        """
        partner = self.binding.odoo_id.res_partner_id
        self._export_dependency(
            partner, "chatwoot.res.partner", component_usage="exporter"
        )
        partner_binding = self._get_or_create_binding(
            "chatwoot.res.partner",
            [
                ("odoo_id", "=", partner.id),
                ("backend_id", "=", self.backend_record.id),
            ],
            {"odoo_id": partner.id, "backend_id": self.backend_record.id},
        )
        contact_inbox = self._get_or_create_binding(
            "chatwoot.contact.inbox",
            [
                ("partner_binding_id", "=", partner_binding.id),
                ("inbox_id", "=", self.binding.inbox_id.id),
            ],
            {
                "partner_binding_id": partner_binding.id,
                "inbox_id": self.binding.inbox_id.id,
            },
        )
        self._export_dependency(
            contact_inbox, "chatwoot.contact.inbox", component_usage="exporter"
        )
        conversation = self._get_or_create_binding(
            "chatwoot.conversation",
            [("contact_inbox_id", "=", contact_inbox.id)],
            {"contact_inbox_id": contact_inbox.id},
        )
        self._export_dependency(
            conversation, "chatwoot.conversation", component_usage="exporter"
        )
        self.binding.with_context(connector_no_export=True).write(
            {"conversation_id": conversation.id}
        )

    def _get_or_create_binding(self, model_name, domain, values):
        """Return the binding matching the domain, creating it if needed.

        :param model_name: name of the binding model
        :param domain: search domain
        :param values: values used to create the binding
        :return: the binding record
        """
        model = self.env[model_name].with_context(active_test=False).sudo()
        binding = model.search(domain, limit=1)
        if not binding:
            binding = model.with_context(connector_no_export=True).create(values)
        return binding

    def _create(self, data):
        """Post the message in Chatwoot and return its ID.

        :param data: payload built by the export mapper
        :return: the message ID returned by Chatwoot
        :rtype: str
        """
        conversation_id = self.binding.conversation_id.chatwoot_id
        result = self.backend_adapter.create(conversation_id, data)
        message_id = result.get("id")
        if not message_id:
            raise ValueError(
                "Chatwoot returned no message ID for binding %s. "
                "Full response: %s" % (self.binding.id, result)
            )
        return str(message_id)

    def _after_export(self):
        """Mark the notification as sent."""
        self.binding.odoo_id.sudo().write(
            {
                "notification_status": "sent",
                "failure_type": False,
                "failure_reason": False,
            }
        )


def _no_connector_export(self, record, *args, **kwargs):
    """Tell whether connector exports are disabled by context.

    :param record: the binding being created
    :return: truthy when ``connector_no_export`` or ``no_connector_export``
        is set in the context
    """
    return self.env.context.get("connector_no_export") or self.env.context.get(
        "no_connector_export"
    )


class ChatwootMailNotificationListener(Component):
    """Queue the export of a message binding when it is created."""

    _name = "chatwoot.mail.notification.listener"
    _inherit = "base.connector.listener"
    _apply_on = ["chatwoot.mail.notification"]

    @skip_if(lambda self, record, **kwargs: _no_connector_export(self, record))
    def on_record_create(self, record, fields=None):
        """Queue an export job on the Chatwoot channel.

        :param record: the created ``chatwoot.mail.notification``
        :param fields: names of the fields given at creation
        """
        record.with_delay(channel="root.chatwoot").export_record()

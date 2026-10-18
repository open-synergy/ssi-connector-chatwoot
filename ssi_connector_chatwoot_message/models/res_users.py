# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    notification_type = fields.Selection(
        selection_add=[("chatwoot", "Handle by Chatwoot")],
        ondelete={"chatwoot": "set default"},
    )
    chatwoot_inbox_id = fields.Many2one(
        comodel_name="chatwoot.inbox",
        string="Chatwoot Inbox",
        domain="[('allow_outgoing', '=', True)]",
        help="Chatwoot inbox that delivers the chatter notifications of "
        "this user when the notification policy is Handle by Chatwoot",
    )

    def __init__(self, pool, cr):
        """Let users read and change their own Chatwoot inbox.

        :param pool: the model registry
        :param cr: the database cursor
        """
        super().__init__(pool, cr)
        # duplicate lists to avoid modifying the original references
        pool[self._name].SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        pool[self._name].SELF_WRITEABLE_FIELDS.extend(["chatwoot_inbox_id"])
        pool[self._name].SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        pool[self._name].SELF_READABLE_FIELDS.extend(["chatwoot_inbox_id"])

    @api.constrains("notification_type", "chatwoot_inbox_id")
    def _check_chatwoot_inbox_required(self):
        """Require an inbox when the user is handled by Chatwoot.

        :raises ValidationError: when the notification policy is
            Handle by Chatwoot and no inbox is selected
        """
        for user in self.sudo():
            if not user._check_chatwoot_inbox_required_condition():
                error_message = """
Context: Save user notification policy
Database ID: %s
Problem: Handle by Chatwoot needs a Chatwoot inbox
Solution: Select a Chatwoot inbox or choose another notification policy
""" % (
                    user.id,
                )
                raise ValidationError(_(error_message))

    def _check_chatwoot_inbox_required_condition(self):
        """Tell whether a Chatwoot user has an inbox.

        :return: True when valid; never raises
        """
        self.ensure_one()
        if self.notification_type != "chatwoot":
            return True
        return bool(self.chatwoot_inbox_id)

    def _chatwoot_enable_partner_sync(self):
        """Flag the partner of Chatwoot users for the contact sync."""
        partners = (
            self.sudo()
            .filtered(lambda user: user.notification_type == "chatwoot")
            .mapped("partner_id")
            .filtered(lambda partner: not partner.sync_to_chatwoot)
        )
        if partners:
            partners.write({"sync_to_chatwoot": True})

    @api.model_create_multi
    def create(self, vals_list):
        """Create users and enable the contact sync of Chatwoot users.

        :param vals_list: list of values of the users to create
        :return: the created users
        """
        users = super().create(vals_list)
        users._chatwoot_enable_partner_sync()
        return users

    def write(self, vals):
        """Write users and enable the contact sync of Chatwoot users.

        :param vals: values to write
        :return: result of the standard write
        """
        result = super().write(vals)
        if "notification_type" in vals:
            self._chatwoot_enable_partner_sync()
        return result

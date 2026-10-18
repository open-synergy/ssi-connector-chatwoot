# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    chatwoot_notify = fields.Boolean(
        string="Notify via Chatwoot",
        default=False,
        help="If enabled, chatter notifications of this partner are sent "
        "through Chatwoot instead of email. Does not apply to internal "
        "users, who use their own notification policy.",
    )
    chatwoot_inbox_id = fields.Many2one(
        comodel_name="chatwoot.inbox",
        string="Chatwoot Inbox",
        domain="[('allow_outgoing', '=', True)]",
        help="Chatwoot inbox that delivers the chatter notifications of "
        "this partner",
    )

    @api.constrains("chatwoot_notify", "chatwoot_inbox_id")
    def _check_chatwoot_inbox_required(self):
        """Require an inbox when the partner is notified via Chatwoot.

        :raises ValidationError: when Notify via Chatwoot is enabled and
            no inbox is selected
        """
        for partner in self.sudo():
            if not partner._check_chatwoot_inbox_required_condition():
                error_message = """
Context: Save partner Chatwoot notification
Database ID: %s
Problem: Notify via Chatwoot needs a Chatwoot inbox
Solution: Select a Chatwoot inbox or disable Notify via Chatwoot
""" % (
                    partner.id,
                )
                raise ValidationError(_(error_message))

    def _check_chatwoot_inbox_required_condition(self):
        """Tell whether a partner notified via Chatwoot has an inbox.

        :return: True when valid; never raises
        """
        self.ensure_one()
        if not self.chatwoot_notify:
            return True
        return bool(self.chatwoot_inbox_id)

    @api.model_create_multi
    def create(self, vals_list):
        """Create partners; Notify via Chatwoot enables the contact sync.

        :param vals_list: list of values of the partners to create
        :return: the created partners
        """
        for vals in vals_list:
            if vals.get("chatwoot_notify"):
                vals["sync_to_chatwoot"] = True
        return super().create(vals_list)

    def write(self, vals):
        """Write partners; Notify via Chatwoot enables the contact sync.

        :param vals: values to write
        :return: result of the standard write
        """
        if vals.get("chatwoot_notify"):
            vals = dict(vals, sync_to_chatwoot=True)
        return super().write(vals)

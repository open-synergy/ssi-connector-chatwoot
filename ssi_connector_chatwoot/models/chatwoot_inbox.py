# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ChatwootInbox(models.Model):
    """Chatwoot inbox imported from a Chatwoot account.

    An inbox is a channel (WhatsApp, Telegram, email, ...) configured in
    Chatwoot. It has no Odoo counterpart, so it is a plain binding.
    Administrators decide which inboxes may be used for outgoing messages.
    """

    _name = "chatwoot.inbox"
    _inherit = "external.binding"
    _description = "Chatwoot Inbox"
    _order = "backend_id, name"

    name = fields.Char(
        string="Name",
        required=True,
        help="Inbox name as defined in Chatwoot",
    )
    backend_id = fields.Many2one(
        comodel_name="chatwoot.backend",
        string="Chatwoot Backend",
        required=True,
        ondelete="cascade",
        help="Chatwoot backend this inbox belongs to",
    )
    chatwoot_id = fields.Char(
        string="Chatwoot Inbox ID",
        help="Identifier of the inbox in Chatwoot",
    )
    channel_type = fields.Char(
        string="Channel Type",
        readonly=True,
        help="Raw channel type reported by Chatwoot, for information only",
    )
    allow_outgoing = fields.Boolean(
        string="Allow Outgoing Messages",
        default=False,
        help="Tick to allow Odoo to send messages through this inbox",
    )
    sync_date = fields.Datetime(
        string="Last Synchronization",
        help="Date of the last import of this inbox",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Untick to archive the inbox",
    )

    @api.constrains("backend_id", "chatwoot_id")
    def _check_chatwoot_inbox_unique(self):
        """Reject a second inbox with the same backend and Chatwoot ID.

        :raises ValidationError: when another inbox (archived ones
            included) has the same backend and Chatwoot ID
        """
        for inbox in self.sudo():
            if not inbox._check_chatwoot_inbox_unique_condition():
                error_message = """
Context: Save Chatwoot inbox
Database ID: %s
Problem: An inbox with the same Chatwoot ID already exists for this backend
Solution: Edit the existing inbox instead of creating another one
""" % (
                    inbox.id,
                )
                raise ValidationError(_(error_message))

    def _check_chatwoot_inbox_unique_condition(self):
        """Tell whether no other inbox shares backend and Chatwoot ID.

        :return: True when valid or when there is no Chatwoot ID
        """
        self.ensure_one()
        if not self.chatwoot_id:
            return True
        duplicates = (
            self.with_context(active_test=False)
            .sudo()
            .search_count(
                [
                    ("id", "!=", self.id),
                    ("backend_id", "=", self.backend_id.id),
                    ("chatwoot_id", "=", self.chatwoot_id),
                ]
            )
        )
        return not duplicates

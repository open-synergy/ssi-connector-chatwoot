# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ChatwootConversation(models.Model):
    """Binding between a Chatwoot contact inbox and a Chatwoot conversation.

    There is one conversation per contact inbox. It is created on the
    first message sent and reused for every following message.
    """

    _name = "chatwoot.conversation"
    _inherit = "external.binding"
    _description = "Chatwoot Conversation Binding"
    _order = "id desc"

    contact_inbox_id = fields.Many2one(
        comodel_name="chatwoot.contact.inbox",
        string="Contact Inbox",
        required=True,
        ondelete="cascade",
        help="Contact inbox binding this conversation belongs to",
    )
    backend_id = fields.Many2one(
        comodel_name="chatwoot.backend",
        string="Chatwoot Backend",
        related="contact_inbox_id.backend_id",
        store=True,
        help="Chatwoot backend of the contact inbox",
    )
    chatwoot_id = fields.Char(
        string="Chatwoot Conversation ID",
        help="Identifier of the conversation in Chatwoot",
    )
    sync_date = fields.Datetime(
        string="Last Synchronization",
        help="Date of the last export of this conversation",
    )

    @api.constrains("contact_inbox_id")
    def _check_chatwoot_conversation_unique(self):
        """Reject a second conversation for the same contact inbox.

        :raises ValidationError: when another conversation is already
            bound to the same contact inbox
        """
        for record in self.sudo():
            if not record._check_chatwoot_conversation_unique_condition():
                error_message = """
Context: Save Chatwoot conversation binding
Database ID: %s
Problem: A conversation already exists for this contact inbox
Solution: Reuse the existing conversation instead of creating another one
""" % (
                    record.id,
                )
                raise ValidationError(_(error_message))

    def _check_chatwoot_conversation_unique_condition(self):
        """Tell whether no other conversation shares the contact inbox.

        :return: True when valid; never raises
        """
        self.ensure_one()
        duplicates = (
            self.with_context(active_test=False)
            .sudo()
            .search_count(
                [
                    ("id", "!=", self.id),
                    ("contact_inbox_id", "=", self.contact_inbox_id.id),
                ]
            )
        )
        return not duplicates

    def export_record(self):
        """Export this conversation to Chatwoot.

        Designed to be called via ``with_delay()``.

        :return: the result message of the exporter
        """
        self.ensure_one()
        binding = self.sudo()
        with binding.backend_id.work_on(self._name) as work:
            exporter = work.component(usage="exporter")
            return exporter.run(binding)

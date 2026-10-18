# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    send_via = fields.Selection(
        string="Send Via",
        selection=[("email", "Email"), ("chatwoot", "Chatwoot")],
        default="email",
        required=True,
        help="Channel used to deliver the message to the recipients added "
        "in this composer. Email keeps the standard behavior; Chatwoot "
        "sends the message and its attachments through a Chatwoot inbox.",
    )
    chatwoot_inbox_id = fields.Many2one(
        string="Chatwoot Inbox",
        comodel_name="chatwoot.inbox",
        domain="[('allow_outgoing', '=', True)]",
        help="Chatwoot inbox that delivers the message. Required when the "
        "message is sent via Chatwoot; it takes precedence over the "
        "inbox preference of each recipient.",
    )

    @api.constrains("send_via", "chatwoot_inbox_id")
    def _check_chatwoot_inbox_id(self):
        """Reject a Chatwoot delivery without a Chatwoot inbox.

        :raises ValidationError: when ``send_via`` is Chatwoot and no
            inbox is selected
        """
        for record in self.sudo():
            if not record._check_chatwoot_inbox_id_condition():
                error_message = """
Context: Send message via Chatwoot
Database ID: %s
Problem: No Chatwoot inbox is selected
Solution: Select a Chatwoot inbox or send the message via Email
""" % (
                    record.id,
                )
                raise ValidationError(_(error_message))

    def _check_chatwoot_inbox_id_condition(self):
        """Tell whether a Chatwoot delivery has an inbox.

        :return: True when valid; never raises
        :rtype: bool
        """
        self.ensure_one()
        return self.send_via != "chatwoot" or bool(self.chatwoot_inbox_id)

    def send_mail(self, auto_commit=False):
        """Send the message, through Chatwoot when the wizard asks for it.

        A wizard in ``comment`` mode with ``send_via`` set to Chatwoot
        posts its message with the ``chatwoot_force_inbox_id`` context
        key; ``mail.thread`` then routes the recipients of the message
        to Chatwoot instead of email.

        :param auto_commit: commit after each batch of emails
        :return: result of the standard method
        """
        result = None
        for wizard in self:
            if wizard.composition_mode == "comment" and wizard.send_via == "chatwoot":
                wizard = wizard.with_context(
                    chatwoot_force_inbox_id=wizard.chatwoot_inbox_id.id
                )
            result = super(MailComposeMessage, wizard).send_mail(
                auto_commit=auto_commit
            )
        return result

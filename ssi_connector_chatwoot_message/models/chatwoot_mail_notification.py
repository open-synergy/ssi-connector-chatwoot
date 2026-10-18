# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ChatwootMailNotification(models.Model):
    """Binding between a chatter notification and a Chatwoot message.

    One binding stands for one message sent to one recipient. Odoo only
    creates it; the export to Chatwoot runs in a queue job.
    """

    _name = "chatwoot.mail.notification"
    _inherit = "external.binding"
    _description = "Chatwoot Message Binding"
    _order = "id desc"

    odoo_id = fields.Many2one(
        comodel_name="mail.notification",
        string="Notification",
        required=True,
        ondelete="cascade",
        help="Chatter notification sent through Chatwoot",
    )
    inbox_id = fields.Many2one(
        comodel_name="chatwoot.inbox",
        string="Inbox",
        required=True,
        ondelete="restrict",
        help="Chatwoot inbox the message is sent through",
    )
    conversation_id = fields.Many2one(
        comodel_name="chatwoot.conversation",
        string="Conversation",
        ondelete="set null",
        help="Chatwoot conversation the message was posted in",
    )
    backend_id = fields.Many2one(
        comodel_name="chatwoot.backend",
        string="Chatwoot Backend",
        related="inbox_id.backend_id",
        store=True,
        help="Chatwoot backend of the inbox",
    )
    chatwoot_id = fields.Char(
        string="Chatwoot Message ID",
        help="Identifier of the message in Chatwoot",
    )
    sync_date = fields.Datetime(
        string="Last Synchronization",
        help="Date of the last export of this message",
    )

    def export_record(self):
        """Export this message to Chatwoot.

        Designed to be called via ``with_delay()``. The job runs as
        superuser because the user who posted the message may not be
        allowed to write bindings.

        :return: the result message of the exporter
        """
        self.ensure_one()
        binding = self.sudo()
        with binding.backend_id.work_on(self._name) as work:
            exporter = work.component(usage="exporter")
            return exporter.run(binding)

# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class MailNotification(models.Model):
    _inherit = "mail.notification"

    # Chatwoot delivery channel, same pattern as the ``sms`` module.
    notification_type = fields.Selection(
        selection_add=[("chatwoot", "Chatwoot")],
        ondelete={"chatwoot": "set default"},
    )
    failure_type = fields.Selection(
        selection_add=[
            ("chatwoot_inbox", "No Chatwoot Inbox"),
            ("chatwoot_server", "Chatwoot Server Error"),
        ],
    )
    chatwoot_bind_ids = fields.One2many(
        comodel_name="chatwoot.mail.notification",
        inverse_name="odoo_id",
        string="Chatwoot Bindings",
        copy=False,
        help="Chatwoot message bindings of this notification",
    )

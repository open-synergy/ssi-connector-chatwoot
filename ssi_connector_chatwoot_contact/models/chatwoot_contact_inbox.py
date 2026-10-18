# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ChatwootContactInbox(models.Model):
    """Binding between a Chatwoot contact and a Chatwoot inbox.

    Chatwoot needs a ``source_id`` to open a conversation. It is created
    by pairing a contact with an inbox and is kept in ``chatwoot_id``.
    """

    _name = "chatwoot.contact.inbox"
    _inherit = "external.binding"
    _description = "Chatwoot Contact Inbox Binding"
    _order = "name"

    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True,
        help="Partner and inbox of this binding",
    )
    partner_binding_id = fields.Many2one(
        comodel_name="chatwoot.res.partner",
        string="Contact Binding",
        required=True,
        ondelete="cascade",
        help="Chatwoot contact binding of the partner",
    )
    inbox_id = fields.Many2one(
        comodel_name="chatwoot.inbox",
        string="Inbox",
        required=True,
        ondelete="cascade",
        domain="[('allow_outgoing', '=', True)]",
        help="Chatwoot inbox paired with the contact",
    )
    backend_id = fields.Many2one(
        comodel_name="chatwoot.backend",
        string="Chatwoot Backend",
        related="inbox_id.backend_id",
        store=True,
        help="Chatwoot backend of the inbox",
    )
    chatwoot_id = fields.Char(
        string="Source ID",
        help="Source ID returned by Chatwoot for this contact and inbox",
    )
    sync_date = fields.Datetime(
        string="Last Synchronization",
        help="Date of the last export of this binding",
    )

    @api.depends("partner_binding_id.name", "inbox_id.name")
    def _compute_name(self):
        """Compute the display name as ``<partner> / <inbox>``."""
        for record in self:
            result = ""
            if record.partner_binding_id and record.inbox_id:
                result = "%s / %s" % (
                    record.partner_binding_id.name,
                    record.inbox_id.name,
                )
            record.name = result

    @api.constrains("partner_binding_id", "inbox_id")
    def _check_chatwoot_contact_inbox_unique(self):
        """Reject a second binding for the same contact and inbox.

        :raises ValidationError: when another binding already pairs the
            same contact binding with the same inbox
        """
        for record in self.sudo():
            if not record._check_chatwoot_contact_inbox_unique_condition():
                error_message = """
Context: Save Chatwoot contact inbox binding
Database ID: %s
Problem: A binding already exists for this contact and inbox
Solution: Edit the existing binding instead of creating another one
""" % (
                    record.id,
                )
                raise ValidationError(_(error_message))

    def _check_chatwoot_contact_inbox_unique_condition(self):
        """Tell whether no other binding shares contact and inbox.

        :return: True when valid; never raises
        """
        self.ensure_one()
        duplicates = (
            self.with_context(active_test=False)
            .sudo()
            .search_count(
                [
                    ("id", "!=", self.id),
                    ("partner_binding_id", "=", self.partner_binding_id.id),
                    ("inbox_id", "=", self.inbox_id.id),
                ]
            )
        )
        return not duplicates

    @api.constrains("partner_binding_id", "inbox_id")
    def _check_chatwoot_contact_inbox_backend(self):
        """Reject a contact and an inbox that belong to different backends.

        :raises ValidationError: when the backend of the contact binding
            differs from the backend of the inbox
        """
        for record in self.sudo():
            if not record._check_chatwoot_contact_inbox_backend_condition():
                error_message = """
Context: Save Chatwoot contact inbox binding
Database ID: %s
Problem: The contact and the inbox belong to different backends
Solution: Select an inbox of the backend of the contact binding
""" % (
                    record.id,
                )
                raise ValidationError(_(error_message))

    def _check_chatwoot_contact_inbox_backend_condition(self):
        """Tell whether contact binding and inbox share the same backend.

        :return: True when valid; never raises
        """
        self.ensure_one()
        return self.partner_binding_id.backend_id == self.inbox_id.backend_id

    def action_export(self):
        """Queue the export of this binding to Chatwoot.

        :return: a client action showing that the export was queued
        """
        self.ensure_one()
        self.with_delay().export_record()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Export Contact Inbox",
                "message": "The contact inbox export has been queued.",
                "type": "success",
                "sticky": False,
            },
        }

    def export_record(self):
        """Export this binding to Chatwoot.

        Designed to be called via ``with_delay()``.

        :return: the result message of the exporter
        """
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage="exporter")
            return exporter.run(self)

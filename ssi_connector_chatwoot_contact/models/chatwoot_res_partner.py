# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Binding model: chatwoot.res.partner
====================================

This model is the *binding* between an Odoo ``res.partner`` and a Chatwoot
contact.  It uses the ``_inherits`` mechanism from the OCA connector pattern:
each binding record "wraps" a real res.partner record via ``odoo_id`` and adds
Chatwoot-specific fields (backend, external ID, sync date).

To push a partner to Chatwoot, create a ``chatwoot.res.partner`` record that
references the partner and the desired Chatwoot backend.  You can also call
``export_record()`` directly on an existing binding.
"""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ChatwootResPartner(models.Model):
    """Binding between an Odoo res.partner and a Chatwoot contact."""

    _name = "chatwoot.res.partner"
    _inherit = "external.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "Chatwoot Contact Binding"
    _rec_name = "name"

    _sql_constraints = [
        (
            "chatwoot_partner_uniq",
            "unique(backend_id, odoo_id)",
            "A Chatwoot binding already exists for this partner and backend.",
        )
    ]

    # -----------------------------------------------------------------
    # Binding fields (required by connector.external.binding / binder)
    # -----------------------------------------------------------------
    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        ondelete="cascade",
    )
    backend_id = fields.Many2one(
        comodel_name="chatwoot.backend",
        string="Chatwoot Backend",
        required=True,
        ondelete="restrict",
    )
    chatwoot_id = fields.Char(
        string="Chatwoot Contact ID",
    )
    sync_date = fields.Datetime(
        string="Last Synchronization",
    )

    # -----------------------------------------------------------------
    # Convenience methods
    # -----------------------------------------------------------------

    @api.model
    def export_batch(self, backend, domain=None):
        """Export all partners marked for sync on a given backend.

        :param backend: ``chatwoot.backend`` record
        :param domain: optional extra domain on ``res.partner``
        """
        domain = domain or []
        partners = self.env["res.partner"].search(
            [("sync_to_chatwoot", "=", True)] + domain
        )
        for partner in partners:
            # Find existing binding or create a new one
            binding = self.with_context(active_test=False).search(
                [
                    ("odoo_id", "=", partner.id),
                    ("backend_id", "=", backend.id),
                ]
            )
            if not binding:
                binding = self.create({"odoo_id": partner.id, "backend_id": backend.id})
            binding.with_delay().export_record()

    def export_record(self, fields=None):
        """Queue an export job for this binding.

        :param fields: list of Odoo field names that changed (used by
                       the mapper's ``changed_by`` decorators to limit
                       the payload to only the modified fields on update).
                       Pass ``None`` to export all fields (e.g. on create).
        """
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage="exporter")
            return exporter.run(self, fields=fields)

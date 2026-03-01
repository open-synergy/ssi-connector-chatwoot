# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
res.partner extension
=====================

Adds two fields to res.partner:

* ``sync_to_chatwoot`` (Boolean) – opt-in flag to include the partner in the
  Chatwoot sync.  Only partners with this flag set will be exported.

* ``chatwoot_bind_ids`` (One2many) – list of Chatwoot binding records for
  this partner (one per backend).
"""

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sync_to_chatwoot = fields.Boolean(
        string="Sync to Chatwoot",
        default=False,
        help="If enabled, this contact will be synchronised to Chatwoot "
        "as a contact whenever it is created or updated.",
    )

    chatwoot_bind_ids = fields.One2many(
        comodel_name="chatwoot.res.partner",
        inverse_name="odoo_id",
        string="Chatwoot Bindings",
        copy=False,
    )

    @api.model
    def _chatwoot_sync_domain(self):
        """Return the domain for partners eligible for Chatwoot sync."""
        return [("sync_to_chatwoot", "=", True)]

    def action_force_export_to_chatwoot(self):
        """Manually trigger an export to all active Chatwoot backends."""
        backends = self.env["chatwoot.backend"].search([("active", "=", True)])
        for backend in backends:
            for partner in self.filtered("sync_to_chatwoot"):
                binding = (
                    self.env["chatwoot.res.partner"]
                    .with_context(active_test=False)
                    .search(
                        [
                            ("odoo_id", "=", partner.id),
                            ("backend_id", "=", backend.id),
                        ]
                    )
                )
                if not binding:
                    binding = self.env["chatwoot.res.partner"].create(
                        {"odoo_id": partner.id, "backend_id": backend.id}
                    )
                binding.with_delay().export_record()
        return True

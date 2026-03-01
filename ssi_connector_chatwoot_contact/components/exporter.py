# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Exporter: chatwoot.res.partner
================================

Inherits ``generic.exporter`` from the OCA connector framework and
overrides only the parts that are specific to the Chatwoot API:

* ``_create`` – parses the Chatwoot contact ID from the POST response.
* ``_update`` – plain PUT call (adapter handles it; override only for logging).

The full export flow (locking, binder.bind, commit) is handled by
``GenericExporter.run()``.
"""

import logging

from odoo import fields

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ChatwootResPartnerExporter(Component):
    """Export a res.partner binding to Chatwoot."""

    _name = "chatwoot.res.partner.exporter"
    _inherit = "generic.exporter"
    _apply_on = ["chatwoot.res.partner"]
    _collection = "chatwoot.backend"
    _usage = "exporter"

    # Used by _export_dependency when auto-creating dependency bindings.
    _default_binding_field = "chatwoot_bind_ids"

    def run(self, binding, fields=None, *args, **kwargs):
        """Run the export and ensure chatwoot_id is persisted on the binding.

        :param fields: list of Odoo field names that changed; passed to
                       ``GenericExporter._run()`` so only the relevant
                       mapper methods (decorated with ``@changed_by``) are
                       included in an update payload.
        """
        result = super().run(binding, fields=fields, *args, **kwargs)
        # Safety-net: the binder already wrote chatwoot_id inside super().run(),
        # but we log the final state for verification.
        _logger.info(
            "Export finished for binding id=%s: chatwoot_id=%s sync_date=%s",
            self.binding.id,
            self.binding.chatwoot_id,
            self.binding.sync_date,
        )
        return result

    def _create(self, data):
        """Create the Chatwoot contact and return its ID as a string."""
        result = self.backend_adapter.create(data)

        _logger.debug(
            "Chatwoot create contact response for partner '%s': %s",
            self.binding.odoo_id.display_name,
            result,
        )

        # Chatwoot POST /contacts response (official docs):
        # {
        #   "payload": [ { "id": 123, ... } ],   ← list of contacts
        #   "id": 123,                             ← top-level id (same contact)
        #   "availability_status": "online"
        # }
        #
        # Try top-level "id" first (most direct), then dig into payload.
        chatwoot_id = result.get("id")

        if not chatwoot_id:
            payload = result.get("payload")
            if isinstance(payload, list) and payload:
                chatwoot_id = payload[0].get("id")
            elif isinstance(payload, dict):
                chatwoot_id = payload.get("id") or (payload.get("contact") or {}).get(
                    "id"
                )

        if not chatwoot_id:
            raise ValueError(
                "Chatwoot returned no ID after creating contact for binding %s. "
                "Full response: %s" % (self.binding.id, result)
            )

        _logger.info(
            "Created Chatwoot contact id=%s for partner '%s' (binding id=%s)",
            chatwoot_id,
            self.binding.odoo_id.display_name,
            self.binding.id,
        )
        return str(chatwoot_id)

    def _after_export(self):
        """Guarantee chatwoot_id and sync_date are written to the binding.

        The base binder.bind() already does this write, but we repeat it here
        unconditionally via sudo() to rule out any permission or readonly-flag
        interference.
        """
        if self.external_id:
            self.binding.sudo().with_context(connector_no_export=True).write(
                {
                    "chatwoot_id": str(self.external_id),
                    "sync_date": fields.Datetime.now(),
                }
            )
            _logger.info(
                "_after_export: wrote chatwoot_id=%s to binding id=%s",
                self.external_id,
                self.binding.id,
            )

    def _update(self, data):
        """Update the existing Chatwoot contact."""
        self.backend_adapter.write(self.external_id, data)
        _logger.debug(
            "Updated Chatwoot contact id=%s for partner '%s'",
            self.external_id,
            self.binding.odoo_id.display_name,
        )

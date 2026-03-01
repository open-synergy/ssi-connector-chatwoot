# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Event Listener: res.partner → Chatwoot
=========================================

Listens to ``on_record_create`` and ``on_record_write`` events on
``res.partner`` records.  When a partner that has ``sync_to_chatwoot = True``
is created or relevant fields are modified, an asynchronous export job is
queued for every active Chatwoot backend.

The ``connector_no_export`` context key is honoured to prevent re-entrant
export loops (e.g. when the binder writes back the external ID).
"""

import logging

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if

_logger = logging.getLogger(__name__)

# Fields on res.partner that, when changed, should trigger an export.
PARTNER_EXPORT_FIELDS = {
    "name",
    "email",
    "phone",
    "mobile",
    "company_name",
    "parent_id",
    "sync_to_chatwoot",
}


def _no_connector_export(self, record, *args, **kwargs):
    return self.env.context.get("connector_no_export") or self.env.context.get(
        "no_connector_export"
    )


class ChatwootResPartnerListener(Component):
    """Trigger Chatwoot export on partner create / write."""

    _name = "chatwoot.res.partner.listener"
    _inherit = "base.connector.listener"
    _apply_on = ["res.partner"]

    # ------------------------------------------------------------------ #
    #  Helpers                                                            #
    # ------------------------------------------------------------------ #

    def _get_or_create_binding(self, partner, backend):
        """Return (or create) the binding for partner + backend."""
        binding_model = self.env["chatwoot.res.partner"]
        binding = binding_model.with_context(active_test=False).search(
            [("odoo_id", "=", partner.id), ("backend_id", "=", backend.id)],
            limit=1,
        )
        if not binding:
            binding = binding_model.create(
                {"odoo_id": partner.id, "backend_id": backend.id}
            )
        return binding

    def _schedule_export(self, partner, fields=None):
        """Queue an export job for every active backend."""
        if not partner.sync_to_chatwoot:
            _logger.debug(
                "_schedule_export: partner id=%s has sync_to_chatwoot=False, skipped.",
                partner.id,
            )
            return
        backends = self.env["chatwoot.backend"].search([("active", "=", True)])
        if not backends:
            _logger.warning("_schedule_export: no active Chatwoot backend found.")
            return
        for backend in backends:
            binding = self._get_or_create_binding(partner, backend)
            _logger.info(
                "_schedule_export: queuing export job for binding id=%s "
                "(partner id=%s, backend '%s', fields=%s)",
                binding.id,
                partner.id,
                backend.name,
                fields,
            )
            binding.with_delay().export_record(fields=fields)

    # ------------------------------------------------------------------ #
    #  Events                                                             #
    # ------------------------------------------------------------------ #

    @skip_if(lambda self, record, **kwargs: _no_connector_export(self, record))
    def on_record_create(self, record, fields=None):
        """Export newly created partners that are flagged for sync."""
        _logger.debug(
            "on_record_create fired for partner id=%s name='%s' sync=%s",
            record.id,
            record.name,
            record.sync_to_chatwoot,
        )
        self._schedule_export(record, fields=fields)

    @skip_if(lambda self, record, **kwargs: _no_connector_export(self, record))
    def on_record_write(self, record, fields=None):
        """Export partners when relevant fields are changed."""
        _logger.debug(
            "on_record_write fired for partner id=%s fields=%s sync=%s",
            record.id,
            fields,
            record.sync_to_chatwoot,
        )
        fields = fields or set()
        changed = PARTNER_EXPORT_FIELDS & set(fields)
        if not changed:
            _logger.debug(
                "on_record_write skipped: no relevant fields changed "
                "(changed=%s, monitored=%s)",
                set(fields),
                PARTNER_EXPORT_FIELDS,
            )
            return
        _logger.info(
            "on_record_write: scheduling Chatwoot export for partner id=%s "
            "because fields %s changed",
            record.id,
            changed,
        )
        self._schedule_export(record, fields=list(changed))

    def on_record_unlink(self, record):
        """Queue deletion of corresponding Chatwoot contact(s) before unlink.

        The ``chatwoot_id`` values are read NOW (while the binding records
        still exist) and passed as plain arguments to a queue job on
        ``chatwoot.backend``.  By the time the job runs, the Odoo binding
        will already be gone (cascade-deleted with the partner), but the
        job only needs the backend record and the plain Chatwoot ID string.
        """
        if not record.sync_to_chatwoot:
            return

        bindings = record.chatwoot_bind_ids.filtered(lambda b: b.chatwoot_id)
        if not bindings:
            return

        for binding in bindings:
            chatwoot_id = binding.chatwoot_id
            backend = binding.backend_id
            _logger.info(
                "on_record_unlink: queuing deletion of Chatwoot contact id=%s "
                "for partner '%s' (backend '%s')",
                chatwoot_id,
                record.display_name,
                backend.name,
            )
            backend.with_delay().delete_contact(chatwoot_id)

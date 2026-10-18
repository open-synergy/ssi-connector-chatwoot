# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Chatwoot Inbox Components
=========================

Adapter, binder and batch importer of the ``chatwoot.inbox`` binding.
"""

import logging

from odoo import fields

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ChatwootInboxAdapter(Component):
    """Adapter for the Chatwoot inboxes API."""

    _name = "chatwoot.inbox.adapter"
    _inherit = "chatwoot.backend.adapter"
    _apply_on = ["chatwoot.inbox"]
    _usage = "backend.adapter"

    def search(self):
        """List the inboxes of the Chatwoot account.

        Calls ``GET /api/v1/accounts/{id}/inboxes``.

        :return: list of inbox dicts
        :rtype: list
        """
        response = self._request("get", "inboxes")
        return response.get("payload", [])


class ChatwootInboxBinder(Component):
    """Binder for chatwoot.inbox."""

    _name = "chatwoot.inbox.binder"
    _inherit = "chatwoot.binder"
    _apply_on = ["chatwoot.inbox"]


class ChatwootInboxBatchImporter(Component):
    """Create or update every inbox of the Chatwoot account."""

    _name = "chatwoot.inbox.batch.importer"
    _inherit = "base.importer"
    _apply_on = ["chatwoot.inbox"]
    _collection = "chatwoot.backend"
    _usage = "batch.importer"

    def run(self):
        """Import all inboxes returned by the adapter.

        Existing inboxes get their name and channel type refreshed;
        ``allow_outgoing`` is never touched. Inboxes missing from the
        response are left alone.

        :return: the imported ``chatwoot.inbox`` recordset
        """
        binder = self.component(usage="binder")
        result = self.model.browse()
        for data in self.backend_adapter.search():
            vals = {
                "name": data.get("name") or str(data.get("id")),
                "channel_type": data.get("channel_type"),
                "sync_date": fields.Datetime.now(),
            }
            binding = binder.to_internal(data["id"])
            if binding:
                binding.write(vals)
            else:
                vals.update(
                    {
                        "backend_id": self.backend_record.id,
                        "chatwoot_id": str(data["id"]),
                    }
                )
                binding = self.model.create(vals)
            result |= binding
        _logger.info(
            "Imported %s inbox(es) from backend '%s'",
            len(result),
            self.backend_record.name,
        )
        return result

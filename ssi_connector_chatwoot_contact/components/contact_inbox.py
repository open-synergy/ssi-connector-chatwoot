# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Chatwoot Contact Inbox Components
=================================

Adapter, binder, export mapper and exporter of the
``chatwoot.contact.inbox`` binding.
"""

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ChatwootContactInboxAdapter(Component):
    """Adapter for the Chatwoot contact inboxes API."""

    _name = "chatwoot.contact.inbox.adapter"
    _inherit = "chatwoot.backend.adapter"
    _apply_on = ["chatwoot.contact.inbox"]
    _usage = "backend.adapter"

    # pylint: disable=W8106
    def create(self, contact_id, data):
        """Pair a contact with an inbox in Chatwoot.

        Calls ``POST /api/v1/accounts/{id}/contacts/{cid}/contact_inboxes``.

        :param contact_id: Chatwoot contact numeric ID
        :param data: dict with the ``inbox_id`` of Chatwoot
        :return: response dict (contains ``source_id``)
        :rtype: dict
        """
        return self._request(
            "post", "contacts/{}/contact_inboxes".format(contact_id), json=data
        )


class ChatwootContactInboxBinder(Component):
    """Binder for chatwoot.contact.inbox."""

    _name = "chatwoot.contact.inbox.binder"
    _inherit = "chatwoot.binder"
    _apply_on = ["chatwoot.contact.inbox"]


class ChatwootContactInboxExportMapper(Component):
    """Map a contact inbox binding to the Chatwoot payload."""

    _name = "chatwoot.contact.inbox.export.mapper"
    _inherit = "base.export.mapper"
    _apply_on = ["chatwoot.contact.inbox"]
    _collection = "chatwoot.backend"
    _usage = "export.mapper"

    @mapping
    def inbox_id(self, record):
        """Map the Chatwoot ID of the inbox.

        :param record: the ``chatwoot.contact.inbox`` binding
        :return: dict with the ``inbox_id`` key
        """
        return {"inbox_id": int(record.inbox_id.chatwoot_id)}


class ChatwootContactInboxExporter(Component):
    """Export a contact inbox binding to Chatwoot."""

    _name = "chatwoot.contact.inbox.exporter"
    _inherit = "generic.exporter"
    _apply_on = ["chatwoot.contact.inbox"]
    _collection = "chatwoot.backend"
    _usage = "exporter"

    _default_binding_field = "chatwoot_bind_ids"

    def run(self, binding, *args, **kwargs):
        """Export the binding unless it already has a source ID.

        :param binding: the ``chatwoot.contact.inbox`` binding
        :return: result message of the export
        """
        if binding.chatwoot_id:
            return _("Already exported.")
        return super().run(binding, *args, **kwargs)

    def _export_dependencies(self):
        """Export the contact first when it has no Chatwoot ID yet."""
        self._export_dependency(
            self.binding.partner_binding_id,
            "chatwoot.res.partner",
            component_usage="exporter",
        )

    def _create(self, data):
        """Create the contact inbox in Chatwoot and return its source ID.

        :param data: payload built by the export mapper
        :return: the ``source_id`` returned by Chatwoot
        :rtype: str
        """
        contact_id = self.binding.partner_binding_id.chatwoot_id
        result = self.backend_adapter.create(contact_id, data)
        source_id = result.get("source_id")
        if not source_id:
            raise ValueError(
                "Chatwoot returned no source ID for binding %s. "
                "Full response: %s" % (self.binding.id, result)
            )
        return str(source_id)

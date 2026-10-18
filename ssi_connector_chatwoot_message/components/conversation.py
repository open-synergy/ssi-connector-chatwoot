# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Chatwoot Conversation Components
================================

Adapter, binder, export mapper and exporter of the
``chatwoot.conversation`` binding.
"""

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ChatwootConversationAdapter(Component):
    """Adapter for the Chatwoot conversations API."""

    _name = "chatwoot.conversation.adapter"
    _inherit = "chatwoot.backend.adapter"
    _apply_on = ["chatwoot.conversation"]
    _usage = "backend.adapter"

    # pylint: disable=W8106
    def create(self, data):
        """Open a conversation in Chatwoot.

        Calls ``POST /api/v1/accounts/{id}/conversations``.

        :param data: dict with ``source_id``, ``inbox_id`` and
            ``contact_id``
        :return: response dict (contains the conversation ``id``)
        :rtype: dict
        """
        return self._request("post", "conversations", json=data)


class ChatwootConversationBinder(Component):
    """Binder for chatwoot.conversation."""

    _name = "chatwoot.conversation.binder"
    _inherit = "chatwoot.binder"
    _apply_on = ["chatwoot.conversation"]


class ChatwootConversationExportMapper(Component):
    """Map a conversation binding to the Chatwoot payload."""

    _name = "chatwoot.conversation.export.mapper"
    _inherit = "base.export.mapper"
    _apply_on = ["chatwoot.conversation"]
    _collection = "chatwoot.backend"
    _usage = "export.mapper"

    @mapping
    def source_id(self, record):
        """Map the source ID of the contact inbox.

        :param record: the ``chatwoot.conversation`` binding
        :return: dict with the ``source_id`` key
        """
        return {"source_id": record.contact_inbox_id.chatwoot_id}

    @mapping
    def inbox_id(self, record):
        """Map the Chatwoot ID of the inbox.

        :param record: the ``chatwoot.conversation`` binding
        :return: dict with the ``inbox_id`` key
        """
        return {"inbox_id": int(record.contact_inbox_id.inbox_id.chatwoot_id)}

    @mapping
    def contact_id(self, record):
        """Map the Chatwoot ID of the contact.

        :param record: the ``chatwoot.conversation`` binding
        :return: dict with the ``contact_id`` key
        """
        return {
            "contact_id": int(record.contact_inbox_id.partner_binding_id.chatwoot_id)
        }


class ChatwootConversationExporter(Component):
    """Export a conversation binding to Chatwoot."""

    _name = "chatwoot.conversation.exporter"
    _inherit = "generic.exporter"
    _apply_on = ["chatwoot.conversation"]
    _collection = "chatwoot.backend"
    _usage = "exporter"

    _default_binding_field = "chatwoot_bind_ids"

    def run(self, binding, *args, **kwargs):
        """Export the binding unless it already has a Chatwoot ID.

        :param binding: the ``chatwoot.conversation`` binding
        :return: result message of the export
        """
        if binding.chatwoot_id:
            return _("Already exported.")
        return super().run(binding, *args, **kwargs)

    def _export_dependencies(self):
        """Export the contact inbox first when it has no source ID yet."""
        self._export_dependency(
            self.binding.contact_inbox_id,
            "chatwoot.contact.inbox",
            component_usage="exporter",
        )

    def _create(self, data):
        """Create the conversation in Chatwoot and return its ID.

        :param data: payload built by the export mapper
        :return: the conversation ID returned by Chatwoot
        :rtype: str
        """
        result = self.backend_adapter.create(data)
        conversation_id = result.get("id")
        if not conversation_id:
            raise ValueError(
                "Chatwoot returned no conversation ID for binding %s. "
                "Full response: %s" % (self.binding.id, result)
            )
        return str(conversation_id)

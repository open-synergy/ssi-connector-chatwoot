# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Chatwoot Contact Adapter
========================

Implements CRUD operations against the Chatwoot Contacts REST API:

  POST   /api/v1/accounts/{id}/contacts          – create
  GET    /api/v1/accounts/{id}/contacts/{cid}    – read
  PUT    /api/v1/accounts/{id}/contacts/{cid}    – update
  DELETE /api/v1/accounts/{id}/contacts/{cid}    – delete
  GET    /api/v1/accounts/{id}/contacts/search   – search
"""

import requests

from odoo.addons.component.core import Component


class ChatwootContactAdapter(Component):
    """CRUD adapter for Chatwoot contacts."""

    _name = "chatwoot.res.partner.adapter"
    _inherit = "chatwoot.backend.adapter"
    _apply_on = ["chatwoot.res.partner"]
    _usage = "backend.adapter"

    # ------------------------------------------------------------------ #
    #  CRUD                                                               #
    # ------------------------------------------------------------------ #

    def search(self, query="", page=1):
        """Search contacts by name / email / phone.

        :param query: search string
        :param page:  page number (Chatwoot paginates at 15 items)
        :returns: list of contact dicts
        """
        response = self._request(
            "get",
            "contacts/search",
            params={"q": query, "page": page, "include_contacts": True},
        )
        return response.get("payload", [])

    # pylint: disable=W8106
    def read(self, external_id):
        """Fetch a single contact by its Chatwoot ID.

        :param external_id: Chatwoot contact numeric ID (str or int)
        :returns: contact dict
        """
        response = self._request("get", "contacts/{}".format(external_id))
        return response

    # pylint: disable=W8106
    def create(self, data):
        """Create a new contact in Chatwoot.

        :param data: dict with contact fields
        :returns: created contact dict (contains 'id')
        """
        response = self._request("post", "contacts", json=data)
        return response

    # pylint: disable=W8106
    def write(self, external_id, data):
        """Update an existing Chatwoot contact.

        :param external_id: Chatwoot contact numeric ID
        :param data: dict with fields to update
        :returns: updated contact dict
        """
        response = self._request("put", "contacts/{}".format(external_id), json=data)
        return response

    def delete(self, external_id):
        """Delete a Chatwoot contact.

        :param external_id: Chatwoot contact numeric ID

        A 404 response is silently ignored — the contact was already deleted
        on the Chatwoot side, which is the desired end-state.
        """
        try:
            self._request("delete", "contacts/{}".format(external_id))
        except requests.exceptions.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return True
            raise
        return True

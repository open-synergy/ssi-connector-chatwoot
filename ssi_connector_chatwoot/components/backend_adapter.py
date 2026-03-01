# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Chatwoot Backend Adapter
========================

Base adapter that wraps HTTP calls to the Chatwoot REST API.
Concrete adapters for specific resources (contacts, conversations, …) will
inherit from :class:`ChatwootCRUDAdapter`.
"""

import logging

import requests

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import NetworkRetryableError

_logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30  # seconds


class ChatwootBaseAdapter(AbstractComponent):
    """Base Chatwoot Adapter: holds helpers for HTTP calls."""

    _name = "chatwoot.backend.adapter"
    _inherit = "base.backend.adapter.crud"
    _collection = "chatwoot.backend"

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    @property
    def _base_url(self):
        backend = self.backend_record
        return "{}/api/v1/accounts/{}".format(
            backend.url.rstrip("/"),
            backend.account_id,
        )

    @property
    def _headers(self):
        return {
            "api_access_token": self.backend_record.api_token,
            "Content-Type": "application/json",
        }

    def _request(self, method, path, **kwargs):
        """Make an HTTP request to the Chatwoot API.

        :param method: HTTP method (get, post, put, patch, delete)
        :param path:   API path relative to the base accounts URL
        :raises NetworkRetryableError: on connection / timeout errors
        """
        url = "{}/{}".format(self._base_url, path.lstrip("/"))
        kwargs.setdefault("timeout", _DEFAULT_TIMEOUT)
        kwargs.setdefault("headers", self._headers)

        try:
            response = requests.request(method, url, **kwargs)
        except (requests.ConnectionError, requests.Timeout) as exc:
            raise NetworkRetryableError(
                "A network error occurred while trying to communicate with "
                "Chatwoot: %s" % exc
            ) from exc

        if not response.ok:
            try:
                body = response.json()
            except Exception:
                body = response.text
            raise requests.exceptions.HTTPError(
                "{} {} for url: {}\nResponse body: {}".format(
                    response.status_code,
                    response.reason,
                    response.url,
                    body,
                ),
                response=response,
            )
        if response.content:
            return response.json()
        return {}

    def test_connection(self):
        """Simple connectivity test: fetch account details."""
        return self._request("get", "")

    # ------------------------------------------------------------------ #
    #  CRUDAdapter stubs (override in sub-classes)                        #
    # ------------------------------------------------------------------ #

    # pylint: disable=W8106
    def search(self, *args, **kwargs):
        raise NotImplementedError

    # pylint: disable=W8106
    def read(self, external_id, *args, **kwargs):
        raise NotImplementedError

    # pylint: disable=W8106
    def search_read(self, *args, **kwargs):
        raise NotImplementedError

    # pylint: disable=W8106
    def create(self, data):
        raise NotImplementedError

    # pylint: disable=W8106
    def write(self, external_id, data):
        raise NotImplementedError

    # pylint: disable=W8106
    def delete(self, external_id):
        raise NotImplementedError

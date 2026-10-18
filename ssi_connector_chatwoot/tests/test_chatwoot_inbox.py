# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

import requests
from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged

from odoo.addons.queue_job.exception import RetryableJobError

REQUEST_PATH = (
    "odoo.addons.ssi_connector_chatwoot.components.backend_adapter.requests.request"
)


def _response(status_code, payload=None):
    """Build a fake ``requests`` response.

    :param status_code: HTTP status code of the response
    :param payload: JSON body of the response
    :return: a mock behaving like ``requests.Response``
    """
    body = payload if payload is not None else {}
    response = mock.Mock()
    response.status_code = status_code
    response.ok = status_code < 400
    response.reason = "reason"
    response.url = "https://chatwoot.example.com/api"
    response.content = b"{}"
    response.text = "{}"
    response.json.return_value = body
    return response


@tagged("post_install", "-at_install")
class TestChatwootInbox(YamlTransactionCase):
    """Scenario tests for the ``chatwoot.inbox`` model and its import."""

    def setUp(self):
        """Create the backend used by the Python tests."""
        super().setUp()
        self.backend = self.env["chatwoot.backend"].create(
            {
                "name": "Python Inbox Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 7,
                "api_token": "test-token",
            }
        )

    def _inboxes(self):
        """Return the inboxes of the test backend, archived included.

        :return: ``chatwoot.inbox`` recordset
        """
        return (
            self.env["chatwoot.inbox"]
            .with_context(active_test=False)
            .search([("backend_id", "=", self.backend.id)])
        )

    def test_chatwoot_inbox(self):
        """Run the create and duplicate scenarios of the inbox."""
        self.run_yaml_scenario("test_data_chatwoot_inbox.yaml")

    def test_import_inbox_idempotent(self):
        """Assert importing twice keeps two inboxes and ``allow_outgoing``.

        Pure Python - trigger P6 (L-15: ``requests.request`` is patched).
        """
        payload = {
            "payload": [
                {"id": 1, "name": "WhatsApp", "channel_type": "Channel::Api"},
                {"id": 2, "name": "Telegram", "channel_type": "Channel::Telegram"},
            ]
        }
        with mock.patch(REQUEST_PATH, return_value=_response(200, payload)) as patched:
            self.backend.import_inbox()
            self.assertEqual(len(self._inboxes()), 2)
            inbox = self._inboxes().filtered(lambda r: r.chatwoot_id == "1")
            inbox.write({"allow_outgoing": True})
            payload["payload"][0]["name"] = "WhatsApp Renamed"
            self.backend.import_inbox()
        self.assertEqual(len(self._inboxes()), 2)
        self.assertEqual(inbox.name, "WhatsApp Renamed")
        self.assertEqual(inbox.channel_type, "Channel::Api")
        self.assertTrue(inbox.allow_outgoing)
        self.assertTrue(inbox.sync_date)
        self.assertIn("/accounts/7/inboxes", patched.call_args[0][1])

    def test_action_import_inbox_queues_job(self):
        """Assert the button enqueues the import instead of running it.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        returned client action).
        """
        result = self.backend.action_import_inbox()
        self.assertEqual(result["tag"], "display_notification")
        job = self.env["queue.job"].search(
            [
                ("model_name", "=", "chatwoot.backend"),
                ("method_name", "=", "import_inbox"),
            ]
        )
        self.assertTrue(job)
        self.assertFalse(self._inboxes())

    def _request_status(self, status_code):
        """Issue a request whose fake response has the given status.

        :param status_code: HTTP status code returned by the fake response
        """
        with self.backend.work_on("chatwoot.inbox") as work:
            adapter = work.component(usage="backend.adapter")
            with mock.patch(REQUEST_PATH, return_value=_response(status_code)):
                adapter._request("get", "inboxes")

    def test_retryable_statuses(self):
        """Assert 429 and 5xx responses raise a retryable job error.

        Pure Python - trigger P5 (L-22: the exception is not an
        ``expect_error`` type) and P6 (L-15: ``requests.request`` is
        patched).
        """
        for status_code in (429, 500, 502, 503, 504):
            with self.assertRaises(RetryableJobError):
                self._request_status(status_code)

    def test_permanent_statuses(self):
        """Assert other 4xx responses stay permanent HTTP errors.

        Pure Python - trigger P5 (L-22: the exception is not an
        ``expect_error`` type) and P6 (L-15: ``requests.request`` is
        patched).
        """
        for status_code in (404, 422):
            with self.assertRaises(requests.exceptions.HTTPError):
                self._request_status(status_code)

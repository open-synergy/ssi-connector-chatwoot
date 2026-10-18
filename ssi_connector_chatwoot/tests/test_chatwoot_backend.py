# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

import requests
from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged

from odoo.addons.connector.exception import NetworkRetryableError

GET_PATH = "odoo.addons.ssi_connector_chatwoot.models.chatwoot_backend.requests.get"


@tagged("post_install", "-at_install")
class TestChatwootBackend(YamlTransactionCase):
    """Scenario tests for the ``chatwoot.backend`` model."""

    def setUp(self):
        """Create the backend used by the Python tests."""
        super().setUp()
        self.backend = self.env["chatwoot.backend"].create(
            {
                "name": "Python Test Backend",
                "url": "https://chatwoot.example.com/",
                "account_id": 12,
                "api_token": "test-token",
            }
        )

    def test_chatwoot_backend(self):
        """Run the create, edit and delete scenarios of the backend."""
        self.run_yaml_scenario("test_data_chatwoot_backend.yaml")

    def test_test_connection_success(self):
        """Assert a successful connection test returns a success notice.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        returned client action) and P6 (L-15: ``requests.get`` is patched).
        """
        response = mock.Mock()
        with mock.patch(GET_PATH, return_value=response) as patched:
            result = self.backend.action_test_connection()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")
        self.assertEqual(result["params"]["type"], "success")
        self.assertEqual(
            patched.call_args[0][0],
            "https://chatwoot.example.com/api/v1/accounts/12",
        )

    def test_test_connection_connection_error(self):
        """Assert a connection error is raised as a retryable error.

        Pure Python - trigger P5 (L-22: the exception is not an
        ``expect_error`` type) and P6 (L-15: ``requests.get`` is patched).
        """
        with mock.patch(GET_PATH, side_effect=requests.ConnectionError("down")):
            with self.assertRaises(NetworkRetryableError):
                self.backend.action_test_connection()

    def test_test_connection_timeout(self):
        """Assert a timeout is raised as a retryable error.

        Pure Python - trigger P5 (L-22: the exception is not an
        ``expect_error`` type) and P6 (L-15: ``requests.get`` is patched).
        """
        with mock.patch(GET_PATH, side_effect=requests.Timeout("slow")):
            with self.assertRaises(NetworkRetryableError):
                self.backend.action_test_connection()

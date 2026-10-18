# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged

REQUEST_PATH = (
    "odoo.addons.ssi_connector_chatwoot.components.backend_adapter.requests.request"
)


@tagged("post_install", "-at_install")
class TestChatwootContactInbox(YamlTransactionCase):
    """Scenario tests for ``chatwoot.contact.inbox``."""

    def setUp(self):
        """Create the backend, inbox, partner and binding fixtures."""
        super().setUp()
        self.backend = self.env["chatwoot.backend"].create(
            {
                "name": "Python CI Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "test-token",
            }
        )
        self.inbox = self.env["chatwoot.inbox"].create(
            {
                "name": "Python Inbox",
                "backend_id": self.backend.id,
                "chatwoot_id": "5",
                "allow_outgoing": True,
            }
        )
        self.partner = self.env["res.partner"].create(
            {"name": "Python CI Partner", "sync_to_chatwoot": False}
        )
        self.partner_binding = self.env["chatwoot.res.partner"].create(
            {"odoo_id": self.partner.id, "backend_id": self.backend.id}
        )
        self.binding = self.env["chatwoot.contact.inbox"].create(
            {
                "partner_binding_id": self.partner_binding.id,
                "inbox_id": self.inbox.id,
            }
        )

    @staticmethod
    def _response(payload):
        """Build a fake successful HTTP response.

        :param payload: the JSON body of the response
        :return: a mock response object
        """
        response = mock.Mock(ok=True, content=b"{}")
        response.json.return_value = payload
        return response

    def test_chatwoot_contact_inbox(self):
        """Run the create and constraint scenarios."""
        self.run_yaml_scenario("test_data_chatwoot_contact_inbox.yaml")

    def test_mapper_values(self):
        """Assert the export mapper sends the Chatwoot ID of the inbox.

        Pure Python - trigger P1 (L-01: mapper values are a return value
        that the ``call`` action discards).
        """
        with self.backend.work_on("chatwoot.contact.inbox") as work:
            mapper = work.component(usage="export.mapper")
            values = mapper.map_record(self.binding).values(for_create=True)
        self.assertEqual(values, {"inbox_id": 5})

    def test_export_exports_contact_first(self):
        """Assert the contact is exported before the contact inbox.

        Pure Python - trigger P6 (L-15: ``requests.request`` must be
        patched so that no network call is made).
        """
        responses = [
            self._response({"payload": {"contact": {"id": 7}}}),
            self._response({"source_id": "src-1"}),
        ]
        with mock.patch(REQUEST_PATH, side_effect=responses) as request:
            self.binding.export_record()
        self.assertEqual(request.call_count, 2)
        first, second = request.call_args_list
        self.assertEqual(first[0][0], "post")
        self.assertTrue(first[0][1].endswith("/contacts"))
        self.assertEqual(second[0][0], "post")
        self.assertTrue(second[0][1].endswith("/contacts/7/contact_inboxes"))
        self.assertEqual(second[1]["json"], {"inbox_id": 5})
        self.assertEqual(self.partner_binding.chatwoot_id, "7")
        self.assertEqual(self.binding.chatwoot_id, "src-1")
        self.assertTrue(self.binding.sync_date)

    def test_export_skips_exported_binding(self):
        """Assert an already exported binding does not call Chatwoot.

        Pure Python - trigger P6 (L-15: ``requests.request`` must be
        patched so that no network call is made).
        """
        self.binding.write({"chatwoot_id": "src-9"})
        with mock.patch(REQUEST_PATH) as request:
            self.binding.export_record()
        request.assert_not_called()
        self.assertEqual(self.binding.chatwoot_id, "src-9")

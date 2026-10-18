# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase, not HttpCase: HttpCase has no ``cls.env`` in 14.0.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiResPartner(HttpSavepointCase):
    """Tour tests for the ``res.partner`` Chatwoot work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the backend, the inbox and the partner used by the tour."""
        super().setUpClass()
        backend = cls.env["chatwoot.backend"].create(
            {
                "name": "TOUR Chatwoot Message Partner Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "tour-token",
            }
        )
        cls.env["chatwoot.inbox"].create(
            {
                "name": "TOUR Chatwoot Message Partner Inbox",
                "backend_id": backend.id,
                "chatwoot_id": "32",
                "allow_outgoing": True,
            }
        )
        cls.env["res.partner"].create({"name": "TOUR Chatwoot Notify Partner"})

    def test_set_chatwoot_notification(self):
        """Run the Notify via Chatwoot tour for partners.

        IK: docs/res_partner/01-set-chatwoot-notification.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_message_res_partner_set_chatwoot_notification",
            login="admin",
        )

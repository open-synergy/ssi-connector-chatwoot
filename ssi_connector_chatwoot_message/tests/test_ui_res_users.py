# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase, not HttpCase: HttpCase has no ``cls.env`` in 14.0.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiResUsers(HttpSavepointCase):
    """Tour tests for the ``res.users`` Chatwoot work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the backend and the inbox picked by the tour."""
        super().setUpClass()
        backend = cls.env["chatwoot.backend"].create(
            {
                "name": "TOUR Chatwoot Message Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "tour-token",
            }
        )
        cls.env["chatwoot.inbox"].create(
            {
                "name": "TOUR Chatwoot Message Inbox",
                "backend_id": backend.id,
                "chatwoot_id": "31",
                "allow_outgoing": True,
            }
        )

    def test_set_chatwoot_notification(self):
        """Run the Chatwoot notification preference tour for users.

        IK: docs/res_users/01-set-chatwoot-notification.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_message_res_users_set_chatwoot_notification",
            login="admin",
        )

# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase, not HttpCase: HttpCase has no ``cls.env`` in 14.0.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiMailComposeMessage(HttpSavepointCase):
    """Tour tests for the composer Chatwoot work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the inbox, the document and the recipient of the tour."""
        super().setUpClass()
        backend = cls.env["chatwoot.backend"].create(
            {
                "name": "TOUR Chatwoot Compose Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "tour-token",
            }
        )
        cls.env["chatwoot.inbox"].create(
            {
                "name": "TOUR Chatwoot Compose Inbox",
                "backend_id": backend.id,
                "chatwoot_id": "33",
                "allow_outgoing": True,
            }
        )
        cls.env["res.partner"].create(
            {
                "name": "TOUR Chatwoot Compose Document",
                "email": "compose.document@example.com",
            }
        )
        cls.env["res.partner"].create(
            {
                "name": "TOUR Chatwoot Compose Recipient",
                "email": "compose.recipient@example.com",
            }
        )

    def test_send_via_chatwoot(self):
        """Run the send via Chatwoot tour for the composer.

        IK: docs/mail_compose_message/01-send-via-chatwoot.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_message_mail_compose_message_send_via_chatwoot",
            login="admin",
        )

# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase, not HttpCase: HttpCase has no ``cls.env`` in 14.0.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiChatwootInbox(HttpSavepointCase):
    """Tour tests for the ``chatwoot.inbox`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the backend and the inbox used by the tours."""
        super().setUpClass()
        cls.env.ref("base.user_admin").write(
            {"groups_id": [(4, cls.env.ref("connector.group_connector_manager").id)]}
        )
        backend = cls.env["chatwoot.backend"].create(
            {
                "name": "TOUR Inbox Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "tour-token",
            }
        )
        cls.env["chatwoot.inbox"].create(
            {
                "name": "TOUR Inbox",
                "backend_id": backend.id,
                "chatwoot_id": "901",
            }
        )

    def test_edit(self):
        """Run the edit tour for ``chatwoot.inbox``.

        IK: docs/chatwoot_inbox/01-edit.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_chatwoot_inbox_edit",
            login="admin",
        )

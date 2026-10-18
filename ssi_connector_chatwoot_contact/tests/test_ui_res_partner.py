# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase, not HttpCase: HttpCase has no ``cls.env`` in 14.0.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiResPartner(HttpSavepointCase):
    """Tour tests for the ``res.partner`` Chatwoot work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the backend and the flagged partner used by the tours."""
        super().setUpClass()
        cls.env.ref("base.user_admin").write(
            {"groups_id": [(4, cls.env.ref("connector.group_connector_manager").id)]}
        )
        cls.env["chatwoot.backend"].create(
            {
                "name": "TOUR Chatwoot Partner Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "tour-token",
            }
        )
        cls.env["res.partner"].create(
            {"name": "TOUR Chatwoot Force Partner", "sync_to_chatwoot": True}
        )

    def test_create(self):
        """Run the create tour for ``res.partner``.

        IK: docs/res_partner/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_contact_res_partner_create",
            login="admin",
        )

    def test_force_export(self):
        """Run the force export tour for ``res.partner``.

        IK: docs/res_partner/02-force-export.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_contact_res_partner_force_export",
            login="admin",
        )

# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase, not HttpCase: HttpCase has no ``cls.env`` in 14.0.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiChatwootContactInbox(HttpSavepointCase):
    """Tour tests for the ``chatwoot.contact.inbox`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the backend, inbox, partners and bindings for the tours."""
        super().setUpClass()
        cls.env.ref("base.user_admin").write(
            {"groups_id": [(4, cls.env.ref("connector.group_connector_manager").id)]}
        )
        cls.backend = cls.env["chatwoot.backend"].create(
            {
                "name": "TOUR CI Chatwoot Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "tour-token",
            }
        )
        cls.inbox = cls.env["chatwoot.inbox"].create(
            {
                "name": "TOUR CI Inbox",
                "backend_id": cls.backend.id,
                "chatwoot_id": "5",
                "allow_outgoing": True,
            }
        )
        partner_model = cls.env["res.partner"]
        binding_model = cls.env["chatwoot.res.partner"]
        for kind in ("Create", "Export"):
            partner = partner_model.create({"name": "TOUR CI %s Partner" % kind})
            partner_binding = binding_model.create(
                {"odoo_id": partner.id, "backend_id": cls.backend.id}
            )
            if kind == "Export":
                cls.env["chatwoot.contact.inbox"].create(
                    {
                        "partner_binding_id": partner_binding.id,
                        "inbox_id": cls.inbox.id,
                    }
                )

    def test_create(self):
        """Run the create tour for ``chatwoot.contact.inbox``.

        IK: docs/chatwoot_contact_inbox/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_contact_chatwoot_contact_inbox_create",
            login="admin",
        )

    def test_export(self):
        """Run the export tour for ``chatwoot.contact.inbox``.

        IK: docs/chatwoot_contact_inbox/02-export.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_contact_chatwoot_contact_inbox_export",
            login="admin",
        )

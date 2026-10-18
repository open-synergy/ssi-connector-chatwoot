# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

# HttpSavepointCase, not HttpCase: HttpCase has no ``cls.env`` in 14.0.
from odoo.tests import HttpSavepointCase, tagged

REQUEST_PATH = (
    "odoo.addons.ssi_connector_chatwoot.components.backend_adapter.requests.request"
)


@tagged("post_install", "-at_install")
class TestUiChatwootResPartner(HttpSavepointCase):
    """Tour tests for the ``chatwoot.res.partner`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the backends, partners and bindings used by the tours."""
        super().setUpClass()
        cls.env.ref("base.user_admin").write(
            {"groups_id": [(4, cls.env.ref("connector.group_connector_manager").id)]}
        )
        backend_model = cls.env["chatwoot.backend"]
        cls.backend = backend_model.create(
            {
                "name": "TOUR Chatwoot Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "tour-token",
            }
        )
        cls.other_backend = backend_model.create(
            {
                "name": "TOUR Chatwoot Other Backend",
                "url": "https://chatwoot-other.example.com",
                "account_id": 2,
                "api_token": "tour-token-other",
            }
        )
        partner_model = cls.env["res.partner"]
        binding_model = cls.env["chatwoot.res.partner"]
        cls.create_partner = partner_model.create(
            {"name": "TOUR Binding Create Partner"}
        )
        for kind in ("Edit", "Delete", "Export"):
            partner = partner_model.create({"name": "TOUR Binding %s Partner" % kind})
            binding_model.create({"odoo_id": partner.id, "backend_id": cls.backend.id})

    def test_create(self):
        """Run the create tour for ``chatwoot.res.partner``.

        IK: docs/chatwoot_res_partner/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_contact_chatwoot_res_partner_create",
            login="admin",
        )

    def test_edit(self):
        """Run the edit tour for ``chatwoot.res.partner``.

        IK: docs/chatwoot_res_partner/02-edit.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_contact_chatwoot_res_partner_edit",
            login="admin",
        )

    def test_delete(self):
        """Run the delete tour for ``chatwoot.res.partner``.

        IK: docs/chatwoot_res_partner/03-delete.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_contact_chatwoot_res_partner_delete",
            login="admin",
        )

    def test_export(self):
        """Run the export tour with the Chatwoot HTTP call patched.

        The call to ``requests.request`` is mocked so that no network access
        happens; the mocked response carries the contact id ``7``.

        IK: docs/chatwoot_res_partner/04-export.md
        """
        response = mock.Mock(ok=True, content=b"{}")
        response.json.return_value = {"payload": {"contact": {"id": 7}}}
        with mock.patch(REQUEST_PATH, return_value=response):
            self.start_tour(
                "/web",
                "ssi_connector_chatwoot_contact_chatwoot_res_partner_export",
                login="admin",
            )

# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

# HttpSavepointCase, not HttpCase: HttpCase has no ``cls.env`` in 14.0.
from odoo.tests import HttpSavepointCase, tagged

GET_PATH = "odoo.addons.ssi_connector_chatwoot.models.chatwoot_backend.requests.get"


@tagged("post_install", "-at_install")
class TestUiChatwootBackend(HttpSavepointCase):
    """Tour tests for the ``chatwoot.backend`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the backends used by the tours."""
        super().setUpClass()
        cls.env.ref("base.user_admin").write(
            {"groups_id": [(4, cls.env.ref("connector.group_connector_manager").id)]}
        )
        backend_model = cls.env["chatwoot.backend"]
        for kind in ("Edit", "Delete", "Test", "Import"):
            backend_model.create(
                {
                    "name": "TOUR %s Backend" % kind,
                    "url": "https://chatwoot.example.com",
                    "account_id": 1,
                    "api_token": "tour-token",
                }
            )

    def test_create(self):
        """Run the create tour for ``chatwoot.backend``.

        IK: docs/chatwoot_backend/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_chatwoot_backend_create",
            login="admin",
        )

    def test_edit(self):
        """Run the edit tour for ``chatwoot.backend``.

        IK: docs/chatwoot_backend/02-edit.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_chatwoot_backend_edit",
            login="admin",
        )

    def test_delete(self):
        """Run the delete tour for ``chatwoot.backend``.

        IK: docs/chatwoot_backend/03-delete.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_chatwoot_backend_delete",
            login="admin",
        )

    def test_test_connection(self):
        """Run the test connection tour with ``requests.get`` patched.

        The call is mocked so that no network access happens.

        IK: docs/chatwoot_backend/04-test-connection.md
        """
        with mock.patch(GET_PATH, return_value=mock.Mock()):
            self.start_tour(
                "/web",
                "ssi_connector_chatwoot_chatwoot_backend_test_connection",
                login="admin",
            )

    def test_import_inbox(self):
        """Run the import inboxes tour for ``chatwoot.backend``.

        The import is only queued, so no network access happens.

        IK: docs/chatwoot_backend/05-import-inbox.md
        """
        self.start_tour(
            "/web",
            "ssi_connector_chatwoot_chatwoot_backend_import_inbox",
            login="admin",
        )

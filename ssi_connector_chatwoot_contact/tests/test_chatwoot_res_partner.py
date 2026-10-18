# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import importlib.util
import os
from unittest import mock

from odoo_yaml_test import YamlTransactionCase

from odoo.modules.module import get_module_path
from odoo.tests import tagged

MODULE = "ssi_connector_chatwoot_contact"
CONSTRAINT = "chatwoot_res_partner_chatwoot_partner_uniq"
CONSTRAINT_XMLID_NAME = "constraint_" + CONSTRAINT
REQUEST_PATH = (
    "odoo.addons.ssi_connector_chatwoot.components.backend_adapter.requests.request"
)


@tagged("post_install", "-at_install")
class TestChatwootResPartner(YamlTransactionCase):
    """Scenario tests for ``chatwoot.res.partner`` and its partner hooks."""

    def setUp(self):
        """Create the backend and partner fixtures for the Python tests."""
        super().setUp()
        self.backend = self.env["chatwoot.backend"].create(
            {
                "name": "Python Test Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "test-token",
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "Python Partner",
                "mobile": "+62 812-3456-7890",
                "email": "python@example.com",
                "sync_to_chatwoot": False,
            }
        )
        self.binding = self.env["chatwoot.res.partner"].create(
            {"odoo_id": self.partner.id, "backend_id": self.backend.id}
        )

    def _mapped_values(self, binding, for_create=True):
        """Return the export mapper values for a binding.

        :param binding: the ``chatwoot.res.partner`` record
        :param for_create: whether to map as for a creation
        :return: dict of values sent to Chatwoot
        """
        with self.backend.work_on("chatwoot.res.partner") as work:
            mapper = work.component(usage="export.mapper")
            return mapper.map_record(binding).values(for_create=for_create)

    def test_chatwoot_res_partner(self):
        """Run the binding, listener and partner scenarios."""
        self.run_yaml_scenario("test_data_chatwoot_res_partner.yaml")

    def test_legacy_sql_constraint_absent(self):
        """Assert the legacy unique constraint is absent from PostgreSQL.

        Pure Python - trigger P1 (L-01: the ``call`` action discards return
        values, and raw SQL result rows are never reachable from YAML).
        """
        self.env.cr.execute(
            "SELECT conname FROM pg_constraint WHERE conname = %s", (CONSTRAINT,)
        )
        self.assertEqual(self.env.cr.fetchall(), [])

    def test_migration_drops_legacy_constraint(self):
        """Assert the pre-migration drops the constraint and its XML ID.

        Pure Python - trigger P10 (L-11: the script must be imported from
        its file, which ``EVAL:`` cannot do) and P1 (L-01: SQL rows).
        """
        cr = self.env.cr
        cr.execute(
            "ALTER TABLE chatwoot_res_partner ADD CONSTRAINT %s "
            "UNIQUE (backend_id, odoo_id)" % CONSTRAINT
        )
        constraint = self.env["ir.model.constraint"].create(
            {
                "name": CONSTRAINT,
                "model": self.env["ir.model"]._get("chatwoot.res.partner").id,
                "module": self.env["ir.module.module"]
                .search([("name", "=", MODULE)])
                .id,
                "type": "u",
            }
        )
        self.env["ir.model.data"].create(
            {
                "module": MODULE,
                "name": CONSTRAINT_XMLID_NAME,
                "model": "ir.model.constraint",
                "res_id": constraint.id,
            }
        )
        path = os.path.join(
            get_module_path(MODULE), "migrations", "14.0.2.0.1", "pre-migrate.py"
        )
        spec = importlib.util.spec_from_file_location("pre_migrate_2_0_1", path)
        script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script)
        for _run in range(2):
            script.migrate(cr, "14.0.2.0.0")
            cr.execute(
                "SELECT conname FROM pg_constraint WHERE conname = %s",
                (CONSTRAINT,),
            )
            self.assertEqual(cr.fetchall(), [])
            cr.execute(
                "SELECT id FROM ir_model_data WHERE module = %s AND name = %s",
                (MODULE, CONSTRAINT_XMLID_NAME),
            )
            self.assertEqual(cr.fetchall(), [])

    def test_mapper_values(self):
        """Assert the export mapper builds the Chatwoot payload.

        Pure Python - trigger P1 (L-01: mapper values are a return value
        that the ``call`` action discards).
        """
        values = self._mapped_values(self.binding)
        self.assertEqual(values["name"], "Python Partner")
        self.assertEqual(values["phone_number"], "+6281234567890")
        self.assertEqual(values["email"], "python@example.com")
        self.assertEqual(values["additional_attributes"]["odoo_id"], self.partner.id)

    def test_mapper_omits_invalid_phone_and_empty_email(self):
        """Assert phone without ``+`` and empty email are left out.

        Pure Python - trigger P1 (L-01: mapper values are a return value
        that the ``call`` action discards).
        """
        self.partner.write({"mobile": "0812-3456-7890", "email": False})
        values = self._mapped_values(self.binding)
        self.assertNotIn("phone_number", values)
        self.assertNotIn("email", values)

    def test_export_record_stores_chatwoot_id(self):
        """Assert ``export_record`` stores the id returned by Chatwoot.

        Pure Python - trigger P6 (L-15: ``requests.request`` must be
        patched so that no network call is made).
        """
        response = mock.Mock(ok=True, content=b"{}")
        response.json.return_value = {"payload": {"contact": {"id": 7}}}
        with mock.patch(REQUEST_PATH, return_value=response) as request:
            self.binding.export_record()
        self.assertEqual(request.call_count, 1)
        self.assertEqual(request.call_args[0][0], "post")
        self.assertEqual(self.binding.chatwoot_id, "7")
        self.assertTrue(self.binding.sync_date)

    def test_delete_contact_calls_chatwoot(self):
        """Assert ``delete_contact`` issues a DELETE for the contact id.

        Pure Python - trigger P6 (L-15: ``requests.request`` must be
        patched so that no network call is made).
        """
        response = mock.Mock(ok=True, content=b"")
        with mock.patch(REQUEST_PATH, return_value=response) as request:
            self.backend.delete_contact("7")
        self.assertEqual(request.call_count, 1)
        self.assertEqual(request.call_args[0][0], "delete")
        self.assertTrue(request.call_args[0][1].endswith("/contacts/7"))

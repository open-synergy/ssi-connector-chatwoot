# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestResPartner(YamlTransactionCase):
    """Scenario tests for the Chatwoot preference of ``res.partner``."""

    def test_res_partner(self):
        """Run the Notify via Chatwoot scenarios."""
        self.run_yaml_scenario("test_data_res_partner.yaml")

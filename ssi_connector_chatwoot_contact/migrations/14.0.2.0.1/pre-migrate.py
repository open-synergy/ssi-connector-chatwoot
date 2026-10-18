# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Migration: 14.0.2.0.0 -> 14.0.2.0.1
#
# Changes: the SQL constraint ``chatwoot_partner_uniq`` on
#          ``chatwoot_res_partner`` was replaced by an ``@api.constrains``
#          check. Odoo does not drop a constraint that disappears from
#          ``_sql_constraints`` on upgrade, so it is dropped here.

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Drop the legacy unique constraint on the binding table.

    The call also removes the matching ``ir.model.constraint`` record and
    XML ID, and is idempotent (``DROP CONSTRAINT IF EXISTS``).

    :param env: the migration environment
    :param version: the version being migrated from (unused)
    :return: nothing; drops ``chatwoot_res_partner_chatwoot_partner_uniq``
    """
    openupgrade.delete_sql_constraint_safely(
        env,
        "ssi_connector_chatwoot_contact",
        "chatwoot_res_partner",
        "chatwoot_partner_uniq",
    )

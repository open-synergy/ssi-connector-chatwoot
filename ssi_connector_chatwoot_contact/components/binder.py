# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Binder: chatwoot.res.partner
============================

Resolves Odoo <-> Chatwoot ID pairs for the partner binding model.
"""

from odoo.addons.component.core import Component


class ChatwootResPartnerBinder(Component):
    """Binder for chatwoot.res.partner."""

    _name = "chatwoot.res.partner.binder"
    _inherit = "chatwoot.binder"
    _apply_on = ["chatwoot.res.partner"]

# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Chatwoot Binder
===============

Base binder for all Chatwoot binding models.  Concrete binders
(e.g. for res.partner) should inherit this class and set ``_model_name``.
"""

from odoo.addons.component.core import AbstractComponent


class ChatwootBinder(AbstractComponent):
    """Base binder for Chatwoot connector."""

    _name = "chatwoot.binder"
    _inherit = "base.binder"
    _collection = "chatwoot.backend"

    _external_field = "chatwoot_id"
    _backend_field = "backend_id"
    _odoo_field = "odoo_id"
    _sync_date_field = "sync_date"

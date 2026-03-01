# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Export Mapper: res.partner -> Chatwoot contact
===============================================

Converts the Odoo partner fields into the JSON payload expected by the
Chatwoot Contacts API::

    {
        "name":         "José Lopes",
        "email":        "jose@example.com",
        "phone_number": "+5511999990000",   # E.164 required by Chatwoot
        "identifier":   "odoo-42",          # stable Odoo-side identifier
        "additional_attributes": {
            "odoo_id": 42
        }
    }

Chatwoot requires phone_number in E.164 format (+<country_code><number>,
digits only after the +, 7-15 digits total).  Numbers that cannot be
normalised to E.164 are silently omitted to avoid 422 errors.
"""

import logging
import re

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping, only_create

_logger = logging.getLogger(__name__)

# E.164: optional leading +, then digits only (spaces/dashes/parens stripped)
_E164_RE = re.compile(r"^\+\d{7,15}$")


def _to_e164(phone):
    """Attempt to normalise *phone* to E.164 format.

    Steps:
    1. Strip whitespace, dashes, dots, parentheses.
    2. If the result matches ``+DIGITS``, return it unchanged.
    3. Otherwise return ``None`` (caller will skip the field).
    """
    if not phone:
        return None
    # Remove common formatting characters
    cleaned = re.sub(r"[\s\-\.\(\)]", "", phone)
    if _E164_RE.match(cleaned):
        return cleaned
    return None


class ChatwootResPartnerExportMapper(Component):
    """Map a res.partner (wrapped as chatwoot.res.partner) to a Chatwoot contact."""

    _name = "chatwoot.res.partner.export.mapper"
    _inherit = "base.export.mapper"
    _apply_on = ["chatwoot.res.partner"]
    _collection = "chatwoot.backend"
    _usage = "export.mapper"

    @mapping
    def name(self, record):
        return {"name": record.name or ""}

    @changed_by("email")
    @mapping
    def email(self, record):
        # Omit the field entirely when empty — Chatwoot rejects empty strings
        if record.email:
            return {"email": record.email}
        return {}

    @changed_by("mobile", "phone")
    @mapping
    def phone_number(self, record):
        """Send phone_number only when it is valid E.164.

        Chatwoot rejects phone numbers that are not in E.164 format with a
        422 error.  Numbers stored in Odoo without a country code prefix are
        skipped with a warning rather than causing the whole export to fail.
        """
        raw = record.mobile or record.phone or ""
        if not raw:
            return {}
        e164 = _to_e164(raw)
        if e164:
            return {"phone_number": e164}
        _logger.warning(
            "Partner '%s' (id=%s): phone '%s' is not in E.164 format "
            "(expected +<country_code><number>). "
            "The phone_number field will be omitted from the Chatwoot export.",
            record.odoo_id.display_name,
            record.odoo_id.id,
            raw,
        )
        return {}

    @mapping
    @only_create
    def identifier(self, record):
        """Set a stable identifier so we can find the contact later."""
        return {"identifier": "odoo-{}".format(record.odoo_id.id)}

    @mapping
    def additional_attributes(self, record):
        return {
            "additional_attributes": {
                "odoo_id": record.odoo_id.id,
                "company": record.company_name
                or (record.parent_id.name if record.parent_id else ""),
            }
        }

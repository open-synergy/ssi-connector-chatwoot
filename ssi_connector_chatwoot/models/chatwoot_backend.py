# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

import requests

from odoo import fields, models

from odoo.addons.connector.exception import NetworkRetryableError

_logger = logging.getLogger(__name__)


class ChatwootBackend(models.Model):
    """Chatwoot Backend - stores connection parameters to a Chatwoot instance."""

    _name = "chatwoot.backend"
    _inherit = "connector.backend"
    _description = "Chatwoot Backend"

    name = fields.Char(string="Name", required=True)
    url = fields.Char(
        string="URL",
        required=True,
        help="Chatwoot instance URL, e.g. https://app.chatwoot.com",
    )
    account_id = fields.Integer(
        string="Account ID",
        required=True,
        help="Chatwoot account numeric ID",
    )
    api_token = fields.Char(
        string="API Token (User)",
        required=True,
        help="User access token from Chatwoot profile settings",
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    def action_test_connection(self):
        """Test the connection to the Chatwoot API."""
        self.ensure_one()
        url = "{}/api/v1/accounts/{}".format(self.url.rstrip("/"), self.account_id)
        headers = {
            "api_access_token": self.api_token,
            "Content-Type": "application/json",
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except (requests.ConnectionError, requests.Timeout) as exc:
            raise NetworkRetryableError(
                "Could not connect to Chatwoot: %s" % exc
            ) from exc

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Connection Test",
                "message": "Successfully connected to Chatwoot!",
                "type": "success",
                "sticky": False,
            },
        }

    def delete_contact(self, chatwoot_id):
        """Delete a contact from Chatwoot by its external ID.

        Designed to be called via ``with_delay()`` so that the deletion is
        processed asynchronously through the queue job runner.  The
        ``chatwoot_id`` is passed as a plain value so this method remains
        functional even after the Odoo binding record has been deleted.

        :param chatwoot_id: Chatwoot contact ID (str or int)
        """
        self.ensure_one()
        with self.work_on("chatwoot.res.partner") as work:
            adapter = work.component(usage="backend.adapter")
            adapter.delete(str(chatwoot_id))
        _logger.info(
            "Deleted Chatwoot contact id=%s via backend '%s'",
            chatwoot_id,
            self.name,
        )

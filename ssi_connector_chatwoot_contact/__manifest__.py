# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Chatwoot Connector - Contact",
    "version": "14.0.2.0.2",
    "category": "Connector",
    "author": "PT. Simetri Sinergi Indonesia",
    "website": "https://simetri-sinergi.id",
    "license": "AGPL-3",
    "depends": [
        "ssi_connector_chatwoot",
        "ssi_partner",
        "queue_job",
        "web_tour",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/chatwoot_res_partner_views.xml",
        "views/res_partner_views.xml",
        "views/assets.xml",
    ],
    "installable": True,
}

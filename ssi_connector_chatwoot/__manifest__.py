# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Chatwoot Connector",
    "version": "14.0.2.1.0",
    "category": "Connector",
    "author": "PT. Simetri Sinergi Indonesia",
    "website": "https://simetri-sinergi.id",
    "license": "AGPL-3",
    "depends": [
        "connector",
        "queue_job",
        "ssi_connector",
        "web_tour",
    ],
    "data": [
        "security/ir.model.access.csv",
        "menu.xml",
        "views/chatwoot_backend_views.xml",
        "views/chatwoot_inbox_views.xml",
        "views/assets.xml",
    ],
    "installable": True,
}

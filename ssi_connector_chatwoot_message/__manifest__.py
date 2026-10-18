# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Chatwoot Connector - Message",
    "version": "14.0.1.0.0",
    "category": "Connector",
    "author": "PT. Simetri Sinergi Indonesia",
    "website": "https://simetri-sinergi.id",
    "license": "AGPL-3",
    "depends": [
        "ssi_connector_chatwoot_contact",
        "mail",
        "queue_job",
        "web_tour",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/queue_job_channel_data.xml",
        "views/res_users_views.xml",
        "views/res_partner_views.xml",
        "views/assets.xml",
    ],
    "installable": True,
}

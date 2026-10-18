# Export Chatwoot Contact Binding

> **Module:** `ssi_connector_chatwoot_contact`\
> **Model:** `chatwoot.res.partner`\
> **Menu:** Connector > Chatwoot > Bindings > Contacts\
> **Actor:** user in group _Connector Manager_\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** A binding exists.
- **Data:** The Chatwoot backend of the binding is reachable with a valid API token.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Chatwoot > Bindings > Contacts** menu.
2. Find and open the binding to export.
3. Click the **Export to Chatwoot** button in the header.

## Post-Condition

- The partner is pushed to Chatwoot: **Chatwoot Contact ID** is filled with the id
  returned by Chatwoot and **Last Synchronization** is set.

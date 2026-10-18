# Edit Chatwoot Contact Binding

> **Module:** `ssi_connector_chatwoot_contact`\
> **Model:** `chatwoot.res.partner`\
> **Menu:** Connector > Chatwoot > Bindings > Contacts\
> **Actor:** user in group _Connector Manager_\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** A binding exists.
- **Data:** The Chatwoot backend to switch to exists and is active.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Chatwoot > Bindings > Contacts** menu.
2. Find and open the binding to edit.
3. Click the **Edit** button.
4. Change **Chatwoot Backend**. The new backend must not already have a binding for the
   same partner.
5. Click **Save**.

## Post-Condition

- The binding is updated with the new backend.

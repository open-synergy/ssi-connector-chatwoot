# Delete Chatwoot Contact Binding

> **Module:** `ssi_connector_chatwoot_contact`\
> **Model:** `chatwoot.res.partner`\
> **Menu:** Connector > Chatwoot > Bindings > Contacts\
> **Actor:** user in group _Connector Manager_\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** A binding exists.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Chatwoot > Bindings > Contacts** menu.
2. Find and open the binding to delete.
3. Click **Action** > **Delete**.
4. Click **OK** to confirm.

## Post-Condition

- The binding is permanently removed. The partner itself and the contact already created
  in Chatwoot are not deleted.

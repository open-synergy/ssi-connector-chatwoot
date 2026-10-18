# Delete Chatwoot Backend

> **Module:** `ssi_connector_chatwoot`\
> **Model:** `chatwoot.backend`\
> **Menu:** Connector > Configuration > Chatwoot > Backends\
> **Actor:** user in group _Connector Manager_\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** A Chatwoot backend exists and has no binding.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Configuration > Chatwoot > Backends** menu.
2. Find and open the backend to delete.
3. Click **Action** > **Delete**.
4. Click **OK** to confirm.

## Post-Condition

- The backend is permanently removed. Contacts already created in Chatwoot are not
  deleted.

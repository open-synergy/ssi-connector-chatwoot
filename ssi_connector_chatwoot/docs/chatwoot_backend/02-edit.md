# Edit Chatwoot Backend

> **Module:** `ssi_connector_chatwoot`\
> **Model:** `chatwoot.backend`\
> **Menu:** Connector > Configuration > Chatwoot > Backends\
> **Actor:** user in group _Connector Manager_\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** A Chatwoot backend exists.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Configuration > Chatwoot > Backends** menu.
2. Find and open the backend to edit.
3. Click the **Edit** button.
4. Change the fields as needed, for example **Name** or **URL**. Untick **Active** to
   archive the backend.
5. Click **Save**.

## Post-Condition

- The backend is updated with the new values.
- An archived backend (**Active** unticked) is hidden from the default list and shows
  the **Archived** ribbon when opened.

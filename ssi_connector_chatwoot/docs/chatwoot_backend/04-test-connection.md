# Test Connection of Chatwoot Backend

> **Module:** `ssi_connector_chatwoot`\
> **Model:** `chatwoot.backend`\
> **Menu:** Connector > Configuration > Chatwoot > Backends\
> **Actor:** user in group _Connector Manager_\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** A Chatwoot backend exists.
- **Data:** The Chatwoot instance of the backend is reachable with a valid API token.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Configuration > Chatwoot > Backends** menu.
2. Find and open the backend to test.
3. Click the **Test Connection** button in the header.

## Post-Condition

- A **Connection Test** notification is displayed with the message _Successfully
  connected to Chatwoot!_.
- When the instance cannot be reached, an error is raised instead and no notification is
  displayed.

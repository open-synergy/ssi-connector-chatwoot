# Create Chatwoot Backend

> **Module:** `ssi_connector_chatwoot`\
> **Model:** `chatwoot.backend`\
> **Menu:** Connector > Configuration > Chatwoot > Backends\
> **Actor:** user in group _Connector Manager_

## Pre-Condition

- **Data:** The URL, the account id and a user access token of the Chatwoot instance are
  known.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Configuration > Chatwoot > Backends** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the fields:
   - **Name** _(required)_: Enter a name for the backend.
   - **URL** _(required)_: Enter the Chatwoot instance URL, e.g.
     `https://app.chatwoot.com`.
   - **Account ID** _(required)_: Enter the numeric Chatwoot account id.
   - **API Token (User)** _(required)_: Enter the user access token from the Chatwoot
     profile settings.
4. Click **Save**.

## Post-Condition

- A new Chatwoot backend is created, active, and owned by the current company.
- The backend is shown in the **Backends** list.

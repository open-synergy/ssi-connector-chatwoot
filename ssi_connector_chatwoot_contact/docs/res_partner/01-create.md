# Create Partner for Chatwoot Sync

> **Module:** `ssi_connector_chatwoot_contact`\
> **Model:** `res.partner`\
> **Menu:** Contacts > Contacts\
> **Actor:** user in group _Connector Manager_

## Pre-Condition

- **Module:** The _Contacts_ app is installed, which provides the **Contacts** menu.
- **Data:** At least one Chatwoot backend exists and is active.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Contacts > Contacts** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Name** _(required)_: Enter the partner name.
4. Open the **Chatwoot** tab.
5. Enable **Sync to Chatwoot** so that the partner is exported to every active Chatwoot
   backend.
6. Click **Save**.

## Post-Condition

- The partner is created with **Sync to Chatwoot** enabled.
- One binding per active Chatwoot backend is listed on the **Chatwoot** tab, and an
  export job is queued for each of them.

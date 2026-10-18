# Force Export Partner to Chatwoot

> **Module:** `ssi_connector_chatwoot_contact`\
> **Model:** `res.partner`\
> **Menu:** Contacts > Contacts\
> **Actor:** user in group _Connector Manager_\
> **Requires:** `01-create`

## Pre-Condition

- **Module:** The _Contacts_ app is installed, which provides the **Contacts** menu.
- **Record:** **Sync to Chatwoot** is enabled on the partner.
- **Data:** At least one Chatwoot backend exists and is active.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Contacts > Contacts** menu.
2. Find and open the partner to export.
3. Open the **Chatwoot** tab.
4. Click **Force Export to Chatwoot**. The button is only visible while **Sync to
   Chatwoot** is enabled.

## Post-Condition

- A binding exists for every active Chatwoot backend and an export job is queued for
  each of them.

# Edit Chatwoot Inbox

> **Module:** `ssi_connector_chatwoot`\
> **Model:** `chatwoot.inbox`\
> **Menu:** Connector > Configuration > Inboxes\
> **Actor:** user in group _Connector Manager_\
> **Requires:** `05-import-inbox`

## Pre-Condition

- **Record:** A Chatwoot inbox exists (inboxes are created by importing them from a
  backend, not by hand).
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Configuration > Inboxes** menu.
2. Find and open the inbox to edit.
3. Click the **Edit** button.
4. Tick **Allow Outgoing Messages** to let Odoo send messages through this inbox, or
   untick it to stop doing so. Untick **Active** to archive the inbox.
5. Click **Save**.

## Post-Condition

- The inbox is saved with the new **Allow Outgoing Messages** setting.
- An archived inbox (**Active** unticked) is hidden from the default list and shows the
  **Archived** ribbon when opened.

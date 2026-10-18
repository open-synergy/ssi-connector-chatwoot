# Import Inboxes of Chatwoot Backend

> **Module:** `ssi_connector_chatwoot`\
> **Model:** `chatwoot.backend`\
> **Menu:** Connector > Configuration > Chatwoot > Backends\
> **Actor:** user in group _Connector Manager_\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** A Chatwoot backend exists.
- **Data:** The Chatwoot account of the backend has at least one inbox.
- **Config:** The queue job runner is running, otherwise the import stays queued.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Configuration > Chatwoot > Backends** menu.
2. Find and open the backend whose inboxes must be imported.
3. Click the **Import Inboxes** button in the header.

## Post-Condition

- An **Import Inboxes** notification is displayed with the message _The inbox import has
  been queued._.
- Once the queued job has run, every inbox of the Chatwoot account exists once under
  **Connector > Configuration > Inboxes** for this backend.
- Importing again updates the name and channel type of known inboxes without creating
  duplicates and without changing **Allow Outgoing Messages**.
- A temporary Chatwoot error (HTTP 429, 500, 502, 503, 504) makes the job retry instead
  of fail.

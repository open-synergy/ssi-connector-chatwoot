# Export Chatwoot Contact Inbox Binding

> **Module:** `ssi_connector_chatwoot_contact`\
> **Model:** `chatwoot.contact.inbox`\
> **Menu:** Connector > Chatwoot > Bindings > Contact Inboxes\
> **Actor:** user in group _Connector Manager_\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** A contact inbox binding exists.
- **Data:** The Chatwoot backend of the binding is reachable with a valid API token.
- **Config:** The queue job runner is running, otherwise the export stays queued.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Chatwoot > Bindings > Contact Inboxes** menu.
2. Find and open the binding to export.
3. Click the **Export** button in the header.

## Post-Condition

- A **Export Contact Inbox** notification is displayed with the message _The contact
  inbox export has been queued._.
- Once the queued job has run, the contact is exported first if it has no Chatwoot ID
  yet, then **Source ID** is filled with the value returned by Chatwoot and **Last
  Synchronization** is set.
- A binding that already has a **Source ID** is not exported again.

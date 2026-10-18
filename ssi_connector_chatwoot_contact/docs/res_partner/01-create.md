# Create Contact

> **Module:** `ssi_connector_chatwoot_contact`\
> **Extends:** `ssi_partner` — model `res.partner`, aksi `01-create`

## Additional Pre-Condition

- **Access:** User is in group _Connector Manager_ to see the **Chatwoot** tab.

## Additional Fields

When this module is installed, the Contacts form gains a **Chatwoot** tab:

- **Sync to Chatwoot**: Enable it to export the contact to every active Chatwoot backend
  whenever the contact is created or one of its relevant fields (name, email, phone,
  mobile, company name, parent, **Sync to Chatwoot** itself) is changed. Optional,
  disabled by default.
- **Chatwoot Bindings**: Read-only here in practice. Lists one binding per Chatwoot
  backend with its **Chatwoot Contact ID** and **Last Synchronization**.

## Additional Post-Condition

- When **Sync to Chatwoot** is enabled, a binding is created for every active Chatwoot
  backend and an export job is queued for each of them.

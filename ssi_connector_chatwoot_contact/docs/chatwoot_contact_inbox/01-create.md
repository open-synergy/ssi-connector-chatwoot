# Create Chatwoot Contact Inbox Binding

> **Module:** `ssi_connector_chatwoot_contact`\
> **Model:** `chatwoot.contact.inbox`\
> **Menu:** Connector > Chatwoot > Bindings > Contact Inboxes\
> **Actor:** user in group _Connector Manager_

## Pre-Condition

- **Record:** A contact binding exists for the partner (see
  `chatwoot_res_partner/01-create`).
- **Record:** An inbox exists on the same Chatwoot backend as the contact binding and
  has **Allow Outgoing Messages** ticked.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Chatwoot > Bindings > Contact Inboxes** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Contact Binding** _(required)_: Select the Chatwoot contact binding of the
     partner.
   - **Inbox** _(required)_: Select the inbox. Only inboxes that allow outgoing messages
     are offered, and the inbox must belong to the same backend as the contact binding.
4. Click **Save**.

## Post-Condition

- A new binding is created and **Chatwoot Backend** is filled from the inbox.
- A contact and an inbox can be paired only once; a duplicate pair or an inbox of
  another backend is rejected.
- **Source ID** and **Last Synchronization** stay empty until the binding is exported
  (see `02-export`).

# Create Chatwoot Contact Binding

> **Module:** `ssi_connector_chatwoot_contact`\
> **Model:** `chatwoot.res.partner`\
> **Menu:** Connector > Chatwoot > Bindings > Contacts\
> **Actor:** user in group _Connector Manager_

## Pre-Condition

- **Data:** At least one Chatwoot backend exists and is active.
- **Data:** The partner to be linked exists and has no binding yet for that backend.
- **Access:** User is in group _Connector Manager_.

## Flow

1. Open the **Connector > Chatwoot > Bindings > Contacts** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Partner** _(required)_: Select the Odoo partner to link.
   - **Chatwoot Backend** _(required)_: Select the Chatwoot backend. A partner can have
     only one binding per backend.
4. Click **Save**.

## Post-Condition

- A new binding is created between the partner and the Chatwoot backend.
- **Chatwoot Contact ID** and **Last Synchronization** stay empty until the binding is
  exported (see `04-export`).

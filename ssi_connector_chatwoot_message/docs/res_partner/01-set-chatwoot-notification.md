# Set Chatwoot Notification (Contact)

> **Module:** `ssi_connector_chatwoot_message`\
> **Model:** `res.partner`\
> **Menu:** Contacts > Contacts\
> **Actor:** user who can edit contacts

## Pre-Condition

- **Record:** The contact exists and is not an internal user. Internal users choose
  their own channel in their preferences.
- **Data:** At least one Chatwoot inbox exists with **Allow Outgoing Messages** enabled
  (see the work instructions of `ssi_connector_chatwoot`).
- **Access:** User can edit contacts.

## Flow

1. Open the **Contacts > Contacts** menu.
2. Find and open the contact.
3. Click **Edit**.
4. Open the **Chatwoot Notification** tab.
5. Tick **Notify via Chatwoot**.
6. In **Chatwoot Inbox**, select the inbox that delivers the notifications of this
   contact. The field is required while **Notify via Chatwoot** is ticked.
7. Click **Save**.

## Post-Condition

- Chatter notifications addressed to this contact (as a follower or a recipient) are
  sent as Chatwoot messages in the selected inbox instead of email.
- The contact is flagged **Sync to Chatwoot** and is exported to Chatwoot.
- Password reset, signup, portal invitation and bounce emails are not affected: they
  stay email.

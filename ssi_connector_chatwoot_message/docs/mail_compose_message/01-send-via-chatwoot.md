# Send Message via Chatwoot (Composer)

> **Module:** `ssi_connector_chatwoot_message`\
> **Model:** `mail.compose.message`\
> **Menu:** Contacts > Contacts\
> **Actor:** user who can post messages on contacts

## Pre-Condition

- **Record:** The contact that receives the message exists and has an email address.
  Without one, Odoo asks you to complete the contact before the composer can be used.
- **Data:** At least one Chatwoot inbox exists with **Allow Outgoing Messages** enabled
  (see the work instructions of `ssi_connector_chatwoot`).
- **Access:** User can edit contacts and post messages in the chatter.

## Flow

1. Open the **Contacts > Contacts** menu.
2. Find and open the contact.
3. In the chatter, click **Send message**.
4. In the message box, click the **Full composer** button.
5. In **Recipients**, add the contact that receives the message.
6. In **Subject**, type the subject of the message.
7. In **Send Via**, select **Chatwoot**.
8. In **Chatwoot Inbox**, select the inbox that delivers the message. The field is
   required while **Send Via** is **Chatwoot**.
9. Click **Send**.

## Post-Condition

- The recipients added in **Recipients** receive the message, and the files attached to
  it, as Chatwoot messages in the selected inbox instead of email.
- The inbox selected in the composer is used even when a recipient prefers another
  inbox.
- The other followers of the document keep their own notification preference.
- Sending via Chatwoot without an inbox is rejected.

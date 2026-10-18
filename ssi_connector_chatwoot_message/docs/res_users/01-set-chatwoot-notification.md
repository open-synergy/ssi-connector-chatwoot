# Set Chatwoot Notification (User)

> **Module:** `ssi_connector_chatwoot_message`\
> **Model:** `res.users`\
> **Menu:** User menu > Preferences\
> **Actor:** any internal user

## Pre-Condition

- **Data:** At least one Chatwoot inbox exists with **Allow Outgoing Messages** enabled
  (see the work instructions of `ssi_connector_chatwoot`).
- **Access:** User is an internal user. No extra group is needed.

## Flow

1. Open the user menu (your name in the top bar), then click the **Preferences** menu
   item.
2. In **Notification**, select **Handle by Chatwoot**.
3. In **Chatwoot Inbox**, select the inbox that delivers your notifications. Only
   inboxes that allow outgoing messages are offered. The field is required while
   **Handle by Chatwoot** is selected.
4. Click **Save**.

## Post-Condition

- The notifications you receive in the chatter are sent as Chatwoot messages in the
  selected inbox instead of email. They are queued and sent in the background; the
  delivery status is kept on the notification.
- Your contact is flagged **Sync to Chatwoot** and is exported to Chatwoot.
- Password reset, signup, portal invitation and bounce emails are not affected: they
  stay email.

# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from unittest import mock

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged

REQUEST_PATH = (
    "odoo.addons.ssi_connector_chatwoot.components.backend_adapter.requests.request"
)


@tagged("post_install", "-at_install")
class TestMailComposeMessage(YamlTransactionCase):
    """Tests of the Chatwoot delivery of the message composer."""

    def setUp(self):
        """Create the backend, inboxes, recipient and document fixtures."""
        super().setUp()
        self.backend = self.env["chatwoot.backend"].create(
            {
                "name": "Python Compose Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "test-token",
            }
        )
        self.inbox_a = self.env["chatwoot.inbox"].create(
            {
                "name": "Python Compose Inbox A",
                "backend_id": self.backend.id,
                "chatwoot_id": "5",
                "allow_outgoing": True,
            }
        )
        self.inbox_b = self.env["chatwoot.inbox"].create(
            {
                "name": "Python Compose Inbox B",
                "backend_id": self.backend.id,
                "chatwoot_id": "6",
                "allow_outgoing": True,
            }
        )
        self.recipient = self.env["res.partner"].create(
            {
                "name": "Python Compose Recipient",
                "email": "python.compose@example.com",
                "chatwoot_notify": True,
                "chatwoot_inbox_id": self.inbox_a.id,
            }
        )
        self.document = self.env["res.partner"].create(
            {"name": "Python Compose Document"}
        )

    def test_composer_scenarios(self):
        """Run the YAML scenarios of the composer.

        Covers the missing inbox error and the Chatwoot notification
        of the recipients.
        """
        self.run_yaml_scenario("test_data_mail_compose_message.yaml")

    @staticmethod
    def _response(payload):
        """Build a fake successful HTTP response.

        :param payload: the JSON body of the response
        :return: a mock response object
        """
        response = mock.Mock(ok=True, content=b"{}")
        response.json.return_value = payload
        return response

    def _responses(self):
        """Return the responses of a first export: four API calls.

        :return: list of fake responses in call order
        """
        return [
            self._response({"payload": {"contact": {"id": 7}}}),
            self._response({"source_id": "src-1"}),
            self._response({"id": 21}),
            self._response({"id": 99}),
        ]

    def _send(self, subject, inbox=None, attachments=None, send_via="chatwoot"):
        """Send a message to the recipient through the composer.

        :param subject: subject of the message
        :param inbox: ``chatwoot.inbox`` chosen in the composer
        :param attachments: ``ir.attachment`` records to attach
        :param send_via: value of the ``send_via`` field
        :return: the posted ``mail.message``
        """
        values = {
            "composition_mode": "comment",
            "model": "res.partner",
            "res_id": self.document.id,
            "subject": subject,
            "body": "<p>Python body</p>",
            "partner_ids": [(6, 0, self.recipient.ids)],
            "send_via": send_via,
            "chatwoot_inbox_id": inbox.id if inbox else False,
            "attachment_ids": [(6, 0, (attachments or self.env["ir.attachment"]).ids)],
        }
        self.env["mail.compose.message"].create(values).send_mail()
        return self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("subject", "=", subject)]
        )

    def _binding(self, message):
        """Return the Chatwoot binding of the recipient for a message.

        :param message: the posted ``mail.message``
        :return: the ``chatwoot.mail.notification`` record
        """
        notification = self.env["mail.notification"].search(
            [
                ("mail_message_id", "=", message.id),
                ("res_partner_id", "=", self.recipient.id),
                ("notification_type", "=", "chatwoot"),
            ]
        )
        return notification.chatwoot_bind_ids

    def test_no_mail_and_composer_inbox_wins(self):
        """Assert no email is created and the composer inbox is used.

        Pure Python - trigger P6 (L-15: the export job is not run, so no
        network call is made; the binding is inspected instead).
        """
        message = self._send("Python Compose One", inbox=self.inbox_b)
        binding = self._binding(message)
        self.assertEqual(len(binding), 1)
        self.assertEqual(binding.inbox_id, self.inbox_b)
        mails = self.env["mail.mail"].search(
            [
                ("mail_message_id", "=", message.id),
                ("recipient_ids", "in", self.recipient.ids),
            ]
        )
        self.assertFalse(mails)

    def test_email_uses_recipient_preference(self):
        """Assert a composer sent via email keeps the recipient preference.

        Pure Python - trigger P6 (L-15: no export job is run).
        """
        message = self._send("Python Compose Two", send_via="email")
        notification = self.env["mail.notification"].search(
            [
                ("mail_message_id", "=", message.id),
                ("res_partner_id", "=", self.recipient.id),
            ]
        )
        self.assertEqual(notification.notification_type, "chatwoot")
        self.assertEqual(notification.chatwoot_bind_ids.inbox_id, self.inbox_a)

    def test_other_followers_keep_their_preference(self):
        """Assert a follower outside the recipients keeps its channel.

        Pure Python - trigger P6 (L-15: no export job is run).
        """
        user = self.env["res.users"].create(
            {
                "name": "Python Compose Follower",
                "login": "python_compose_follower",
                "email": "python.follower@example.com",
                "notification_type": "email",
            }
        )
        self.document.message_subscribe(partner_ids=user.partner_id.ids)
        message = self._send("Python Compose Three", inbox=self.inbox_b)
        notification = self.env["mail.notification"].search(
            [
                ("mail_message_id", "=", message.id),
                ("res_partner_id", "=", user.partner_id.id),
            ]
        )
        self.assertEqual(notification.notification_type, "email")

    def test_attachment_is_sent_as_multipart(self):
        """Assert a message with an attachment is posted as multipart.

        Pure Python - trigger P6 (L-15: ``requests.request`` must be
        patched so that no network call is made).
        """
        attachment = self.env["ir.attachment"].create(
            {
                "name": "python_compose.pdf",
                "datas": base64.b64encode(b"%PDF-python"),
                "mimetype": "application/pdf",
            }
        )
        message = self._send(
            "Python Compose Four", inbox=self.inbox_b, attachments=attachment
        )
        binding = self._binding(message)
        with mock.patch(REQUEST_PATH, side_effect=self._responses()) as req:
            binding.export_record()
        last = req.call_args_list[3]
        self.assertTrue(last[0][1].endswith("/conversations/21/messages"))
        self.assertNotIn("json", last[1])
        self.assertNotIn("Content-Type", last[1]["headers"])
        self.assertEqual(last[1]["data"]["message_type"], "outgoing")
        files = last[1]["files"]
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0][0], "attachments[]")
        self.assertEqual(files[0][1][0], "python_compose.pdf")
        self.assertEqual(files[0][1][1], b"%PDF-python")
        self.assertEqual(files[0][1][2], "application/pdf")

    def test_message_without_attachment_is_sent_as_json(self):
        """Assert a message without attachment is still posted as JSON.

        Pure Python - trigger P6 (L-15: ``requests.request`` must be
        patched so that no network call is made).
        """
        message = self._send("Python Compose Five", inbox=self.inbox_b)
        binding = self._binding(message)
        with mock.patch(REQUEST_PATH, side_effect=self._responses()) as req:
            binding.export_record()
        last = req.call_args_list[3]
        self.assertNotIn("files", last[1])
        self.assertEqual(last[1]["json"]["message_type"], "outgoing")
        self.assertNotIn("attachment_ids", last[1]["json"])

# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

import requests
from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged

from odoo.addons.ssi_connector_chatwoot_message.components.mail_notification import (
    ChatwootMailNotificationExporter,
)

REQUEST_PATH = (
    "odoo.addons.ssi_connector_chatwoot.components.backend_adapter.requests.request"
)


@tagged("post_install", "-at_install")
class TestMailNotification(YamlTransactionCase):
    """Python tests for the export of Chatwoot message bindings."""

    def setUp(self):
        """Create the backend, inbox, recipient and document fixtures."""
        super().setUp()
        self.backend = self.env["chatwoot.backend"].create(
            {
                "name": "Python Message Backend",
                "url": "https://chatwoot.example.com",
                "account_id": 1,
                "api_token": "test-token",
            }
        )
        self.inbox = self.env["chatwoot.inbox"].create(
            {
                "name": "Python Message Inbox",
                "backend_id": self.backend.id,
                "chatwoot_id": "5",
                "allow_outgoing": True,
            }
        )
        self.recipient = self.env["res.partner"].create(
            {
                "name": "Python Message Recipient",
                "chatwoot_notify": True,
                "chatwoot_inbox_id": self.inbox.id,
            }
        )
        self.author = self.env["res.partner"].create({"name": "Python Author"})
        self.document = self.env["res.partner"].create(
            {"name": "Python Message Document"}
        )
        self.document.message_subscribe(partner_ids=[self.recipient.id])

    @staticmethod
    def _response(payload):
        """Build a fake successful HTTP response.

        :param payload: the JSON body of the response
        :return: a mock response object
        """
        response = mock.Mock(ok=True, content=b"{}")
        response.json.return_value = payload
        return response

    @staticmethod
    def _error_response(status_code):
        """Build a fake HTTP error response.

        :param status_code: the HTTP status of the response
        :return: a mock response object
        """
        response = mock.Mock(
            ok=False,
            status_code=status_code,
            reason="Unprocessable Entity",
            url="https://chatwoot.example.com/messages",
            content=b"{}",
        )
        response.json.return_value = {"error": "invalid"}
        return response

    def _post(self, body="Python body"):
        """Post a comment on the document and return the binding.

        :param body: HTML body of the message
        :return: the ``chatwoot.mail.notification`` of the recipient
        """
        message = self.document.message_post(
            body=body,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            author_id=self.author.id,
        )
        notification = self.env["mail.notification"].search(
            [
                ("mail_message_id", "=", message.id),
                ("res_partner_id", "=", self.recipient.id),
                ("notification_type", "=", "chatwoot"),
            ]
        )
        return notification

    def _success_responses(self):
        """Return the responses of a first export: four API calls.

        :return: list of fake responses in call order
        """
        return [
            self._response({"payload": {"contact": {"id": 7}}}),
            self._response({"source_id": "src-1"}),
            self._response({"id": 21}),
            self._response({"id": 99}),
        ]

    def test_export_creates_dependencies_and_reuses_conversation(self):
        """Assert dependencies are created in order and the chat is reused.

        Pure Python - trigger P6 (L-15: ``requests.request`` must be
        patched so that no network call is made).
        """
        notification = self._post("First")
        binding = notification.chatwoot_bind_ids
        self.assertEqual(len(binding), 1)
        with mock.patch(REQUEST_PATH, side_effect=self._success_responses()) as req:
            binding.export_record()
        calls = req.call_args_list
        self.assertEqual(len(calls), 4)
        self.assertTrue(calls[0][0][1].endswith("/contacts"))
        self.assertTrue(calls[1][0][1].endswith("/contacts/7/contact_inboxes"))
        self.assertTrue(calls[2][0][1].endswith("/conversations"))
        self.assertTrue(calls[3][0][1].endswith("/conversations/21/messages"))
        self.assertEqual(calls[3][1]["json"]["message_type"], "outgoing")
        self.assertEqual(binding.chatwoot_id, "99")
        self.assertEqual(notification.notification_status, "sent")
        second = self._post("Second").chatwoot_bind_ids
        with mock.patch(REQUEST_PATH, side_effect=[self._response({"id": 100})]) as req:
            second.export_record()
        self.assertEqual(req.call_count, 1)
        self.assertTrue(req.call_args[0][1].endswith("/conversations/21/messages"))
        self.assertEqual(second.conversation_id, binding.conversation_id)
        self.assertEqual(
            self.env["chatwoot.conversation"].search_count(
                [("backend_id", "=", self.backend.id)]
            ),
            1,
        )

    def test_permanent_error_marks_exception(self):
        """Assert a permanent API error is stored and not raised.

        Pure Python - trigger P6 (L-15: ``requests.request`` must be
        patched so that no network call is made).
        """
        notification = self._post()
        responses = self._success_responses()[:3] + [self._error_response(422)]
        with mock.patch(REQUEST_PATH, side_effect=responses):
            notification.chatwoot_bind_ids.export_record()
        self.assertEqual(notification.notification_status, "exception")
        self.assertEqual(notification.failure_type, "chatwoot_server")
        self.assertIn("422", notification.failure_reason)

    def test_retryable_error_is_raised_until_last_attempt(self):
        """Assert a retryable error is raised, then stored on the last try.

        Pure Python - trigger P6 (L-15: ``requests.request`` must be
        patched so that no network call is made).
        """
        notification = self._post()
        binding = notification.chatwoot_bind_ids
        error = requests.ConnectionError("down")
        with mock.patch(REQUEST_PATH, side_effect=error):
            with self.assertRaises(Exception) as caught:
                binding.export_record()
        self.assertEqual(type(caught.exception).__name__, "NetworkRetryableError")
        self.assertEqual(notification.notification_status, "ready")
        with mock.patch(REQUEST_PATH, side_effect=error), mock.patch.object(
            ChatwootMailNotificationExporter, "_is_last_attempt", return_value=True
        ):
            binding.export_record()
        self.assertEqual(notification.notification_status, "exception")
        self.assertEqual(notification.failure_type, "chatwoot_server")

    def test_inbox_not_allowed_marks_exception(self):
        """Assert an inbox that no longer allows messages is not called.

        Pure Python - trigger P6 (L-15: ``requests.request`` must be
        patched so that no network call is made).
        """
        self.inbox.write({"allow_outgoing": False})
        with mock.patch(REQUEST_PATH) as request:
            message = self.document.message_post(
                body="Python body",
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
        request.assert_not_called()
        notification = self.env["mail.notification"].search(
            [
                ("mail_message_id", "=", message.id),
                ("res_partner_id", "=", self.recipient.id),
            ]
        )
        self.assertEqual(notification.notification_type, "chatwoot")
        self.assertEqual(notification.notification_status, "exception")
        self.assertEqual(notification.failure_type, "chatwoot_inbox")
        self.assertFalse(notification.chatwoot_bind_ids)

    def test_mapper_content(self):
        """Assert the content holds author, document, text and link.

        Pure Python - trigger P1 (L-01: mapper values are a return value
        that the ``call`` action discards).
        """
        binding = self._post("<p>Hello <b>team</b></p>").chatwoot_bind_ids
        with self.backend.work_on("chatwoot.mail.notification") as work:
            mapper = work.component(usage="export.mapper")
            values = mapper.map_record(binding).values(for_create=True)
        content = values["content"]
        first_line = content.splitlines()[0]
        self.assertIn("Python Author", first_line)
        self.assertIn("Python Message Document", first_line)
        self.assertIn("Hello", content)
        self.assertIn("team", content)
        self.assertIn("/mail/view", content)
        self.assertEqual(values["message_type"], "outgoing")

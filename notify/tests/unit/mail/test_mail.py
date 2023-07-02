from email.mime.multipart import MIMEMultipart
from unittest.mock import MagicMock

import pytest

from notify.mail.config import TestConfig
from notify.mail.mail_sender import MailSender


@pytest.fixture()
def mail_sender():
    test_config = TestConfig()
    mail_sender: MailSender = MailSender(test_config)
    yield mail_sender


class TestMailSender:
    @pytest.fixture(autouse=True)
    def setup(self, mail_sender):
        self.mail_sender = mail_sender

    @pytest.fixture
    def test_message(self):
        title = "Test title"
        msg = "Test message"
        reciever = self.mail_sender.config.MAIL_FROM
        message: MIMEMultipart = self.mail_sender._create_mime_message(title, msg, reciever)
        yield message

    def test_create_mime_message(self):
        title = "Test title"
        msg = "Test message"
        reciever = "test@example.com"
        message: MIMEMultipart = self.mail_sender._create_mime_message(title, msg, reciever)
        assert message["From"] == self.mail_sender.config.MAIL_FROM
        assert message["To"] == reciever
        assert message["Subject"] == title
        text = message.get_payload()[0]
        assert str(text).endswith(msg)

    def test_send(self, test_message):
        title = "Test title"
        msg = "Test message"
        reciever = self.mail_sender.config.MAIL_FROM
        self.mail_sender._create_mime_message = MagicMock(return_value=test_message)
        self.mail_sender.send(title, msg, reciever)
        self.mail_sender._create_mime_message.assert_called_once_with(title, msg, reciever)

    def test_send_error(self):
        title = "Test title"
        msg = "Test message"
        reciever = ""
        assert not self.mail_sender.send(title, msg, reciever)

import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from notify.app.logger import LoggerType, create_logger

from .config import Config

logger = create_logger(LoggerType.MAIL, 'MAIL_SENDER')

class Sender(ABC):
    @abstractmethod
    def send(self, msg: str) -> bool:
        ...


class MailSender(Sender):
    def __init__(self, config=Config()):
        self.config = config
        if self.config.SMTP_USERNAME is None or self.config.SMTP_PASSWORD is None:
            raise ValueError('SMTP_USERNAME and SMTP_PASSWORD must be set')

    def _send_with_smtp(self, message: MIMEMultipart, reciever: str) -> None:
        """
        Sends an email message using SMTP.

        Args:
            message: A `MIMEMultipart` object representing the email message to be sent.
            receiver: A string representing the email address of the recipient.
        """
        with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
            server.starttls()
            logger.info(f'Logging in with {self.config.SMTP_USERNAME}')
            server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
            server.sendmail(self.config.MAIL_FROM, reciever, message.as_string())

    def _create_mime_message(self, title: str, msg: str, receiver: str) -> MIMEMultipart:
        """
        This method creates a MIME message for an email with the specified title, message, and recipient.

        Args:
            title: A string representing the title of the email.
            msg: A string representing the body of the email.
            receiver: A string representing the email address of the recipient.

        Returns:
            A `MIMEMultipart` object representing the MIME message for the email.
        """
        message = MIMEMultipart()
        message['From'] = self.config.MAIL_FROM
        message['To'] = receiver
        message['Subject'] = title
        message.attach(MIMEText(msg.replace('\n', '<br>'), 'html'))
        return message

    def send(self, subject: str, msg: str, receiver: str) -> bool:
        """
        Sends an email message to a recipient.

        Args:
            subject: A string representing the subject of the email.
            msg: A string representing the body of the email.
            receiver: A string representing the email address of the recipient.

        Returns:
            A boolean indicating whether the email was successfully sent.
        """
        try:
            message = self._create_mime_message(subject, msg, receiver)
            self._send_with_smtp(message, receiver)
            logger.info(f'Sent email to {receiver}')
            return True
        except Exception as e:
            logger.exception(f'Error sending email: {e}')
            return False

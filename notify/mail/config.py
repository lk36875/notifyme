import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    SMTP_PORT: int = 587
    SMTP_SERVER: str = 'smtp.gmail.com'
    MAIL_USE_TLS: bool = True
    SMTP_USERNAME: str = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD: str = os.environ.get('SMTP_PASSWORD', '')
    MAIL_FROM: str = os.environ.get('SMTP_USERNAME', '')

@dataclass
class TestConfig(Config):
    __test__ = False
    TEST: bool = True

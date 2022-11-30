import pytest
from notifiers import TwilioNotifier
from loguru import logger
import os

from utils import Individual


@pytest.fixture
def twilio_notifier():
    return TwilioNotifier(
            os.environ["TWILIO_MESSAGING_SERVICE_SID"],
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"])


class TestNotifiersBasic:
    def test_twilio_notifier(self, twilio_notifier):
        sender = Individual(
            "John Gibson",
            "+12169731312"
        )
        receiver = Individual(
            "Test Recipient",
            "Test Phone Number",
            groups=set(),
            notes="This is my test note"
        )
        twilio_notifier.notify(sender, receiver)



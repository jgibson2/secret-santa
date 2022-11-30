from utils import Individual
from loguru import logger
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

class Notifier:
    def notify(self, sender: Individual, recipient: Individual):
        raise NotImplementedError()


class TwilioNotifier:
    def __init__(self, twilio_messaging_service_sid: str, twilio_account_sid: str, twilio_auth_token: str):
        self.twilio_messaging_service_sid = twilio_messaging_service_sid
        self.twilio_client = Client(twilio_account_sid, twilio_auth_token)

    def notify(self, sender: Individual, recipient: Individual):
        message = \
            f'''
Dear {sender.name}:

You have been assigned the following person for Secret Santa: 
{recipient.name}

The following notes have been provided:
===================================
{recipient.notes or ""}
===================================

Best,
Your pals at Secret Santa
'''
        try:
            self.twilio_client.messages.create(
                messaging_service_sid=self.twilio_messaging_service_sid,
                body=message,
                to=sender.contact
            )
        except TwilioRestException as e:
            raise RuntimeError(f"Twilio error: {e}")


class GmailNotifier:
    '''
    UNTESTED
    '''
    def __init__(self, service_email_address: str):
        import google.auth
        from googleapiclient.discovery import build
        self.service_email_address = service_email_address
        self.creds, _ = google.auth.default()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def notify(self, sender: Individual, recipient: Individual):
        import base64
        from email.message import EmailMessage
        from googleapiclient.errors import HttpError
        try:
            message = EmailMessage()

            message.set_content(f'''
Dear {sender.name}:

You have been assigned the following person for Secret Santa: 
{recipient.name}

The following notes have been provided:
============================================================================
{recipient.notes or ""}
============================================================================

Best,
Your pals at Secret Santa
''')

            message['To'] = sender.contact
            message['From'] = self.service_email_address
            message['Subject'] = 'Your Secret Santa Assignment'

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
                .decode()

            create_message = {
                'raw': encoded_message
            }
            # pylint: disable=E1101
            send_message = (self.service.users().messages().send
                            (userId="me", body=create_message).execute())
            logger.info(f'Sent message with ID: {send_message["id"]}')
        except HttpError as error:
            logger.info(f'Error encountered while sending message to {sender.contact}: {error}')
            raise RuntimeError(str(error))

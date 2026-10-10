import os
import re
import logging
from datetime import datetime
from models import db, NotificationAttempt

logger = logging.getLogger("sheshield.notifications")


class NotificationService:
    """
    Notification service abstraction for emergency alerts.
    Supports SMS and automated Voice Calls via Twilio or local Mock mode.
    Supports authentication via Twilio API Key (SID + Secret) or Master Auth Token.
    """
    def __init__(self, provider: str = None):
        self._provider = provider

    @property
    def provider(self):
        try:
            from flask import current_app, has_app_context
            if has_app_context():
                if current_app.config.get("TESTING"):
                    return "mock"
                return current_app.config.get("SMS_PROVIDER") or os.environ.get("SMS_PROVIDER", "mock")
        except Exception:
            pass
        return os.environ.get("SMS_PROVIDER", "mock")

    @staticmethod
    def _format_e164(raw_phone: str) -> str:
        """Normalizes Indian and international phone numbers to E.164 format."""
        cleaned_digits = re.sub(r'[^\d+]', '', (raw_phone or "").strip())
        if not cleaned_digits.startswith("+"):
            if len(cleaned_digits) == 10:
                return f"+91{cleaned_digits}"
            elif len(cleaned_digits) == 12 and cleaned_digits.startswith("91"):
                return f"+{cleaned_digits}"
            return f"+{cleaned_digits}"
        return cleaned_digits

    def _get_twilio_client(self):
        """
        Creates authenticated Twilio Client using either:
        1. API Key SID + API Key Secret + Account SID
        2. Or Account SID + Master Auth Token
        """
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        api_key_sid = os.environ.get("TWILIO_API_KEY_SID") or os.environ.get("TWILIO_API_KEY")
        api_key_secret = os.environ.get("TWILIO_API_KEY_SECRET") or os.environ.get("TWILIO_API_SECRET")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

        from twilio.rest import Client
        if account_sid and auth_token:
            return Client(account_sid, auth_token)
        elif api_key_sid and api_key_secret and account_sid:
            return Client(api_key_sid, api_key_secret, account_sid)
        return None

    def send_sos_alert(self, sos_event, contact, place_voice_call=False) -> NotificationAttempt:
        """
        Dispatches emergency SOS notification SMS to a trusted contact.
        Optionally places an emergency automated phone call.
        """
        active_provider = self.provider
        attempt = NotificationAttempt(
            sos_event_id=sos_event.id,
            contact_id=contact.id if hasattr(contact, "id") else None,
            contact_name=contact.name if hasattr(contact, "name") else "Emergency Contact",
            contact_phone=contact.phone_number if hasattr(contact, "phone_number") else "",
            channel="SMS" if active_provider != "mock" else "MOCK",
            created_at=datetime.utcnow()
        )

        message_body = (
            f"EMERGENCY ALERT from SheShield: A safety SOS was activated. "
            f"Event Status: {sos_event.status}. "
        )
        if sos_event.latitude and sos_event.longitude:
            message_body += f"Location: https://maps.google.com/?q={sos_event.latitude},{sos_event.longitude}. "
        message_body += f"Live Tracking & Evidence: http://127.0.0.1:5000/sos/track/{sos_event.token}. "
        message_body += "In immediate danger call 112."

        if active_provider == "mock":
            attempt.status = "MOCK_SENT"
            attempt.provider_response = (
                f"[DEMO/MOCK MODE] SMS simulated to {attempt.contact_phone}. "
                f"Message content: '{message_body}'. No real carrier network accessed."
            )
            logger.info("Notification Mock: %s", attempt.provider_response)

        elif self.provider == "twilio":
            from_number = os.environ.get("TWILIO_FROM_NUMBER") or os.environ.get("TWILIO_PHONE_NUMBER")
            twilio_client = self._get_twilio_client()

            if not (twilio_client and from_number):
                attempt.status = "FAILED"
                attempt.provider_response = "Twilio credentials or sender phone number missing."
                logger.error("Twilio provider configured but credentials or from_number missing.")
            else:
                to_number = self._format_e164(attempt.contact_phone)
                try:
                    msg = twilio_client.messages.create(
                        body=message_body,
                        from_=from_number,
                        to=to_number
                    )
                    attempt.status = "DELIVERED" if msg.status in ("delivered", "sent", "queued") else "ATTEMPTED"
                    attempt.provider_response = f"Twilio SID: {msg.sid} | Status: {msg.status} | Sent to: {to_number}"
                    logger.info("Twilio SMS dispatched to %s: SID=%s", to_number, msg.sid)
                except Exception as ex:
                    attempt.status = "FAILED"
                    attempt.provider_response = f"Twilio SMS Error: {str(ex)}"
                    logger.error("Twilio SMS delivery failed to %s: %s", to_number, str(ex))
        else:
            attempt.status = "FAILED"
            attempt.provider_response = f"Unknown notification provider: {self.provider}"

        db.session.add(attempt)
        db.session.commit()

        # If voice call requested, trigger automated emergency call as well
        if place_voice_call:
            self.make_emergency_call(sos_event, contact)

        return attempt

    def make_emergency_call(self, sos_event, contact) -> NotificationAttempt:
        """
        Places an automated emergency voice phone call to alert the trusted contact.
        Plays synthesized speech in Indian English instructing them to check their SMS for live tracking.
        """
        active_provider = self.provider
        attempt = NotificationAttempt(
            sos_event_id=sos_event.id,
            contact_id=contact.id if hasattr(contact, "id") else None,
            contact_name=contact.name if hasattr(contact, "name") else "Emergency Contact",
            contact_phone=contact.phone_number if hasattr(contact, "phone_number") else "",
            channel="VOICE_CALL" if active_provider != "mock" else "MOCK_CALL",
            created_at=datetime.utcnow()
        )

        if active_provider == "mock":
            attempt.status = "MOCK_SENT"
            attempt.provider_response = (
                f"[DEMO/MOCK MODE] Emergency automated voice call simulated to {attempt.contact_phone}."
            )
            logger.info("Voice Call Mock: %s", attempt.provider_response)

        elif self.provider == "twilio":
            from_number = os.environ.get("TWILIO_FROM_NUMBER") or os.environ.get("TWILIO_PHONE_NUMBER")
            twilio_client = self._get_twilio_client()

            if not (twilio_client and from_number):
                attempt.status = "FAILED"
                attempt.provider_response = "Twilio credentials or sender phone number missing."
                logger.error("Twilio Voice Call failed: credentials or from_number missing.")
            else:
                to_number = self._format_e164(attempt.contact_phone)
                try:
                    twiml_speech = (
                        "<Response>"
                        "<Pause length=\"1\"/>"
                        "<Say>"
                        "Emergency Alert from SheShield. A safety emergency has been activated. "
                        "Please check your SMS messages immediately for live location tracking and audio evidence. "
                        "If the person is in immediate danger, dial 1 1 2."
                        "</Say>"
                        "</Response>"
                    )
                    call = twilio_client.calls.create(
                        twiml=twiml_speech,
                        from_=from_number,
                        to=to_number
                    )
                    attempt.status = "DELIVERED" if call.status in ("queued", "ringing", "in-progress", "completed") else "ATTEMPTED"
                    attempt.provider_response = f"Twilio Call SID: {call.sid} | Status: {call.status} | Dialed: {to_number}"
                    logger.info("Twilio Voice Call placed to %s: SID=%s", to_number, call.sid)
                except Exception as ex:
                    attempt.status = "FAILED"
                    attempt.provider_response = f"Twilio Call Error: {str(ex)}"
                    logger.error("Twilio Voice Call failed to %s: %s", to_number, str(ex))
        else:
            attempt.status = "FAILED"
            attempt.provider_response = f"Unknown provider: {self.provider}"

        db.session.add(attempt)
        db.session.commit()
        return attempt


notification_service = NotificationService()

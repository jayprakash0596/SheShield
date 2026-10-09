import os
import logging
from datetime import datetime
from models import db, NotificationAttempt

logger = logging.getLogger("sheshield.notifications")


class NotificationService:
    """
    Notification service abstraction for emergency alerts.
    Supports safe mock mode for local development/testing, and provider configuration for production.
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

    def send_sos_alert(self, sos_event, contact) -> NotificationAttempt:
        """
        Dispatches emergency SOS notification to a trusted contact.
        Records an authoritative NotificationAttempt audit record.
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
            # Safe mock dispatch for local development & automated test suites
            attempt.status = "MOCK_SENT"
            attempt.provider_response = (
                f"[DEMO/MOCK MODE] SMS simulated to {attempt.contact_phone}. "
                f"Message content: '{message_body}'. No real carrier network accessed."
            )
            logger.info("Notification Mock: %s", attempt.provider_response)

        elif self.provider == "twilio":
            # Real Twilio SMS integration
            account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
            auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
            from_number = os.environ.get("TWILIO_FROM_NUMBER") or os.environ.get("TWILIO_PHONE_NUMBER")

            if not (account_sid and auth_token and from_number):
                attempt.status = "FAILED"
                attempt.provider_response = "Twilio credentials missing in configuration."
                logger.error("Twilio provider configured but credentials missing.")
            else:
                # Format destination phone number to E.164 standard
                raw_phone = attempt.contact_phone.strip()
                import re
                cleaned_digits = re.sub(r'[^\d+]', '', raw_phone)
                if not cleaned_digits.startswith("+"):
                    if len(cleaned_digits) == 10:
                        to_number = f"+91{cleaned_digits}"
                    elif len(cleaned_digits) == 12 and cleaned_digits.startswith("91"):
                        to_number = f"+{cleaned_digits}"
                    else:
                        to_number = f"+{cleaned_digits}"
                else:
                    to_number = cleaned_digits

                try:
                    from twilio.rest import Client
                    twilio_client = Client(account_sid, auth_token)
                    msg = twilio_client.messages.create(
                        body=message_body,
                        from_=from_number,
                        to=to_number
                    )
                    # Status from Twilio: queued, sent, delivered, etc.
                    attempt.status = "DELIVERED" if msg.status in ("delivered", "sent", "queued") else "ATTEMPTED"
                    attempt.provider_response = f"Twilio SID: {msg.sid} | Status: {msg.status} | Sent to: {to_number}"
                    logger.info("Twilio SMS dispatched successfully to %s: SID=%s", to_number, msg.sid)
                except Exception as ex:
                    attempt.status = "FAILED"
                    attempt.provider_response = f"Twilio API Error: {str(ex)}"
                    logger.error("Twilio SMS delivery failed to %s: %s", to_number, str(ex))
        else:
            attempt.status = "FAILED"
            attempt.provider_response = f"Unknown notification provider: {self.provider}"

        db.session.add(attempt)
        db.session.commit()
        return attempt


notification_service = NotificationService()

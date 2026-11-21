import json
import logging
import urllib.request
from email.utils import parseaddr

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class BrevoEmailBackend(BaseEmailBackend):
    """Envia e-mails pela API HTTP do Brevo (funciona onde o SMTP é bloqueado)."""

    def send_messages(self, email_messages):
        enviados = 0

        for msg in email_messages:
            nome, remetente = parseaddr(msg.from_email or settings.DEFAULT_FROM_EMAIL)

            sender = {"email": remetente}
            if nome:
                sender["name"] = nome

            corpo = {
                "sender": sender,
                "to": [{"email": e} for e in msg.to],
                "subject": msg.subject,
                "textContent": msg.body,
            }

            pedido = urllib.request.Request(
                "https://api.brevo.com/v3/smtp/email",
                data=json.dumps(corpo).encode("utf-8"),
                headers={
                    "api-key": settings.BREVO_API_KEY,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "ImpactaESG/1.0",
                },
                method="POST",
            )

            try:
                with urllib.request.urlopen(pedido, timeout=15):
                    enviados += 1
            except Exception:
                logger.exception("Falha ao enviar e-mail pelo Brevo")
                if not self.fail_silently:
                    raise

        return enviados
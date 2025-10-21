import os
from typing import List
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)


def enviar_whatsapp(mensagem: str, destinatarios: List[str]) -> bool:
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    origem = os.getenv("TWILIO_WHATSAPP_FROM")  # ex: "whatsapp:+1415XXXXXXX"
    if not (sid and token and origem and destinatarios):
        logger.warning("Twilio config missing")
        return False
    client = Client(sid, token)
    try:
        for to in destinatarios:
            client.messages.create(body=mensagem, from_=origem, to=to)
        return True
    except Exception as e:
        logger.error(f"Falha WhatsApp: {e}")
        return False

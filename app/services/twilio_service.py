from twilio.rest import Client
from core.config import settings # (En tu código ya está importado así, es correcto)
import requests

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_sms(to_number: str, message: str):
    """Envía un mensaje SMS."""
    try:
        message = client.messages.create(
            body=message,
            # CAMBIO: Usamos el número específico para SMS
            from_=settings.TWILIO_SMS_NUMBER,
            to=to_number
        )
        print(f"SMS enviado a {to_number} desde {settings.TWILIO_SMS_NUMBER}. SID: {message.sid}", flush=True)
        return message.sid
    except Exception as e:
        print(f"Error al enviar SMS a {to_number}: {e}", flush=True)
        raise

def make_call(to_number: str, message: str):
    """Realiza una llamada y reproduce un mensaje usando TwiML."""
    try:
        twiml_message = f'<Response><Say language="es-MX">{message}</Say></Response>'
        
        call = client.calls.create(
            twiml=twiml_message,
            to=to_number,
            # SIN CAMBIOS: Esta función ya usa el número correcto para llamadas
            from_=settings.TWILIO_PHONE_NUMBER
        )
        print(f"Llamada iniciada a {to_number} desde {settings.TWILIO_PHONE_NUMBER}. SID: {call.sid}", flush=True)
        return call.sid
    except Exception as e:
        print(f"Error al realizar llamada a {to_number}: {e}", flush=True)
        raise

def send_whatsapp(to_number: str, message: str):
    """Envía un mensaje a través de Evolution API."""
    try:
        # Configura el endpoint y los headers aquí
        endpoint = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_API_INSTANCE}"
        headers = {
            "Content-Type": "application/json",
            "apikey": settings.EVOLUTION_API_KEY,
        }

        message_ready = message.replace("+", "") 
        print(f"Enviando mensaje a {to_number} vía Evolution API: {message_ready}", flush=True)

        # Configura el payload
        body = {
            "number": to_number,
            "text": f"{message_ready}.s.whatsapp.net",
        }

        # Realiza la petición POST
        response = requests.post(endpoint, json=body, headers=headers)
        response.raise_for_status()

        print(f"Mensaje enviado a {to_number} vía Evolution API. Response: {response.json()}", flush=True)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje a {to_number} vía Evolution API: {e}", flush=True)
        raise
    except Exception as e:
        print(f"Error al enviar WhatsApp a {to_number}: {e}", flush=True)
from twilio.rest import Client
from core.config import settings # (En tu código ya está importado así, es correcto)

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
    """Envía un mensaje de WhatsApp."""
    try:
        # CAMBIO: WhatsApp también usa el número con capacidad de mensajería
        from_whatsapp_number = f'whatsapp:{settings.TWILIO_SMS_NUMBER}'
        to_whatsapp_number = f'whatsapp:{to_number}'
        
        message = client.messages.create(
            body=message,
            from_=from_whatsapp_number,
            to=to_whatsapp_number
        )
        print(f"WhatsApp enviado a {to_number} desde {settings.TWILIO_SMS_NUMBER}. SID: {message.sid}", flush=True)
        return message.sid
    except Exception as e:
        print(f"Error al enviar WhatsApp a {to_number}: {e}", flush=True)
        raise
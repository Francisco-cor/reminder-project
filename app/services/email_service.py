import msal
import requests
from core.config import settings

# La URL de la autoridad de Microsoft para obtener tokens
AUTHORITY = f"https://login.microsoftonline.com/{settings.OUTLOOK_TENANT_ID}"
# El "alcance" o permiso que solicitamos. '.default' usa los permisos asignados en Azure.
SCOPE = ["https://graph.microsoft.com/.default"]

# Creamos una instancia de la aplicación cliente confidencial.
# Podemos reutilizar esta instancia.
msal_app = msal.ConfidentialClientApplication(
    client_id=settings.OUTLOOK_CLIENT_ID,
    authority=AUTHORITY,
    client_credential=settings.OUTLOOK_CLIENT_SECRET,
)

def _get_access_token():
    """
    Función privada para obtener o refrescar un token de acceso.
    MSAL maneja el caché internamente.
    """
    result = msal_app.acquire_token_silent(scopes=SCOPE, account=None)
    
    if not result:
        print("No se encontró un token en caché, solicitando uno nuevo...")
        result = msal_app.acquire_token_for_client(scopes=SCOPE)
    
    if "access_token" in result:
        return result['access_token']
    else:
        print("Error al adquirir el token:", result.get("error_description"))
        raise Exception("No se pudo obtener el token de acceso para Microsoft Graph.")

def send_email(to_email: str, subject: str, body: str):
    """
    Envía un correo electrónico usando la API de Microsoft Graph.
    """
    access_token = _get_access_token()
    
    # Endpoint de la API de Graph para enviar correos desde la cuenta del usuario especificado
    url = f"https://graph.microsoft.com/v1.0/users/{settings.OUTLOOK_SENDER_EMAIL}/sendMail"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # El cuerpo del correo en el formato que espera la API de Graph
    email_payload = {
        'message': {
            'subject': subject,
            'body': {
                'contentType': 'HTML', # Puedes usar 'Text' o 'HTML'
                'content': body
            },
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': to_email
                    }
                }
            ]
        },
        'saveToSentItems': 'true'
    }
    
    try:
        response = requests.post(url, headers=headers, json=email_payload)
        # Esto lanzará un error si la solicitud falla (ej. 400, 401, 500)
        response.raise_for_status() 
        print(f"Correo enviado exitosamente a {to_email}. Estado: {response.status_code}")
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP al enviar correo a {to_email}: {e}")
        # Imprimimos el cuerpo del error para más detalles
        print(f"Cuerpo de la respuesta de error: {e.response.text}")
        raise
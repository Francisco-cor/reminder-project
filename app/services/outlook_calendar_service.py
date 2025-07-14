import msal
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from core.config import settings
from .email_service import _get_access_token, send_email

# La URL base de Microsoft Graph
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

def create_outlook_event(
    subject: str,
    body: str,
    start_time: datetime,
    end_time: datetime,
    attendees: Optional[List[str]] = None,
    location: Optional[str] = None,
    is_online_meeting: bool = False,
    reminder_minutes_before_start: int = 15,
    categories: Optional[List[str]] = None,
    importance: str = "normal",  # low, normal, high
    send_response: bool = True
) -> Dict[str, Any]:
    """
    Crea un evento en el calendario de Outlook usando Microsoft Graph API.
    
    Args:
        subject: Asunto del evento
        body: Descripción del evento
        start_time: Fecha y hora de inicio
        end_time: Fecha y hora de fin
        attendees: Lista de emails de los asistentes
        location: Ubicación del evento
        is_online_meeting: Si crear una reunión de Teams
        reminder_minutes_before_start: Minutos antes para el recordatorio
        categories: Categorías del evento
        importance: Importancia del evento
        send_response: Si enviar invitaciones a los asistentes
    
    Returns:
        Dict con la información del evento creado
    """
    access_token = _get_access_token()
    
    # Endpoint para crear eventos
    url = f"{GRAPH_API_BASE}/users/{settings.OUTLOOK_SENDER_EMAIL}/events"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Construir el cuerpo del evento
    event_payload = {
        "subject": subject,
        "body": {
            "contentType": "HTML",
            "content": body
        },
        "start": {
            "dateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "America/Mexico_City"
        },
        "end": {
            "dateTime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "America/Mexico_City"
        },
        "reminderMinutesBeforeStart": reminder_minutes_before_start,
        "isReminderOn": True,
        "importance": importance,
        "responseRequested": send_response
    }
    
    # Agregar ubicación si se proporciona
    if location:
        event_payload["location"] = {
            "displayName": location
        }
    
    # Agregar asistentes si se proporcionan
    if attendees:
        event_payload["attendees"] = [
            {
                "emailAddress": {
                    "address": email,
                    "name": email.split('@')[0]  # Usar la parte antes del @ como nombre
                },
                "type": "required"
            } for email in attendees
        ]
    
    # Agregar categorías si se proporcionan
    if categories:
        event_payload["categories"] = categories
    
    # Si es reunión online, agregar configuración de Teams
    if is_online_meeting:
        event_payload["isOnlineMeeting"] = True
        event_payload["onlineMeetingProvider"] = "teamsForBusiness"
    
    try:
        response = requests.post(url, headers=headers, json=event_payload)
        response.raise_for_status()
        
        event_data = response.json()
        print(f"Evento de Outlook creado exitosamente: {event_data.get('webLink')}")
        
        # Si hay asistentes y se debe enviar respuesta, enviar las invitaciones
        if attendees and send_response:
            send_event_invitations(event_data['id'])
        
        return event_data
        
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP al crear evento en Outlook: {e}")
        print(f"Respuesta de error: {e.response.text}")
        raise

def send_event_invitations(event_id: str):
    """
    Envía las invitaciones del evento a los asistentes.
    """
    access_token = _get_access_token()
    
    url = f"{GRAPH_API_BASE}/users/{settings.OUTLOOK_SENDER_EMAIL}/events/{event_id}/send"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Length': '0'
    }
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        print("Invitaciones enviadas exitosamente")
    except requests.exceptions.HTTPError as e:
        print(f"Error al enviar invitaciones: {e}")
        print(f"Respuesta de error: {e.response.text}")

def update_outlook_event(
    event_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Actualiza un evento existente en Outlook.
    
    Args:
        event_id: ID del evento a actualizar
        **kwargs: Campos a actualizar
    
    Returns:
        Dict con la información del evento actualizado
    """
    access_token = _get_access_token()
    
    url = f"{GRAPH_API_BASE}/users/{settings.OUTLOOK_SENDER_EMAIL}/events/{event_id}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Construir el payload con los campos a actualizar
    update_payload = {}
    
    if 'subject' in kwargs:
        update_payload['subject'] = kwargs['subject']
    if 'body' in kwargs:
        update_payload['body'] = {
            "contentType": "HTML",
            "content": kwargs['body']
        }
    if 'start_time' in kwargs:
        update_payload['start'] = {
            "dateTime": kwargs['start_time'].strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "America/Mexico_City"
        }
    if 'end_time' in kwargs:
        update_payload['end'] = {
            "dateTime": kwargs['end_time'].strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "America/Mexico_City"
        }
    if 'location' in kwargs:
        update_payload['location'] = {
            "displayName": kwargs['location']
        }
    if 'attendees' in kwargs:
        update_payload['attendees'] = [
            {
                "emailAddress": {
                    "address": email,
                    "name": email.split('@')[0]
                },
                "type": "required"
            } for email in kwargs['attendees']
        ]
    
    try:
        response = requests.patch(url, headers=headers, json=update_payload)
        response.raise_for_status()
        
        event_data = response.json()
        print(f"Evento actualizado exitosamente: {event_data.get('webLink')}")
        return event_data
        
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP al actualizar evento: {e}")
        print(f"Respuesta de error: {e.response.text}")
        raise

def delete_outlook_event(
    event_id: str,
    send_cancellation: bool = True
) -> bool:
    """
    Elimina (cancela) un evento de Outlook.
    
    Args:
        event_id: ID del evento a eliminar
        send_cancellation: Si enviar notificación de cancelación a los asistentes
    
    Returns:
        True si se eliminó exitosamente
    """
    access_token = _get_access_token()
    
    if send_cancellation:
        # Primero cancelar el evento (esto envía notificaciones)
        cancel_url = f"{GRAPH_API_BASE}/users/{settings.OUTLOOK_SENDER_EMAIL}/events/{event_id}/cancel"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        cancel_payload = {
            "comment": "Este evento ha sido cancelado."
        }
        
        try:
            response = requests.post(cancel_url, headers=headers, json=cancel_payload)
            response.raise_for_status()
            print(f"Evento {event_id} cancelado y notificaciones enviadas")
        except requests.exceptions.HTTPError as e:
            print(f"Error al cancelar evento: {e}")
            print(f"Respuesta de error: {e.response.text}")
    
    # Luego eliminar el evento
    delete_url = f"{GRAPH_API_BASE}/users/{settings.OUTLOOK_SENDER_EMAIL}/events/{event_id}"
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.delete(delete_url, headers=headers)
        response.raise_for_status()
        print(f"Evento {event_id} eliminado exitosamente")
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP al eliminar evento: {e}")
        print(f"Respuesta de error: {e.response.text}")
        raise

def get_outlook_event(event_id: str) -> Dict[str, Any]:
    """
    Obtiene un evento específico de Outlook.
    
    Args:
        event_id: ID del evento
    
    Returns:
        Dict con la información del evento
    """
    access_token = _get_access_token()
    
    url = f"{GRAPH_API_BASE}/users/{settings.OUTLOOK_SENDER_EMAIL}/events/{event_id}"
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP al obtener evento: {e}")
        print(f"Respuesta de error: {e.response.text}")
        raise

def list_outlook_events(
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    top: int = 10,
    search: Optional[str] = None,
    order_by: str = "start/dateTime"
) -> List[Dict[str, Any]]:
    """
    Lista eventos del calendario de Outlook.
    
    Args:
        start_datetime: Fecha/hora de inicio para filtrar
        end_datetime: Fecha/hora de fin para filtrar
        top: Número máximo de resultados
        search: Texto de búsqueda
        order_by: Campo para ordenar resultados
    
    Returns:
        Lista de eventos
    """
    access_token = _get_access_token()
    
    url = f"{GRAPH_API_BASE}/users/{settings.OUTLOOK_SENDER_EMAIL}/events"
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Construir parámetros de consulta
    params = {
        "$top": top,
        "$orderby": order_by
    }
    
    # Agregar filtros de fecha si se proporcionan
    filters = []
    if start_datetime:
        filters.append(f"start/dateTime ge '{start_datetime.strftime('%Y-%m-%dT%H:%M:%S')}'")
    if end_datetime:
        filters.append(f"end/dateTime le '{end_datetime.strftime('%Y-%m-%dT%H:%M:%S')}'")
    
    if filters:
        params["$filter"] = " and ".join(filters)
    
    # Agregar búsqueda si se proporciona
    if search:
        params["$search"] = f'"{search}"'
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('value', [])
        
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP al listar eventos: {e}")
        print(f"Respuesta de error: {e.response.text}")
        raise

def create_outlook_event_with_email(
    subject: str,
    body: str,
    start_time: datetime,
    end_time: datetime,
    attendees: List[str],
    location: Optional[str] = None,
    is_online_meeting: bool = False,
    additional_email_content: Optional[str] = None,
    categories: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Crea un evento en Outlook y envía un correo personalizado adicional a los asistentes.
    
    Args:
        subject: Asunto del evento
        body: Descripción del evento
        start_time: Fecha y hora de inicio
        end_time: Fecha y hora de fin
        attendees: Lista de emails de los asistentes
        location: Ubicación del evento
        is_online_meeting: Si crear una reunión de Teams
        additional_email_content: Contenido adicional para el correo
        categories: Categorías del evento
    
    Returns:
        Dict con la información del evento creado
    """
    try:
        # Crear el evento en Outlook
        event = create_outlook_event(
            subject=subject,
            body=body,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
            location=location,
            is_online_meeting=is_online_meeting,
            reminder_minutes_before_start=30,
            categories=categories,
            send_response=True
        )
        
        # Preparar el cuerpo del correo adicional
        email_body = f"""
        <h2>Nuevo evento agendado: {subject}</h2>
        
        <p><strong>Fecha y hora:</strong> {start_time.strftime('%d/%m/%Y %H:%M')} - {end_time.strftime('%H:%M')}</p>
        <p><strong>Descripción:</strong></p>
        <div style="margin-left: 20px;">{body}</div>
        """
        
        if location:
            email_body += f"<p><strong>Ubicación:</strong> {location}</p>"
        
        if is_online_meeting and event.get('onlineMeeting'):
            join_url = event['onlineMeeting'].get('joinUrl', '')
            if join_url:
                email_body += f'<p><strong>Unirse a la reunión:</strong> <a href="{join_url}">Click aquí para unirse a Teams</a></p>'
        
        if additional_email_content:
            email_body += f"<br/><h3>Información adicional:</h3>{additional_email_content}"
        
        email_body += f"""
        <br/>
        <p>Se ha agregado este evento a tu calendario de Outlook. Recibirás un recordatorio 30 minutos antes del evento.</p>
        <p><a href="{event.get('webLink')}">Ver evento en Outlook</a></p>
        """
        
        # Enviar correo personalizado a cada asistente
        for attendee_email in attendees:
            try:
                send_email(
                    to_email=attendee_email,
                    subject=f"Confirmación: {subject}",
                    body=email_body
                )
                print(f"Correo adicional enviado a {attendee_email}")
            except Exception as e:
                print(f"Error al enviar correo adicional a {attendee_email}: {e}")
                # Continuar con los demás asistentes aunque falle uno
        
        return event
        
    except Exception as e:
        print(f"Error al crear evento con notificación: {e}")
        raise

def get_free_busy_schedule(
    emails: List[str],
    start_time: datetime,
    end_time: datetime,
    interval_minutes: int = 30
) -> Dict[str, Any]:
    """
    Obtiene la disponibilidad (libre/ocupado) de múltiples usuarios.
    
    Args:
        emails: Lista de emails para verificar disponibilidad
        start_time: Inicio del período a verificar
        end_time: Fin del período a verificar
        interval_minutes: Duración de los intervalos en minutos
    
    Returns:
        Dict con la información de disponibilidad
    """
    access_token = _get_access_token()
    
    url = f"{GRAPH_API_BASE}/users/{settings.OUTLOOK_SENDER_EMAIL}/calendar/getSchedule"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "schedules": emails,
        "startTime": {
            "dateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "America/Mexico_City"
        },
        "endTime": {
            "dateTime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "America/Mexico_City"
        },
        "availabilityViewInterval": interval_minutes
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP al obtener disponibilidad: {e}")
        print(f"Respuesta de error: {e.response.text}")
        raise
import os
import json
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from core.config import settings
from typing import Optional, Dict, Any, List

# Configuración de credenciales de Google
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Crea y retorna un servicio de Google Calendar autenticado.
    """
    try:
        # Cargar las credenciales desde el archivo JSON
        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_CREDENTIALS_JSON,
            scopes=SCOPES
        )
        
        # Construir el servicio
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error al crear el servicio de Google Calendar: {e}")
        raise

def create_event(
    summary: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    attendees: Optional[List[str]] = None,
    location: Optional[str] = None,
    calendar_id: str = 'primary',
    send_notifications: bool = True,
    reminder_minutes: Optional[List[int]] = None,
    timezone: str = "UTC"
) -> Dict[str, Any]:
    """
    Crea un evento en Google Calendar.
    
    Args:
        summary: Título del evento
        description: Descripción del evento
        start_time: Fecha y hora de inicio
        end_time: Fecha y hora de fin
        attendees: Lista de emails de los asistentes
        location: Ubicación del evento
        calendar_id: ID del calendario (por defecto 'primary')
        send_notifications: Si enviar notificaciones a los asistentes
        reminder_minutes: Lista de minutos antes del evento para recordatorios
        timezone: Zona horaria del evento
    
    Returns:
        Dict con la información del evento creado
    """
    try:
        service = get_calendar_service()
        
        # Construir el cuerpo del evento
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': timezone,
            },
        }
        
        # Agregar ubicación si se proporciona
        if location:
            event['location'] = location
        
        # Agregar asistentes si se proporcionan
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        # Agregar recordatorios
        if reminder_minutes:
            event['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': minutes} for minutes in reminder_minutes
                ] + [
                    {'method': 'popup', 'minutes': minutes} for minutes in reminder_minutes
                ]
            }
        else:
            event['reminders'] = {'useDefault': True}
        
        # Crear el evento
        event_result = service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendNotifications=send_notifications
        ).execute()
        
        print(f"Evento creado exitosamente: {event_result.get('htmlLink')}")
        return event_result
        
    except HttpError as error:
        print(f"Error HTTP al crear evento: {error}")
        raise
    except Exception as e:
        print(f"Error al crear evento: {e}")
        raise

def update_event(
    event_id: str,
    calendar_id: str = 'primary',
    **kwargs
) -> Dict[str, Any]:
    """
    Actualiza un evento existente en Google Calendar.
    
    Args:
        event_id: ID del evento a actualizar
        calendar_id: ID del calendario
        **kwargs: Campos a actualizar (summary, description, start_time, end_time, etc.)
    
    Returns:
        Dict con la información del evento actualizado
    """
    try:
        service = get_calendar_service()
        
        # Obtener el evento actual
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        # Actualizar campos proporcionados
        if 'summary' in kwargs:
            event['summary'] = kwargs['summary']
        if 'description' in kwargs:
            event['description'] = kwargs['description']
        if 'location' in kwargs:
            event['location'] = kwargs['location']
        
        timezone = kwargs.get("timezone", "UTC")
        if 'start_time' in kwargs:
            event['start'] = {
                'dateTime': kwargs['start_time'].isoformat(),
                'timeZone': timezone,
            }
        if 'end_time' in kwargs:
            event['end'] = {
                'dateTime': kwargs['end_time'].isoformat(),
                'timeZone': timezone,
            }
        if 'attendees' in kwargs:
            event['attendees'] = [{'email': email} for email in kwargs['attendees']]
        
        # Actualizar el evento
        updated_event = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event,
            sendNotifications=kwargs.get('send_notifications', True)
        ).execute()
        
        print(f"Evento actualizado exitosamente: {updated_event.get('htmlLink')}")
        return updated_event
        
    except HttpError as error:
        print(f"Error HTTP al actualizar evento: {error}")
        raise
    except Exception as e:
        print(f"Error al actualizar evento: {e}")
        raise

def delete_event(
    event_id: str,
    calendar_id: str = 'primary',
    send_notifications: bool = True
) -> bool:
    """
    Elimina un evento de Google Calendar.
    
    Args:
        event_id: ID del evento a eliminar
        calendar_id: ID del calendario
        send_notifications: Si enviar notificaciones a los asistentes
    
    Returns:
        True si se eliminó exitosamente
    """
    try:
        service = get_calendar_service()
        
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendUpdates='all' if send_notifications else 'none'
        ).execute()
        
        print(f"Evento {event_id} eliminado exitosamente")
        return True
        
    except HttpError as error:
        print(f"Error HTTP al eliminar evento: {error}")
        raise
    except Exception as e:
        print(f"Error al eliminar evento: {e}")
        raise

def get_event(
    event_id: str,
    calendar_id: str = 'primary'
) -> Dict[str, Any]:
    """
    Obtiene un evento específico de Google Calendar.
    
    Args:
        event_id: ID del evento
        calendar_id: ID del calendario
    
    Returns:
        Dict con la información del evento
    """
    try:
        service = get_calendar_service()
        
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        return event
        
    except HttpError as error:
        print(f"Error HTTP al obtener evento: {error}")
        raise
    except Exception as e:
        print(f"Error al obtener evento: {e}")
        raise

def list_events(
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None,
    max_results: int = 10,
    calendar_id: str = 'primary',
    query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Lista eventos de Google Calendar.
    
    Args:
        time_min: Fecha/hora mínima para filtrar eventos
        time_max: Fecha/hora máxima para filtrar eventos
        max_results: Número máximo de resultados
        calendar_id: ID del calendario
        query: Texto de búsqueda
    
    Returns:
        Lista de eventos
    """
    try:
        service = get_calendar_service()
        
        # Si no se proporciona time_min, usar ahora
        if not time_min:
            time_min = datetime.utcnow()
        
        # Preparar parámetros de la consulta
        params = {
            'calendarId': calendar_id,
            'timeMin': time_min.isoformat() + 'Z',
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        if time_max:
            params['timeMax'] = time_max.isoformat() + 'Z'
        
        if query:
            params['q'] = query
        
        # Ejecutar consulta
        events_result = service.events().list(**params).execute()
        events = events_result.get('items', [])
        
        return events
        
    except HttpError as error:
        print(f"Error HTTP al listar eventos: {error}")
        raise
    except Exception as e:
        print(f"Error al listar eventos: {e}")
        raise


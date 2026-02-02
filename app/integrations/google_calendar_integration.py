import os
import datetime
import calendar
import dateutil.parser
import dateutil.tz
from pathlib import Path
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = Path(__file__).resolve().parent.parent.parent

CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials', 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'credentials', 'token.json')

def get_calendar_service():
    """Autentica o usuário usando OAuth 2.0 e retorna o serviço do Calendar."""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Renovando token expirado...")
            creds.refresh(Request())
        else:
            print("Iniciando fluxo de login no navegador...")
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"Arquivo não encontrado: {CREDENTIALS_FILE}. Baixe o OAuth Client ID do Google Cloud.")
                
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print(f"Token salvo em: {TOKEN_FILE}")

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_free_busy_slots() -> list:
    """Consulta os horários ocupados na agenda."""
    service = get_calendar_service()
    calendar_id = 'primary'

    tz_brasilia = dateutil.tz.gettz('America/Sao_Paulo')
    now = datetime.now(tz_brasilia)

    # Lógica para pegar até o fim do próximo mês
    if now.month == 12:
        next_month = 1
        year = now.year + 1
    else:
        next_month = now.month + 1
        year = now.year

    last_day = calendar.monthrange(year, next_month)[1]
    end_date = datetime(year, next_month, last_day, 23, 59, 59, tzinfo=tz_brasilia)

    body = {
        "timeMin": now.astimezone(dateutil.tz.UTC).isoformat().replace('+00:00', 'Z'),
        "timeMax": end_date.astimezone(dateutil.tz.UTC).isoformat().replace('+00:00', 'Z'),
        "items": [{"id": calendar_id}]
    }

    try:
        freebusy_result = service.freebusy().query(body=body).execute()
        busy_slots_raw = freebusy_result['calendars'][calendar_id]['busy']

        formatted_slots = []

        print(f"\n--- Horários Ocupados Detectados ---")
        for slot in busy_slots_raw:
            start_utc = dateutil.parser.isoparse(slot['start'])
            end_utc = dateutil.parser.isoparse(slot['end'])

            start_br = start_utc.astimezone(tz_brasilia)
            end_br = end_utc.astimezone(tz_brasilia)

            slot_data = {
                "data": start_br.strftime('%Y-%m-%d'),
                "hora_inicio": start_br.strftime('%H:%M'),
                "hora_fim": end_br.strftime('%H:%M')
            }
            formatted_slots.append(slot_data)
            print(f"Dia: {slot_data['data']} | {slot_data['hora_inicio']} - {slot_data['hora_fim']}")

        return formatted_slots

    except Exception as e:
        print(f"Erro ao consultar disponibilidade: {e}")
        return None

def get_available_slots():
    """Gera lista de horários livres baseada na ocupação."""
    busy_slots = get_free_busy_slots()
    if busy_slots is None:
        return []

    tz_brasilia = dateutil.tz.gettz('America/Sao_Paulo')

    START_HOUR = 9
    END_HOUR = 19
    
    now = datetime.now(tz_brasilia)
    
    # Define data limite (fim do próximo mês)
    if now.month == 12:
        end_date = datetime(now.year + 1, 1, calendar.monthrange(now.year + 1, 1)[1])
    else:
        end_date = datetime(now.year, now.month + 1, calendar.monthrange(now.year, now.month + 1)[1])

    available_days = []
    current_day = now.date() + timedelta(days=1)

    while current_day <= end_date.date():
        # Ignora finais de semana (5=Sábado, 6=Domingo)
        if current_day.weekday() >= 5:
            current_day += timedelta(days=1)
            continue

        day_slots = []
        for hour in range(START_HOUR, END_HOUR):
            slot_time = f"{hour:02d}:00"

            # Verifica conflito
            is_busy = any(
                s['data'] == current_day.isoformat() and
                s['hora_inicio'] <= slot_time < s['hora_fim']
                for s in busy_slots
            )

            day_slots.append({
                "time": slot_time,
                "available": not is_busy
            })

        available_days.append({
            "date": current_day.isoformat(),
            "slots": day_slots
        })

        current_day += timedelta(days=1)

    return available_days

def create_event(summary: str, description: str, start_time: datetime, lead_email: str, lead_name: str, duration_hours: int = 1) -> dict:
    """
    Cria evento com Google Meet e convida o participante via OAuth 2.0.
    """
    service = get_calendar_service()
    calendar_id = 'primary'

    print(f"\nCriando evento: {summary} em {start_time}")

    end_time = start_time + timedelta(hours=duration_hours)

    event_body = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'conferenceData': {
            'createRequest': {
                'requestId': f"meet-{int(datetime.now().timestamp())}",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            },
        },
        'attendees': [
            {'email': lead_email, 'displayName': lead_name}
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    try:
        event = service.events().insert(
            calendarId=calendar_id, 
            body=event_body, 
            conferenceDataVersion=1,
            sendUpdates='all'
        ).execute()

        meet_link = event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', 'Link não gerado')
        
        print(f"✅ Evento criado com sucesso!")
        print(f"🔗 Link do evento: {event.get('htmlLink')}")
        print(f"📹 Google Meet: {meet_link}")
        
        return event
    except Exception as e:
        print(f"❌ Erro ao criar evento: {e}")
        return None

# --- BLOCO DE TESTE ---
if __name__ == "__main__":
    # Teste simples ao rodar o arquivo
    
    # 1. Verificar slots (isso vai disparar a autenticação na primeira vez)
    slots = get_available_slots()
    
    # 2. Exemplo de criação de reunião
    tz = dateutil.tz.gettz('America/Sao_Paulo')
    
    # Marca para amanhã às 10h
    amanha = datetime.now(tz) + timedelta(days=1)
    inicio_reuniao = amanha.replace(hour=10, minute=0, second=0, microsecond=0)
    
    create_event(
        summary="Reunião de Diagnóstico",
        description="Conversa sobre automação.",
        start_time=inicio_reuniao,
        lead_email="carloserico71@gmail.com", # Troque para testar
        lead_name="Cliente Teste"
    )
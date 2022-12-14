import logging
import os
from flask import Flask
from flask_ask import Ask, request, session, question, statement
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from utils.nextcloud_calendar import list_events
from dateutil.parser import parse
from utils.nextcloud_notes import get_notes_summary, get_single_note, create_note
from utils.nextcloud_tasks import get_task_summary, create_task

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)
load_dotenv()


@ask.launch
def launch():
    speech_text = "Welcome to the Alexa Skills Kit, you can say hello"
    return (
        question(speech_text)
        .reprompt(speech_text)
        .simple_card("HelloWorld", speech_text)
    )


@ask.intent("HelloWorldIntent")
def hello_world():
    speech_text = "Hello world"
    return statement(speech_text).simple_card("HelloWorld", speech_text)


@ask.intent("AMAZON.HelpIntent")
def help():
    speech_text = "You can say hello to me!"
    return (
        question(speech_text)
        .reprompt(speech_text)
        .simple_card("HelloWorld", speech_text)
    )


@ask.session_ended
def session_ended():
    return "{}", 200


# Implementations
@ask.intent("ListCalendarIntent", default={"event_date": ""})
def list_calendar_intent(event_date):
    if not event_date:
        event_date = datetime.now(tzinfo=timezone(timedelta(hours=-3))).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        event_date = parse(event_date).replace(tzinfo=timezone.utc)

    end_date = event_date + timedelta(days=1)

    events = list_events(event_date, end_date)
    speech_text = f"Seus eventos de {str(event_date.date())} são: {events}"

    return statement(speech_text).simple_card("Eventos Calendário", speech_text)


@ask.intent("CreateCalendarIntent", default={"event_query": "Sem descrição"})
def create_calendar_intent(event_query):
    speech_text = f"Criado evento {event_query}"
    return statement(speech_text).simple_card("CreateCalendarIntent", speech_text)


# Done
@ask.intent("ListTasksIntent")
def list_tasks_intent():
    speech_text = f"Suas próximas 5 tarefas são: {get_task_summary()}."
    return statement(speech_text).simple_card("Lista de tarefas", speech_text)


@ask.intent("FinishTaskIntent", default={"task_name": "Sem descrição"})
def finish_task_intent(task_name):
    speech_text = f"Finalizando tarefa {task_name}"
    return statement(speech_text).simple_card("FinishTaskIntent", speech_text)


# Done
@ask.intent("CreateTaskIntent", default={"task_name": "Sem descrição"})
def create_calendar_intent(task_name):
    create_task(task_name)
    speech_text = f"Criado tarefa {task_name}"
    return statement(speech_text).simple_card("Criar Tarefa", speech_text)


# Done
@ask.intent("ListNotesIntent")
def list_tasks_intent():
    speech_text = f"Suas primeiras 5 notas são: {get_notes_summary()}. Peça para ler uma nota para detalhes."
    return statement(speech_text).simple_card("Lista de notas", speech_text)


# Done
@ask.intent("ReadNoteIntent", default={"note_name": ""})
def read_note_intent(note_name):
    speech_text = get_single_note(note_name)
    return statement(speech_text).simple_card("Nota", speech_text)


# Done
@ask.intent("CreateNoteIntent", default={"note_content": "Sem descrição"})
def create_note_intent(note_content):
    create_note(note_content)
    speech_text = "Nota criada!"
    return statement(speech_text).simple_card("Criar Nota", speech_text)


# if __name__ == '__main__':
#     if 'ASK_VERIFY_REQUESTS' in os.environ:
#         verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
#         if verify == 'false':
#             app.config['ASK_VERIFY_REQUESTS'] = False
#     app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

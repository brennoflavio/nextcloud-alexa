import logging
import os
from flask import Flask
from flask_ask import Ask, request, session, question, statement
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from utils.nextcloud_calendar import list_events
from dateutil.parser import parse

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


@ask.intent("ListTasksIntent")
def list_tasks_intent():
    speech_text = (
        f"Suas próximas 5 tarefas são: comprar café, dentista e fazer caminhada."
    )
    return statement(speech_text).simple_card("ListTasksIntent", speech_text)


@ask.intent("FinishTaskIntent", default={"task_name": "Sem descrição"})
def finish_task_intent(task_name):
    speech_text = f"Finalizando tarefa {task_name}"
    return statement(speech_text).simple_card("FinishTaskIntent", speech_text)


@ask.intent("CreateTaskIntent", default={"task_name": "Sem descrição"})
def create_calendar_intent(task_name):
    speech_text = f"Criado tarefa {task_name}"
    return statement(speech_text).simple_card("CreateTaskIntent", speech_text)


# if __name__ == '__main__':
#     if 'ASK_VERIFY_REQUESTS' in os.environ:
#         verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
#         if verify == 'false':
#             app.config['ASK_VERIFY_REQUESTS'] = False
#     app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

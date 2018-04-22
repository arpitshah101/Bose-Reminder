import json, os
from flask import Flask, render_template, send_file
from watson_developer_cloud import TextToSpeechV1

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime, dateutil.parser

app = Flask(__name__)

events = []

# Setup the Calendar API
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
store = file.Storage('../credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('../client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

def get_calendar_events():
    # Call the Calendar API
    global events
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 3 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=3, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(json.dumps(events))
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def load_events():
    global events
    with open('../events.json') as eventsfile:
        events = json.load(eventsfile)

def generate_notification_text():
    output = ""
    output += "Sorry to interrupt, but you have the following 3 events coming up: "
    for i in range(0, len(events) - 1):
        if 'date' in events[i]['start']:
            d = dateutil.parser.parse(events[i]['start']['date'])
        else:
            d = dateutil.parser.parse(events[i]['start']['dateTime'])
        # print(d.strftime(events[i]['summary'] + " on %B %d, %Y at %I:%M %p, "))
        output += d.strftime(events[i]['summary'] + " at %I:%M %p, ")
        # print('\n')
        # if 'reminders' in events[i].keys() and 'overrides' in events[i]['reminders'].keys():
            # print("Remind " + str(events[i]['reminders']['overrides'][1]['minutes']) + " minutes before " + d.strftime("%I:%M %p"))
            # print(d - datetime.timedelta(minutes=events[i]['reminders']['overrides'][1]['minutes']))
        # else:
            # print("Remind 10 minutes before " + d.strftime("%I:%M %p"))
            # print(d - datetime.timedelta(minutes=10))
        # print('\n')
    if len(events) > 1:
        output += " and " + d.strftime(events[-1]['summary'] + " at %I:%M %p. Good bye.")
    else:   
        if 'date' in events[0]['start']:
            d = dateutil.parser.parse(events[0]['start']['date'])
        else:
            d = dateutil.parser.parse(events[0]['start']['dateTime'])

        output += d.strftime(events[0]['summary'] + " at %I:%M %p. Good bye.")
    return output

@app.route("/update-events")
def update_events():
    # load_events()
    get_calendar_events()
    output = generate_notification_text()
    # output = "Test"
    print(output)
    file_path = text_to_speech(text=output, file_path="./notifications/notification.mp3")
    print("sending command to api")

    os.system("curl -v -d \"<play_info><app_key>[INSERT API KEY HERE]</app_key><url>http://192.168.1.112:3000/notification.mp3</url><service>Bose Remind</service><reason>reason text</reason><message>" + output + "</message><volume>68</volume></play_info>\" http://192.168.1.16:8090/speaker")
    return output

@app.route("/")
def main():
    # return render_template('index.html')
    return "Please use /update-events to trigger notification"

def text_to_speech(text=None, file_path=None):
    if text is None:
        raise Exception("No text input")
    try:
        with open('../ibm-auth.json') as authfile:
            auth_data = json.load(authfile)
            username = auth_data['tts']['username']
            password = auth_data['tts']['password']
        print("Read auth file")
    except:
        raise
    tts = TextToSpeechV1(
        username=username,
        password=password
    )
    voice = 'en-US_AllisonVoice'
    accept = 'audio/mpeg'
    outdir = os.path.dirname(file_path)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    print("Requesting audio...")
    with open(file_path, 'wb') as audio_file:
        audio_file.write(
            tts.synthesize(
                text, voice=voice, accept=accept
            ).content
        )
    print("Wrote file successfully")
    return file_path

@app.route('/notification/<notification_file>')
def get_sound_file(notification_file):
    try:
        return send_file('./notifications/' + notification_file)
    except Exception as e:
        return str(e)

@app.route('/getspeech')
def generate_speech():
    try:
        # result_path = text_to_speech(text="Hi", file_path="./notifications/test.mp3")
        # print("Created file at:", result_path)
        print("WARNING: Disabled the route for now")
    except Exception as e:
        print("Error:", e)
    return ""

if __name__ == "__main__":
    print("Running application now :)")
    app.run('0.0.0.0')
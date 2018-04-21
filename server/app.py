import json, os
from flask import Flask, render_template, send_file
from watson_developer_cloud import TextToSpeechV1

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

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
    accept = 'audio/mp3'
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

@app.route('/get-soundfile/<notification_file>')
def get_sound_file(notification_file):
    try:
        return send_file('./notifications/' + notification_file + '.mp3', attachment_filename = notification_file + '.mp3')
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
    app.run()
from flask import Flask, render_template, send_file

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/get-soundfile/<notification_file>')
def get_sound_file(notification_file):
    try:
        return send_file('./notifications/' + notification_file + '.mp3', attachment_filename = notification_file + '.mp3')
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    print("Running application now :)")
    app.run()
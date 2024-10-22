from twilio.twiml.voice_response import VoiceResponse
from flask import Flask, Response, request, jsonify, send_from_directory, abort
import requests, time, os
from datetime import datetime
from dotenv import load_dotenv
import threading
import asyncio

app = Flask(__name__)
UPLOAD_FOLDER = 'media'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

load_dotenv()

host = os.getenv('HOST')


@app.route("/handler-outgoing-call", methods=['POST', 'GET'])
def voice_audio_file():
    audio_url = f"{host}/download/mp3-output-ttsfree(dot)com.mp3"
    response = VoiceResponse()
    response.play(audio_url)
    response.record(max_length=10, timeout=1, action="/handle-recording",
                    recording_status_callback="/recording-status",
                    method="POST")

    # response.say("Thank you for your confirmation, goodbye.", voice='female')
    response.hangup()
    return str(response)


@app.route("/handle-recording", methods=['POST'])
def handle_recording():
    recording_url = request.form['RecordingUrl']
    recording_url_mp3 = f"{recording_url}.mp3"
    time.sleep(10)  # waiting for file response

    response = requests.get(recording_url_mp3,
                            auth=(os.getenv('SID'), os.getenv('TOKEN')))
    file_name = f'media/records/recording{str(datetime.now().strftime("%d%m%Y%H%M%S"))}.mp3'

    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)

        # wav_filename = convert_mp3_to_wav(file_name)
        #
        # transcript = transcribe_audio(wav_filename)
        from utils import process_recording
        transcript = process_recording(file_name)
        print(f"Transcription: {transcript}")
        response = VoiceResponse()
        if transcript is not False:
            # response.say(f"you say {transcript}", voice='male')
            if "yes" in transcript.lower():
                print("yes audio file play")
                audio_url = f"{host}/download/thanks.mp3"
            elif "no" in transcript.lower():
                print("no audio file play")
                audio_url = f"{host}/download/no_response.mp3"
            else:
                print("else audio file play")
                audio_url = f"{host}/download/others.mp3"
            response.play(audio_url)
        else:
            audio_url = f"{host}/download/not_transcript.mp3"
            response.play(audio_url)
            print("Sorry I could not understand you, please say again")
            response.record(max_length=8, timeout=5, action="/handle-recording",
                            recording_status_callback="/recording-status",
                            method="POST")
        response.hangup()
    else:
        print(f"Failed to download recording: {response.status_code}")

    return str(response)


@app.route("/exception", methods=['POST'])
def handle_error():
    print("exception", request.json)
    print("------------------------------------------")
    return {
        "status": "exception got"
    }



@app.route("/recording-status", methods=['POST'])
def recording_status():
    recording_sid = request.form['RecordingSid']
    recording_url = request.form['RecordingUrl']
    recording_statu = request.form['RecordingStatus']
    print(f"Recording {recording_sid} status: {recording_statu}")
    print(f"Recording available at: {recording_url}")

    return "Status received", 200


@app.route('/call-status', methods=['POST'])
def call_status():
    call_status = request.form.get('CallStatus')
    call_sid = request.form.get('CallSid')

    # Log or take action based on the status
    if call_status == 'no-answer':
        print(f"Call {call_sid} was not answered.")
    elif call_status == 'busy':
        print(f"Call {call_sid} found the line busy.")
    elif call_status == 'failed':
        print(f"Call {call_sid} failed to connect.")
    elif call_status == 'completed':
        print(f"Call {call_sid} was completed successfully.")

    return '', 200


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.isfile(file_path):
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    else:
        abort(404)


@app.route('/texml', methods=['GET', "POST"])
def get_texml():
    print("Request received")
    texml_content = """<?xml version="1.0" encoding="UTF-8"?>
  <!-- XML file setup above-->
 <!-- The Response element wraps the body and is required -->
<Response>
     <!-- You don't need to issue an answer command, start with Say for text to speech -->
    <Say>This is TeXML text to speech setup in seconds! The call will now hangup.</Say>
    <!-- For this example, you want to hangup the call otherwise there will be silence -->
    <Hangup />
</Response>"""

    # Return the TeXML response
    return Response(texml_content, mimetype='application/xml')


@app.route('/gather_response', methods=['POST'])
def gather_response():
    print("Gather response received")
    # Add logic to handle gathered input here
    response_content = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>Thank you for your input. Goodbye!</Say>
        <Hangup/>
    </Response>"""
    return Response(response_content, mimetype='application/xml')


if __name__ == "__main__":
    async def run_message_consumer():
        from main import kafka_message_consumer
        kafka_message_consumer()


    def loop_in_thread(loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_message_consumer())


    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # t = threading.Thread(target=loop_in_thread, args=(loop,))
    # t.start()

    app.run(debug=True, host="0.0.0.0", port=5000)

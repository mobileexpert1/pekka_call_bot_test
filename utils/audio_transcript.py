import subprocess
from pydub import AudioSegment
import speech_recognition as sr


def convert_mp3_to_wav(mp3_filename):
    wav_filename = mp3_filename.replace('.mp3', '.wav')
    command = f"ffmpeg -i {mp3_filename} {wav_filename}"
    subprocess.call(command, shell=True)
    return wav_filename


def transcribe_audio(wav_filename):
    recognizer = sr.Recognizer()

    # Open the WAV file for transcription
    with sr.AudioFile(wav_filename) as source:
        audio_data = recognizer.record(source)  # Read the entire audio file

    # Try recognizing the speech in the audio
    try:
        transcript = recognizer.recognize_google(audio_data)
        print(transcript)
        return transcript
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return False
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition; {e}")
        return False


def preprocess_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    audio = audio.normalize()

    processed_file = file_path.replace(".mp3", "_processed.wav")
    audio.export(processed_file, format="wav")

    return processed_file




from google.cloud import speech
import requests
import os
from pydub import AudioSegment
import noisereduce as nr
import numpy as np
import wave


def convert_mp3_to_wav(mp3_filename):
    audio = AudioSegment.from_mp3(mp3_filename)
    # Convert to mono
    audio = audio.set_channels(1)
    wav_filename = mp3_filename.replace('.mp3', '.wav')
    audio.export(wav_filename, format='wav')
    return wav_filename


def reduce_noise(wav_filename):
    audio = AudioSegment.from_wav(wav_filename)
    samples = np.array(audio.get_array_of_samples())
    reduced_noise = nr.reduce_noise(y=samples, sr=audio.frame_rate)
    cleaned_audio = AudioSegment(
        reduced_noise.tobytes(),
        frame_rate=audio.frame_rate,
        sample_width=audio.sample_width,
        channels=1  # Ensure it remains mono
    )
    cleaned_wav_filename = 'cleaned_audio.wav'
    cleaned_audio.export(cleaned_wav_filename, format='wav')
    return cleaned_wav_filename


def get_sample_rate(audio_file_path):
    with wave.open(audio_file_path, "rb") as wav_file:
        return wav_file.getframerate()


def transcribe_audio(wav_filename):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    service_account_key_path = os.path.join(BASE_DIR, "gcp_key.json")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key_path

    sample_rate = get_sample_rate(wav_filename)

    client = speech.SpeechClient()

    with open(wav_filename, 'rb') as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code='en-US',
        model='phone_call'
    )

    response = client.recognize(config=config, audio=audio)

    transcript = ' '.join([result.alternatives[0].transcript for result in response.results])
    return transcript


def process_recording(mp3_filename):
    wav_filename = convert_mp3_to_wav(mp3_filename)
    cleaned_wav_filename = reduce_noise(wav_filename)
    transcription = transcribe_audio(cleaned_wav_filename)
    if transcription:
        print(f"Transcription: {transcription}")
        return transcription
    else:
        print("Transcription failed.")
        return False



import sys
import os
from dotenv import load_dotenv
import pyaudio
from pynput import keyboard
import wave

import whisper

from langchain_openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate

class Assistant:

    def __init__(self):
        load_dotenv()
        os.environ.get("OPENAI_API_KEY")
        self.FORMAT = pyaudio.paInt16  
        self.CHANNELS = 1             
        self.RATE = 44100              
        self.CHUNK = 1024              
        self.WAVE_OUTPUT_FILENAME = "output.wav"

        self.audio = pyaudio.PyAudio()  

        self.stream = self.audio.open(format=self.FORMAT,
                                      channels=self.CHANNELS,
                                      rate=self.RATE,
                                      input=True,
                                      frames_per_buffer=self.CHUNK)

        self.recording = False
        self.frames = []
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_rel)
        self.listener.start()

        self.record()

    def get_stream_status(self):
        print(f"is it active: {self.stream.is_active()} \n is it stopped: {self.stream.is_stopped()}")

    def on_press(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                print("Recording started...")
                self.recording = True
        except AttributeError:
            pass  

    def on_rel(self, key):
        if key == keyboard.Key.esc:
            print("Exiting program...")
            return False  

        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                print("Recording stopped.")
                self.recording = False
                self.save_audio()
                self.cart()
        except AttributeError:
            pass  

    def save_audio(self):
        if self.frames:
            print("Saving recorded audio...")
            with wave.open(self.WAVE_OUTPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(self.frames))
            print(f"Audio saved as {self.WAVE_OUTPUT_FILENAME}")

    def cart(self):
        print("working on a response...")
        llm = OpenAI()

        model = whisper.load_model("turbo")
        result = model.transcribe("output.wav", fp16=False)

        user_text = result["text"]
        print(user_text)
        try:
            prompt = ChatPromptTemplate.from_template("The User is going to ask you to generate code. do your best to write the python code that meet the requirements. {message}")
            chain = prompt | llm

            resp = chain.invoke({"message":user_text})
            print("Here is my response...",resp)
        except Exception as e:
            print(e)

    def record(self):
        try:
            while True:
                if self.recording:
                    data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                    self.frames.append(data)
        except KeyboardInterrupt:
            print("Interrupted. Stopping recording.")

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()


start = Assistant()

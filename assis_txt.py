import sys
import pyaudio
from pynput import keyboard
import wave


class Assistant:

    def __init__(self):
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

        self.main()

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
        except AttributeError:
            pass  

    def main(self):
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

    def save_audio(self):
        if self.frames:
            print("Saving recorded audio...")
            with wave.open(self.WAVE_OUTPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(self.frames))
            print(f"Audio saved as {self.WAVE_OUTPUT_FILENAME}")


start = Assistant()

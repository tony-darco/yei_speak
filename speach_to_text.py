import speech_recognition as sr
import pyttsx3

r = sr.Recognizer()

class yei_speak:
    def __init__(self):
        self.engine = pyttsx3.init()

    def make_call() -> str:
        try:
            with sr.Microphone() as source2:
                r.adjust_for_ambient_noise(source2, duration=0.2)
                audio2 = r.listen(source2)

                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()

                return(MyText)

        except sr.RequestError as e:
            print('failed')
        except sr.UnknownValueError as ue:
            print ('TF')

    def respond(self, text:str) -> None:
        # Adjust volume
        self.engine.setProperty('rate', 210)
        volume = ['com.apple.eloquence.en-US.Flo','com.apple.speech.synthesis.voice.GoodNews','starting com.apple.voice.compact.en-AU.Karen','com.apple.voice.compact.en-IE.Moira','com.apple.voice.compact.en-ZA.Tessa','com.apple.voice.compact.en-US.Samantha','com.apple.speech.synthesis.voice.Trinoids']

        volume = ['com.apple.speech.synthesis.voice.GoodNews','starting com.apple.voice.compact.en-AU.Karen', 'com.apple.speech.synthesis.voice.GoodNews','com.apple.voice.compact.en-US.Samantha','com.apple.speech.synthesis.voice.Trinoids']
        #print(f'Current volume level: {volume}')
        self.engine.setProperty('volume', 1.0)

        # Getting the list of available voices
        '''def onStart(name):
            print ('starting', name)
        def onEnd(name, completed):
            print ('finishing', name, completed)
        self.engine.connect('started-utterance', onStart)
        self.engine.connect('finished-utterance', onEnd)'''

        '''for voice in volume:
            
            engine.setProperty('voice',voice)
            #print(voice.id)
            engine.say('The quick brown fox jumped over the lazy dog.', voice)'''
        
        self.engine.setProperty('voice','com.apple.voice.compact.en-US.Samantha')
        self.engine.say(text)
        self.engine.runAndWait()

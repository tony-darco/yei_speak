import speech_recognition as sr
import pyttsx3

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain.schema import StrOutputParser

r = sr.Recognizer()

class yei_speak:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.main()
    def make_call(self) -> str:
        print('listening')
        try:
            with sr.Microphone() as source2:
                r.pause_threshold = 1
                r.adjust_for_ambient_noise(source2, duration=0.2)
                audio2 = r.listen(source2, timeout=5 ,phrase_time_limit=30)

                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()
                print('done')
                return(MyText)
            
        except sr.RequestError as e:
            print('failed')
        except sr.UnknownValueError as ue:
            print ('TF')
            
    def brain(self,memory):
        user_input = self.make_call()
        print(user_input)
        
        memory += [(
                "human",
                f"{user_input}",
            )
            ]
        
        
        template = ChatPromptTemplate.from_messages(
            [
                ("""You are a conversion bot.
                 
        {question}"""),
                ("placeholder", "{messages}"),
            ]
        )        

        model = OllamaLLM(model="llama3.2")
        
        chain = template |  model | StrOutputParser()
        
        result = chain.invoke(
            {"question": user_input,
             "messages" : memory}
        )
        
        memory += [(
                "assistant",
                f"{result}",
            )
            ]
        
        self.respond(result)
        return(memory)

    def respond(self, text:str) -> None:
        print(text)
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
    def main(self): 
        memory = []
        while True:
            memory = self.brain(memory)
            print(memory)
conv_start = yei_speak()
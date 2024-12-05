import sys
import requests
import os
from dotenv import load_dotenv

from langchain_ollama import OllamaLLM, OllamaEmbeddings
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
import ollama

from pydantic import BaseModel, Field
from typing import List
from typing_extensions import TypedDict
from langgraph.graph import END, StateGraph, START

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from uuid import uuid4
from langchain_core.documents import Document

#import speech_recognition as sr
#import pyttsx3


class speak_dash:
    def __init__(self, *args, **kwargs):
        #self.engine = pyttsx3.init()
        load_dotenv()
        self.ollama_host = os.environ.get('OLLAMA_URL')
        #print("her",self.ollama_host)
        self._get_model()
        self._set_prompts()
        self._set_vectordb()
        

    def _get_model(self) -> None:
        """
        upon initialization the model setting at are set
        
        """

        self.llm = OllamaLLM(
        model="llama3.2:1b",
        base_url=self.ollama_host
        )


    def _set_prompts(self) -> None:
        
        self.response_template = ChatPromptTemplate.from_messages([
            (
                "system", 
                """You are an AI assistant designed to respond in a helpful, clear, and efficient manner. When addressing user requests, aim to maintain a friendly and conversational tone.
                
                
                Response Guidelines:
                If the memory list is empty (first-time interaction): Treat the conversation as a new topic and provide a friendly, straightforward response without referencing the absence of prior interactions.
                If the memory list contains prior exchanges: Focus on the current request and reference previous interactions only when necessary for clarity or context. Avoid repeating or rehashing earlier conversations unless it directly supports the current response.
                Instructions:
                Tone: Keep responses warm, friendly, and professional.
                Clarity: Prioritize clear, concise answers. Focus on addressing the user's current request efficiently.
                Contextual Awareness: If there is relevant prior conversation history, use it to inform your response.

                Here is the User's Request:
                {question}
            """
            ),
            ("placeholder", "{memory}")
        ])

    class _GraphState(TypedDict):
        question:str
        relevant_memory:List
        response:str

    def _generate_response(self, state:_GraphState) -> _GraphState:
        user_question:str = state["question"]
        conversation_context:str = state["relevant_memory"]

        #print(f"generating response: {user_question}, {conversation_context}")

        llm_chain:str = self.response_template | self.llm | StrOutputParser()

        response = llm_chain.invoke(
            {"question":user_question,
             "memory":conversation_context}
            )

        print("stat",response,'data')
        state.update({
            "response":response
        })
        return state

    def _set_vectordb(self):
        self.vector_collection = os.environ.get('VECTOR_COLLECTION')
        self.vector_directory = os.environ.get('VECTOR_DIRECTORY')

        '''self.emb_llm = OllamaEmbeddings(
            model="llama3.2:1b",
            base_url=self.ollama_host
        )'''

        self.emb_llm = OllamaEmbeddingFunction(
            model_name="llama3.2:1b",
            url=self.ollama_host
        )
        ollama.Client(host=self.ollama_host)
        
        vector_client = chromadb.PersistentClient(path=self.vector_directory)
        self.vector_collection = vector_client.get_or_create_collection(name=self.vector_collection, metadata={"hnsw:space": "cosine"})

        
        
    def send_to_memory(self,state :_GraphState) -> None:
        user_question:str = state["question"]
        response:str = state["response"]

        vector_store = self.vector_collection
        
        memory_content = f"Request:{user_question}"

        response = ollama.embeddings(model="llama3.2:1b",prompt=memory_content)
        new_entry_embedding = response["embedding"]

        try:
            vector_store.add(documents = [memory_content],embeddings=new_entry_embedding,ids=[str(uuid4())])
        except Exception as e:
            print("Failed to add vector store", e)


    def get_memory(self, state: _GraphState):
        user_question:str = state["question"]
        
        vector_store = self.vector_collection

        response = ollama.embeddings(model="llama3.2:1b",prompt=user_question)
        user_question_embedding = response["embedding"]

        similarity_threshold = 0.4

        relevant_memory = vector_store.query(
            query_embeddings = [response["embedding"]],
            n_results = 10,
            include=['distances','documents']
        )
        filter_mem = [mem for mem, dist in zip(relevant_memory['documents'][0], relevant_memory["distances"][0]) if dist <= similarity_threshold]

        if relevant_memory["embeddings"] == None:
            relevant_memory = []

        print(relevant_memory, filter_mem)
        print('here', vector_store.query(
            query_embeddings = [response["embedding"]],
            n_results = 10,
            include=['distances','documents']
        ))

        state.update({
            "relevant_memory":filter_mem
        })
        return(state)

    def voice(self, state: _GraphState) -> None:
        text = state['response']
        # Adjust volume
        self.engine.setProperty('rate', 210)
        self.engine.setProperty('volume', 1.0)
        
        self.engine.say(text)
        self.engine.runAndWait()
        
    def create_workflow(self):
        workflow = StateGraph(self._GraphState)

        workflow.add_node('store_mem', self.send_to_memory)
        workflow.add_node('retrieve_mem', self.get_memory)
        workflow.add_node('respond', self._generate_response)
        #workflow.add_node('voice', self.voice)
        

        workflow.add_edge(START,'retrieve_mem')
        workflow.add_edge('retrieve_mem','respond')
        workflow.add_edge('respond','store_mem')
        #workflow.add_edge('store_mem', 'voice')
        #workflow.add_edge('voice', END)
        workflow.add_edge('store_mem', END)
        
        #print(type(workflow.compile()))
        return(workflow.compile())
        
    def speak(self ) -> None:
        app = self.create_workflow()
        app.invoke(
            {
                "question":"what is wrong with my ip address",
                'relevant_memory':[],
                'response':'',
            })


speak_dash().speak()
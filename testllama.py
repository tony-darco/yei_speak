"""
Tried to RAG the memory..didn't work like I want
"""


import sys
import requests
import os
import json
from dotenv import load_dotenv

from t import OllamaLLM, OllamaEmbeddings
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
import ollama

from pydantic import BaseModel, Field
from typing import List, Literal
from typing_extensions import TypedDict
from operator import itemgetter
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
        #self._set_vectordb()
        

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
                """
                
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

    def _intent(self, state: _GraphState) -> None:
        route_system = "Route the user's query to an api enpoint and method."
        route_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", route_system),
                ("human", "{user_query}")
            ]
        )

        data=[]

        with open('endpoint_description.json', 'r') as file:
            data = json.load(file)

        def is_valid_destination(destination: str) -> bool:
            return destination in data


        class RouteQuery(TypedDict):
            """ROute query to endpoint"""
            destination: Literal["left", "right"]

        route_chain = (
            route_prompt
            | self.llm.with_structured_output(RouteQuery, method="function_calling", include_raw=True)
            | itemgetter("destination")
        )

        output = route_chain.invoke({'user_query': 'Generates an API key for an identity'})  # Replace with actual invocation

        # Validate the destination
        if is_valid_destination(output['destination']):
            print(f"Routing to: {output['destination']}")
        else:
            print(f"Invalid destination: {output['destination']}")


    def voice(self, state: _GraphState) -> None:
        text = state['response']
        # Adjust volume
        self.engine.setProperty('rate', 210)
        self.engine.setProperty('volume', 1.0)
        
        self.engine.say(text)
        self.engine.runAndWait()
        
    def create_workflow(self):
        workflow = StateGraph(self._GraphState)

        #workflow.add_node('store_mem', self.send_to_memory)
        #workflow.add_node('retrieve_mem', self.get_memory)
        #workflow.add_node('respond', self._generate_response)
        #workflow.add_node('voice', self.voice)
        workflow.add_node('store_mem', self._intent)
        

        workflow.add_edge(START,'store_mem')
        #workflow.add_edge('retrieve_mem','respond')
        #workflow.add_edge('respond','store_mem')
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
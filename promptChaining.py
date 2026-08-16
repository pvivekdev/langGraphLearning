import operator
import time
from typing import TypedDict, Annotated, Literal
import ollama
from langchain_core import prompts, messages
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, system, human
from langgraph import  graph,store
from langchain_ollama import  chat_models
from langgraph import graph


llm = chat_models.ChatOllama(model='gemma4:latest', temperature=0.7)

class BlogCreationState(TypedDict):
    title: str
    outline: str
    content: str
    messageHistory :Annotated[BaseMessage, messages.add_message]

def create_outline(state: BlogCreationState) -> BlogCreationState:
    title = state['title']
    prompt  =  f'Generate a detailed outline about {state[title]}'
    outline = llm.invoke(prompt).content
    state['outline'] = outline

def create_blog(state: BlogCreationState) -> BlogCreationState:
    title = state['title']
    outline = state['outline']
    prompt = f'Generate a detailed blog about {state[title]} using the outline {state[outline]}'
    content = llm.invoke(prompt).content
    state['content'] = str(content)
    return state



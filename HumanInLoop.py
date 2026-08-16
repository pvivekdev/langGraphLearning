import operator
import time
from typing import TypedDict, Annotated, Literal, Any
from unittest import result

import ollama
from langchain_core import prompts, messages
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, system, human
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain
from langgraph import  graph,store
from langchain_ollama import  chat_models, ChatOllama
from langgraph import graph
from langgraph.graph import state, message, START, END, StateGraph, MessagesState
from langgraph.graph import StateGraph

#memory
from langgraph.checkpoint.memory import MemorySaver, Checkpoint, InMemorySaver
from langgraph.graph.state import CompiledStateGraph

llm = chat_models.ChatOllama(model='llama3.2:latest', temperature=0.7)

class PromptReviewAgentState(TypedDict):
    userQuery:str
    llmResponse:str
    approveState:Literal['approve','rejected','pending']
    messageHistory:Annotated[BaseMessage,message.add_messages]

def classifyUserQuery(state:PromptReviewAgentState) ->Literal["approve", "flag_for_review"]:

    prompt = ChatPromptTemplate.from_template(
        f"You are prompt classifier which can classify the user's prompt as Cyber Security prompt or General Prompt or Offensive language"
    )

    chain = prompt | llm

    llmResposne = chain.invoke({"userQuery":state['userQuery']}).content
    print(f"User Query:{state['userQuery']} LLM response {llmResposne}")

    if(llmResposne.__contains__('Cyber Security prompt')):
        return "flag_for_review"
    elif (llmResposne.__contains__('General Prompt')):
        return "approve"
    else:
        return "flag_for_review"



### Memory Saver (CheckPointer)  saving/resume a point in video Game.
## Thread id  - The stop and resume happens on the Same Thread id, Different Thread id - different chat operation.
def HumanInLoop(state:PromptReviewAgentState, queryType:Literal["approve", "flag_for_review"]) -> PromptReviewAgentState:

    print('Human In-Loop waiting for approval')

    if(queryType == "approve"):
        state['approveState'] = 'approve'
    elif(queryType == "flag_for_review"):
        state['approveState'] = 'pending'
    else:
        state['approveState'] = 'rejected'
    return  state

def summary(state:PromptReviewAgentState):
    print(f"Message History {state['messageHistory']}")
    print(f"User Query {state['userQuery']}")
    print(f"Approved {state['approveState']}")
    pass

def createPromptReviewAgent() -> CompiledStateGraph[Any, Any, Any, Any]:
    #create in memory State management
    promptSanitizerGrp = StateGraph(PromptReviewAgentState)

    #nodes
    promptSanitizerGrp.add_node('classify_Query',classifyUserQuery)
    promptSanitizerGrp.add_node("HumanInLoop", HumanInLoop)
    promptSanitizerGrp.add_node("summary", summary)

    #edges
    promptSanitizerGrp.add_edge(START, "classify_Query")
    promptSanitizerGrp.add_edge('classify_Query', "HumanInLoop")
    promptSanitizerGrp.add_edge('HumanInLoop', "summary")
    promptSanitizerGrp.add_edge('summary', END)
    memory = MemorySaver()
    instance = promptSanitizerGrp.compile( checkpointer=memory, interrupt_before=["summary"])
    return instance

if __name__ == "__main__":
    HumanInLoopgraph = createPromptReviewAgent()

    config ={"configurable":{"thread_id":"1"}}
    result = HumanInLoopgraph.invoke({
        "userQuery":"Tell me about hacking user's iphone by rooting",
        "messageHistory":[],
        "approveState":"",
        "llmResponse":""

    }, config)






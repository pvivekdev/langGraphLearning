import operator
import time
from typing import TypedDict, Annotated, Literal

import ollama
from  langchain_core import prompts
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, system, human
from langgraph import  graph,store
from langchain_ollama import  chat_models
from langgraph import graph, store
from langgraph.graph import state, message, START, END, StateGraph, MessagesState
from sqlalchemy import true

llm  =  chat_models.ChatOllama(model='llama3.2:latest', temperature=0)

class DastAgentScannerState(TypedDict):
    """State for the DastAgentScanner."""

    # Add any state variables you need here
    last_scan_time: float
    scan_results: str
    host_url: str
    findings: list
    userQuery:str
    messageHistory: Annotated[BaseMessage, message.add_messages]
    itrCnt:Annotated[int, operator.add]

def zap_scanner_node(state: DastAgentScannerState) -> DastAgentScannerState:
    """A node that performs a DAST scan using Zap and updates the state."""
    # Perform the DAST scan using Zap
    # Update the state with the results
    state['last_scan_time'] = time.time()
    state['scan_results'] = 'done'
    state['findings'] = []
    state['host_url'] = 'https://example.com'
    state['findings'] = ["Zero"]
    response = llm.invoke(state['userQuery'])
    print(f'LLm response {response.content}')
    state['messageHistory'] = [response]
    return state

def checkHostReachability (state:DastAgentScannerState) ->DastAgentScannerState:
    state['messageHistory'] = [f"Check for the host reachability for {state['host_url']}"]
    response = llm.invoke(f"Check for the host reachability for {state['host_url']}")
    state['messageHistory'] = response.content
    state['itrCnt'] = 1
    return state

def introFunction(state:DastAgentScannerState) -> DastAgentScannerState:
    resposne  = llm.invoke(state['userQuery'])
    state['messageHistory'] = resposne.content
    return state

#def routing(state:DastAgentScannerState) -> Literal["ZapScan","End"]:

def create_zap_scanner_graph() -> StateGraph:
    graph = StateGraph(DastAgentScannerState)
    graph.add_node("HostReachability", checkHostReachability)
    graph.add_node("ZapScanner",zap_scanner_node)
    graph.add_edge(START,"HostReachability")
    #graph.add_conditional_edges("HostReachability","ZapScanner")
    graph.add_edge("HostReachability","ZapScanner")
    graph.add_edge("ZapScanner",END)
    return graph

def create_parallel_workflow() ->StateGraph:
    parallelGraph = StateGraph(DastAgentScannerState)
    parallelGraph.add_node('IntroFunction',introFunction )
    parallelGraph.add_node('HostReachability', checkHostReachability)
    parallelGraph.add_node("ZapScanner", zap_scanner_node)
    parallelGraph.add_edge(START,"IntroFunction")
    parallelGraph.add_edge(START,"HostReachability")
    parallelGraph.add_edge(START,'ZapScanner')
    return parallelGraph



if __name__ == "__main__":
    # Create the Zap scanner graph

    # Initialize the state for the DastAgentScanner
    initial_state: DastAgentScannerState = {
        "last_scan_time": 0,
        "scan_results": "",
        "host_url": "https://example.com",
        "findings": [],
        "userQuery" : "Tell me mor about zap Proxy Open source Tool"
    }

    zap_graph = create_zap_scanner_graph()
    compiled = zap_graph.compile()
    print("Zap scanner graph created. Executing the graph...")
    print("Graph nodes:", zap_graph.nodes)
    print("Graph edges:", zap_graph.edges)
    grpah_png = compiled.get_graph().draw_mermaid_png()
    with open("zap_graph.png", "wb") as f:
        f.write(grpah_png)

    parallelGraph = create_parallel_workflow()
    compiledParallelGraph = parallelGraph.compile()
    parallel_png = compiledParallelGraph.get_graph().draw_mermaid_png()
    with open("parallel_graph.png", "wb") as f:
        f.write(parallel_png)

    # Execute the graph with the initial state
    result = compiled.invoke(initial_state)
    print("DAST scan completed. Results:", result)

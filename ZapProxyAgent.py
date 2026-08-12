from typing import TypedDict

import ollama
from  langchain_core import prompts
from langgraph import  graph,store, stream
from langchain_ollama import  chat_models
from openai import models
from sympy.strategies import chain
from typer.cli import state
from langgraph import graph, store, stream

from langgraph.graph import Graph, Node, Edge,State, START,End, NodeType, EdgeType, NodeState, EdgeState, StateGraph


llm  =  ollama.chat(model='llama', messages='')

class DastAgentScannerState(TypedDict):
    """State for the DastAgentScanner."""

    # Add any state variables you need here
    last_scan_time: str
    scan_results: dict
    host_url: str
    findings: list

def zap_scanner_node(state: DastAgentScannerState) -> str:
    """A node that performs a DAST scan using Zap and updates the state."""
    # Perform the DAST scan using Zap
    # Update the state with the results
    # Return a new node with the updated state
    return str(state['host_url'])


def create_zap_scanner_graph() -> StateGraph:
    graph = StateGraph(name="ZapScannerGraph", description="A graph for performing DAST scans using Zap.")
    graph.add_node(NodeType.START, name="Start", description="Start of the DAST scan process.")
    graph.add_node(NodeType.PROCESS, name="ZapScanner", description="Perform DAST scan using Zap.", func=zap_scanner_node)
    graph.add_node(NodeType.END, name="End", description="End of the DAST scan process.")
    graph.add_edge(EdgeType.SEQUENCE, source=NodeType.START, target=NodeType.PROCESS)
    graph.add_edge(EdgeType.SEQUENCE, source=NodeType.PROCESS, target=NodeType.END)
    return graph

if __name__ == "__main__":
    # Create the Zap scanner graph
    zap_graph = create_zap_scanner_graph()

    zap_graph.compile().get_graph().draw_mermaid_png().save("zap_scanner_graph.png")
    print("Zap scanner graph created. Executing the graph...")
    print("Graph nodes:", zap_graph.nodes)
    print("Graph edges:", zap_graph.edges)
    print("Graph description:", zap_graph.description)
    print("Graph name:", zap_graph.name)

    # Initialize the state for the DastAgentScanner
    initial_state: DastAgentScannerState = {
        "last_scan_time": "",
        "scan_results": {},
        "host_url": "http://example.com",
        "findings": [],
    }

    # Execute the graph with the initial state
    result = zap_graph.execute(initial_state)
    print("DAST scan completed. Results:", result)


from dotenv import load_dotenv
import os
load_dotenv()  # Load .env FIRST—before any agent imports

from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents.router_agent import RouterAgent
from agents.web_search_agent import WebSearchAgent
from agents.file_analysis_agent import FileAnalysisAgent
from agents.synthesizer_agent import SynthesizerAgent
from utils.logger import log_step

class AgentState(TypedDict):
    query: str
    route: str
    agent_output: str
    final_response: str
    file_name: str
    has_file: bool

def create_graph():
    # Now agents can access the env var
    router = RouterAgent()
    web_agent = WebSearchAgent()
    file_agent = FileAnalysisAgent()
    synth = SynthesizerAgent()

    workflow = StateGraph(AgentState)

    def router_node(state: AgentState):
        log_step("Graph.router_node", f"Routing query: {state['query']}")
        state["route"] = router.route(state["query"], state["has_file"])
        return state

    def web_node(state: AgentState):
        log_step("Graph.web_node", "Executing web search")
        output = web_agent.execute(state["query"])
        state["agent_output"] = output
        return state

    def file_node(state: AgentState):
        log_step("Graph.file_node", f"Executing file analysis on {state['file_name']}")
        output = file_agent.analyze(state["query"])  # Use 'analyze' if using RetrievalQA version
        state["agent_output"] = output
        return state

    def synth_node(state: AgentState):
        log_step("Graph.synth_node", "Synthesizing response")
        state["final_response"] = synth.synthesize(state["query"], state["agent_output"], state["route"])
        return state

    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("web", web_node)
    workflow.add_node("file", file_node)
    workflow.add_node("synthesize", synth_node)

    # Edges
    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        lambda s: s["route"],
        {"web_search": "web", "file_analysis": "file"}
    )
    workflow.add_edge("web", "synthesize")
    workflow.add_edge("file", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()

graph = create_graph()
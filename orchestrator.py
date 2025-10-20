"""
LangGraph-based orchestration system for multi-agent query routing
"""

import time
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import Graph, StateGraph, END
from langgraph.graph.message import add_messages
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from agents.router import QueryRouter
from agents.web_search_agent import WebSearchAgent
from agents.file_analysis_agent import FileAnalysisAgent
from agents.synthesizer import ResponseSynthesizer
from config import Config

class AgentState(TypedDict):
    """State object for the agent workflow"""
    query: str
    file_paths: List[str]
    agent_choice: str
    reasoning: str
    web_results: Optional[Dict[str, Any]]
    file_results: Optional[Dict[str, Any]]
    final_response: Optional[Dict[str, Any]]
    messages: List[BaseMessage]
    error: Optional[str]

class MultiAgentOrchestrator:
    """Main orchestrator for the multi-agent system"""
    
    def __init__(self):
        """Initialize the orchestrator with all agents"""
        self.router = QueryRouter()
        self.web_agent = WebSearchAgent()
        self.file_agent = FileAnalysisAgent()
        self.synthesizer = ResponseSynthesizer()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("router", self._router_node)
        workflow.add_node("web_search", self._web_search_node)
        workflow.add_node("file_analysis", self._file_analysis_node)
        workflow.add_node("synthesizer", self._synthesizer_node)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Add conditional edges from router
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "web_search": "web_search",
                "file_analysis": "file_analysis",
                "both": "web_search",  # Start with web search for 'both'
                "error": END
            }
        )
        
        # Add edges from web search
        workflow.add_conditional_edges(
            "web_search",
            self._after_web_search,
            {
                "synthesizer": "synthesizer",
                "file_analysis": "file_analysis",
                "end": END
            }
        )
        
        # Add edges from file analysis
        workflow.add_conditional_edges(
            "file_analysis",
            self._after_file_analysis,
            {
                "synthesizer": "synthesizer",
                "end": END
            }
        )
        
        # Add edge from synthesizer to end
        workflow.add_edge("synthesizer", END)
        
        return workflow.compile()
    
    def _router_node(self, state: AgentState) -> AgentState:
        """Router node that classifies the query"""
        try:
            print(f"Routing query: {state['query']}")
            
            has_files = len(state.get('file_paths', [])) > 0
            agent_choice, reasoning = self.router.classify_query(state['query'], has_files)
            
            state['agent_choice'] = agent_choice
            state['reasoning'] = reasoning
            
            print(f"Router decision: {agent_choice} - {reasoning}")
            
        except Exception as e:
            print(f"Error in router: {e}")
            state['error'] = f"Router error: {str(e)}"
            state['agent_choice'] = "error"
        
        return state
    
    def _web_search_node(self, state: AgentState) -> AgentState:
        """Web search node"""
        try:
            print("Executing web search...")
            
            web_results = self.web_agent.process_query(state['query'])
            state['web_results'] = web_results
            
            print(f"Web search completed: {len(web_results.get('results', []))} results")
            
        except Exception as e:
            print(f"Error in web search: {e}")
            state['web_results'] = {
                'error': str(e),
                'results': [],
                'extracted_info': {'summary': f'Web search failed: {str(e)}'}
            }
        
        return state
    
    def _file_analysis_node(self, state: AgentState) -> AgentState:
        """File analysis node"""
        try:
            print("Executing file analysis...")
            
            file_paths = state.get('file_paths', [])
            if file_paths:
                file_results = self.file_agent.process_files(file_paths, state['query'])
            else:
                # No files provided, create empty results
                file_results = {
                    'query': state['query'],
                    'files_processed': 0,
                    'processing_results': [],
                    'total_chunks': 0,
                    'vectorstore_built': False,
                    'search_results': [],
                    'agent_type': 'file_analysis',
                    'timestamp': time.time()
                }
            
            state['file_results'] = file_results
            
            print(f"File analysis completed: {file_results.get('files_processed', 0)} files processed")
            
        except Exception as e:
            print(f"Error in file analysis: {e}")
            state['file_results'] = {
                'error': str(e),
                'files_processed': 0,
                'processing_results': [],
                'total_chunks': 0,
                'vectorstore_built': False,
                'search_results': []
            }
        
        return state
    
    def _synthesizer_node(self, state: AgentState) -> AgentState:
        """Synthesizer node"""
        try:
            print("Synthesizing response...")
            
            final_response = self.synthesizer.synthesize_response(
                query=state['query'],
                web_results=state.get('web_results'),
                file_results=state.get('file_results')
            )
            
            state['final_response'] = final_response
            
            print("Response synthesis completed")
            
        except Exception as e:
            print(f"Error in synthesizer: {e}")
            state['final_response'] = {
                'query': state['query'],
                'answer': f"Error synthesizing response: {str(e)}",
                'confidence': 0.0,
                'citations': [],
                'error': str(e)
            }
        
        return state
    
    def _route_decision(self, state: AgentState) -> str:
        """Decision function for routing after router node"""
        agent_choice = state.get('agent_choice', 'error')
        
        if agent_choice == 'error':
            return "error"
        elif agent_choice == 'WEB_SEARCH':
            return "web_search"
        elif agent_choice == 'FILE_ANALYSIS':
            return "file_analysis"
        elif agent_choice == 'BOTH':
            return "both"
        else:
            return "error"
    
    def _after_web_search(self, state: AgentState) -> str:
        """Decision function after web search"""
        agent_choice = state.get('agent_choice', '')
        
        if agent_choice == 'BOTH':
            # Need to also do file analysis
            return "file_analysis"
        else:
            # Only web search needed, go to synthesizer
            return "synthesizer"
    
    def _after_file_analysis(self, state: AgentState) -> str:
        """Decision function after file analysis"""
        # Always go to synthesizer after file analysis
        return "synthesizer"
    
    def process_query(self, query: str, file_paths: List[str] = None) -> Dict[str, Any]:
        """
        Process a query through the multi-agent system
        
        Args:
            query: User query string
            file_paths: Optional list of file paths to analyze
            
        Returns:
            Dictionary with the final response and metadata
        """
        if file_paths is None:
            file_paths = []
        
        # Initialize state
        initial_state = AgentState(
            query=query,
            file_paths=file_paths,
            agent_choice="",
            reasoning="",
            web_results=None,
            file_results=None,
            final_response=None,
            messages=[],
            error=None
        )
        
        print(f"Processing query: {query}")
        if file_paths:
            print(f"With files: {file_paths}")
        
        try:
            # Execute the workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Extract results
            result = {
                'query': query,
                'file_paths': file_paths,
                'agent_choice': final_state.get('agent_choice', ''),
                'reasoning': final_state.get('reasoning', ''),
                'final_response': final_state.get('final_response', {}),
                'web_results': final_state.get('web_results'),
                'file_results': final_state.get('file_results'),
                'error': final_state.get('error'),
                'timestamp': time.time()
            }
            
            return result
            
        except Exception as e:
            print(f"Error in workflow execution: {e}")
            return {
                'query': query,
                'file_paths': file_paths,
                'error': f"Workflow execution failed: {str(e)}",
                'timestamp': time.time()
            }
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the workflow structure"""
        return {
            'nodes': ['router', 'web_search', 'file_analysis', 'synthesizer'],
            'entry_point': 'router',
            'end_points': ['END'],
            'description': 'Multi-agent query routing and processing workflow'
        }


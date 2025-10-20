#!/usr/bin/env python3
"""
Main application interface for the Multi-Agent Query Router
"""

import argparse
import sys
import os
import time
from typing import List, Dict, Any

from orchestrator import MultiAgentOrchestrator
from utils.logger import logger
from config import Config

class MultiAgentApp:
    """Main application class for the multi-agent system"""
    
    def __init__(self):
        """Initialize the application"""
        self.orchestrator = None
        self.setup_orchestrator()
    
    def setup_orchestrator(self):
        """Setup the orchestrator with error handling"""
        try:
            # Validate configuration
            config_status = Config.validate_config()
            if not config_status['valid']:
                print("Configuration validation failed:")
                for issue in config_status['issues']:
                    print(f"  - {issue}")
                sys.exit(1)
            
            # Initialize orchestrator
            self.orchestrator = MultiAgentOrchestrator()
            print("Multi-Agent Orchestrator initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize orchestrator: {e}")
            sys.exit(1)
    
    def process_query(self, query: str, file_paths: List[str] = None) -> Dict[str, Any]:
        """
        Process a query through the multi-agent system
        
        Args:
            query: User query
            file_paths: Optional list of file paths
            
        Returns:
            Processing results
        """
        if file_paths is None:
            file_paths = []
        
        # Validate file paths
        valid_files = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                valid_files.append(file_path)
            else:
                print(f"Warning: File not found: {file_path}")
        
        # Log the request start
        request_id = logger.log_request(query, valid_files)
        
        try:
            # Process through orchestrator
            result = self.orchestrator.process_query(query, valid_files)
            
            # Log results
            if result.get('web_results'):
                logger.log_web_search_results(request_id, result['web_results'])
            
            if result.get('file_results'):
                logger.log_file_analysis_results(request_id, result['file_results'])
            
            if result.get('final_response'):
                logger.log_final_response(request_id, result['final_response'])
            
            if result.get('error'):
                logger.log_error(request_id, result['error'])
            
            return result
            
        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            logger.log_error(request_id, error_msg, "processing_error")
            return {
                'query': query,
                'file_paths': valid_files,
                'error': error_msg,
                'timestamp': time.time()
            }
    
    def display_results(self, result: Dict[str, Any]):
        """Display processing results in a formatted way"""
        print("\n" + "="*80)
        print("MULTI-AGENT QUERY PROCESSING RESULTS")
        print("="*80)
        
        # Basic info
        print(f"Query: {result.get('query', 'N/A')}")
        print(f"Files: {result.get('file_paths', [])}")
        print(f"Agent Choice: {result.get('agent_choice', 'N/A')}")
        print(f"Reasoning: {result.get('reasoning', 'N/A')}")
        
        # Error handling
        if result.get('error'):
            print(f"\n❌ ERROR: {result['error']}")
            return
        
        # Final response
        final_response = result.get('final_response', {})
        if final_response:
            print(f"\n📝 FINAL ANSWER:")
            print("-" * 40)
            print(final_response.get('answer', 'No answer provided'))
            
            # Confidence score
            confidence = final_response.get('confidence', 0)
            print(f"\n🎯 Confidence Score: {confidence:.2f}")
            
            # Citations
            citations = final_response.get('citations', [])
            if citations:
                print(f"\n📚 Citations ({len(citations)}):")
                for i, citation in enumerate(citations, 1):
                    print(f"  {i}. {citation.get('title', 'No title')}")
                    if citation.get('url'):
                        print(f"     URL: {citation['url']}")
                    if citation.get('snippet'):
                        print(f"     Snippet: {citation['snippet']}")
        
        # Agent results summary
        web_results = result.get('web_results')
        if web_results:
            print(f"\n🌐 Web Search Results:")
            print(f"  - Search Type: {web_results.get('search_type', 'N/A')}")
            print(f"  - Results Found: {len(web_results.get('results', []))}")
            extracted_info = web_results.get('extracted_info', {})
            print(f"  - Confidence: {extracted_info.get('confidence', 0):.2f}")
        
        file_results = result.get('file_results')
        if file_results:
            print(f"\n📁 File Analysis Results:")
            print(f"  - Files Processed: {file_results.get('files_processed', 0)}")
            print(f"  - Text Chunks: {file_results.get('total_chunks', 0)}")
            print(f"  - Vector Store Built: {file_results.get('vectorstore_built', False)}")
            search_results = file_results.get('search_results', [])
            print(f"  - Relevant Chunks Found: {len(search_results)}")
        
        print("\n" + "="*80)
    
    def interactive_mode(self):
        """Run the application in interactive mode"""
        print("🤖 Multi-Agent Query Router - Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if user_input.lower() == 'stats':
                    self.show_statistics()
                    continue
                
                if user_input.lower() == 'logs':
                    self.show_recent_logs()
                    continue
                
                # Process the query
                result = self.process_query(user_input)
                self.display_results(result)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_help(self):
        """Show help information"""
        print("\n📖 Available Commands:")
        print("  help     - Show this help message")
        print("  stats    - Show system statistics")
        print("  logs     - Show recent request logs")
        print("  quit     - Exit the application")
        print("\n💡 Usage Examples:")
        print("  What is the capital of France?")
        print("  Who won the last FIFA World Cup?")
        print("  What is the current weather in Tokyo?")
        print("\n📁 File Analysis (when files are uploaded):")
        print("  Summarize this document")
        print("  Find all mentions of 'quantum computing'")
        print("  Describe the main subject in this image")
    
    def show_statistics(self):
        """Show system statistics"""
        stats = logger.get_statistics()
        
        print("\n📊 System Statistics:")
        print("-" * 30)
        print(f"Total Requests: {stats.get('total_requests', 0)}")
        print(f"Completed: {stats.get('completed_requests', 0)}")
        print(f"Errors: {stats.get('error_requests', 0)}")
        print(f"Success Rate: {stats.get('success_rate', 0):.1%}")
        print(f"Avg Processing Time: {stats.get('average_processing_time', 0):.2f}s")
        
        agent_usage = stats.get('agent_usage', {})
        if agent_usage:
            print(f"\nAgent Usage:")
            for agent, count in agent_usage.items():
                print(f"  {agent}: {count}")
        
        file_types = stats.get('file_types_processed', {})
        if file_types:
            print(f"\nFile Types Processed:")
            for file_type, count in file_types.items():
                print(f"  {file_type}: {count}")
    
    def show_recent_logs(self, limit: int = 5):
        """Show recent request logs"""
        logs = logger.get_recent_logs(limit)
        
        print(f"\n📋 Recent Requests (last {limit}):")
        print("-" * 40)
        
        for log in logs:
            timestamp = log.get('datetime', 'Unknown time')
            query = log.get('query', 'No query')[:50] + '...' if len(log.get('query', '')) > 50 else log.get('query', 'No query')
            status = log.get('status', 'unknown')
            agent_choice = log.get('agent_choice', 'N/A')
            
            status_emoji = "✅" if status == "completed" else "❌" if status == "error" else "⏳"
            
            print(f"{status_emoji} {timestamp} | {agent_choice} | {query}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Multi-Agent Query Router')
    parser.add_argument('query', nargs='?', help='Query to process')
    parser.add_argument('-f', '--files', nargs='*', help='File paths to analyze')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--stats', action='store_true', help='Show system statistics')
    parser.add_argument('--logs', action='store_true', help='Show recent logs')
    
    args = parser.parse_args()
    
    # Initialize application
    app = MultiAgentApp()
    
    # Handle different modes
    if args.stats:
        app.show_statistics()
    elif args.logs:
        app.show_recent_logs()
    elif args.interactive:
        app.interactive_mode()
    elif args.query:
        # Single query mode
        result = app.process_query(args.query, args.files)
        app.display_results(result)
    else:
        # Default to interactive mode
        app.interactive_mode()

if __name__ == "__main__":
    main()


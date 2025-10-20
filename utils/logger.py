"""
Logging system for tracking requests, responses, and system metrics
"""

import json
import uuid
import time
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import Config

class RequestLogger:
    """Logger for tracking system requests and responses"""
    
    def __init__(self, log_file: str = None):
        """
        Initialize the logger
        
        Args:
            log_file: Path to the log file (defaults to outputs/requests.json)
        """
        if log_file is None:
            log_file = os.path.join(Config.OUTPUTS_DIR, 'requests.json')
        
        self.log_file = log_file
        self.ensure_log_file_exists()
    
    def ensure_log_file_exists(self):
        """Ensure the log file exists and is properly formatted"""
        if not os.path.exists(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w') as f:
                json.dump([], f)
    
    def log_request(self, query: str, file_paths: List[str] = None, 
                   agent_choice: str = "", reasoning: str = "") -> str:
        """
        Log the start of a request
        
        Args:
            query: User query
            file_paths: List of file paths
            agent_choice: Router's agent choice
            reasoning: Router's reasoning
            
        Returns:
            Request ID for tracking
        """
        request_id = str(uuid.uuid4())
        
        log_entry = {
            'request_id': request_id,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'query': query,
            'file_paths': file_paths or [],
            'agent_choice': agent_choice,
            'reasoning': reasoning,
            'status': 'started',
            'start_time': time.time()
        }
        
        self._append_to_log(log_entry)
        return request_id
    
    def log_web_search_results(self, request_id: str, web_results: Dict[str, Any]):
        """
        Log web search results
        
        Args:
            request_id: Request ID to update
            web_results: Results from web search agent
        """
        self._update_log_entry(request_id, {
            'web_search_results': web_results,
            'web_search_completed': time.time()
        })
    
    def log_file_analysis_results(self, request_id: str, file_results: Dict[str, Any]):
        """
        Log file analysis results
        
        Args:
            request_id: Request ID to update
            file_results: Results from file analysis agent
        """
        self._update_log_entry(request_id, {
            'file_analysis_results': file_results,
            'file_analysis_completed': time.time()
        })
    
    def log_final_response(self, request_id: str, final_response: Dict[str, Any]):
        """
        Log the final synthesized response
        
        Args:
            request_id: Request ID to update
            final_response: Final response from synthesizer
        """
        self._update_log_entry(request_id, {
            'final_response': final_response,
            'status': 'completed',
            'end_time': time.time()
        })
    
    def log_error(self, request_id: str, error: str, error_type: str = "general"):
        """
        Log an error for a request
        
        Args:
            request_id: Request ID to update
            error: Error message
            error_type: Type of error
        """
        self._update_log_entry(request_id, {
            'error': error,
            'error_type': error_type,
            'status': 'error',
            'end_time': time.time()
        })
    
    def _append_to_log(self, log_entry: Dict[str, Any]):
        """Append a new entry to the log file"""
        try:
            # Read existing logs
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            # Append new entry
            logs.append(log_entry)
            
            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def _update_log_entry(self, request_id: str, updates: Dict[str, Any]):
        """Update an existing log entry"""
        try:
            # Read existing logs
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            # Find and update the entry
            for log_entry in logs:
                if log_entry.get('request_id') == request_id:
                    log_entry.update(updates)
                    break
            
            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Error updating log file: {e}")
    
    def get_request_log(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific request log by ID
        
        Args:
            request_id: Request ID to retrieve
            
        Returns:
            Log entry or None if not found
        """
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            for log_entry in logs:
                if log_entry.get('request_id') == request_id:
                    return log_entry
            
            return None
            
        except Exception as e:
            print(f"Error reading log file: {e}")
            return None
    
    def get_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent log entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent log entries
        """
        try:
            # Check if file exists and has content
            if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
                return []
            
            with open(self.log_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                logs = json.loads(content)
            
            # Sort by timestamp (most recent first)
            logs.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            return logs[:limit]
            
        except Exception as e:
            print(f"Error reading log file: {e}")
            return []
    
    def get_logs_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get logs filtered by status
        
        Args:
            status: Status to filter by (started, completed, error)
            
        Returns:
            List of matching log entries
        """
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            filtered_logs = [log for log in logs if log.get('status') == status]
            
            # Sort by timestamp (most recent first)
            filtered_logs.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            return filtered_logs
            
        except Exception as e:
            print(f"Error reading log file: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about logged requests
        
        Returns:
            Dictionary with various statistics
        """
        try:
            # Check if file exists and has content
            if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
                return {
                    'total_requests': 0,
                    'completed_requests': 0,
                    'error_requests': 0,
                    'average_processing_time': 0,
                    'agent_usage': {},
                    'file_types_processed': {}
                }
            
            with open(self.log_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {
                        'total_requests': 0,
                        'completed_requests': 0,
                        'error_requests': 0,
                        'average_processing_time': 0,
                        'agent_usage': {},
                        'file_types_processed': {}
                    }
                logs = json.loads(content)
            
            if not logs:
                return {
                    'total_requests': 0,
                    'completed_requests': 0,
                    'error_requests': 0,
                    'average_processing_time': 0,
                    'agent_usage': {},
                    'file_types_processed': {}
                }
            
            # Calculate statistics
            total_requests = len(logs)
            completed_requests = len([log for log in logs if log.get('status') == 'completed'])
            error_requests = len([log for log in logs if log.get('status') == 'error'])
            
            # Calculate average processing time
            processing_times = []
            for log in logs:
                if log.get('start_time') and log.get('end_time'):
                    processing_time = log['end_time'] - log['start_time']
                    processing_times.append(processing_time)
            
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Agent usage statistics
            agent_usage = {}
            for log in logs:
                agent_choice = log.get('agent_choice', 'unknown')
                agent_usage[agent_choice] = agent_usage.get(agent_choice, 0) + 1
            
            # File types processed
            file_types = {}
            for log in logs:
                file_paths = log.get('file_paths', [])
                for file_path in file_paths:
                    file_ext = os.path.splitext(file_path)[1].lower()
                    file_types[file_ext] = file_types.get(file_ext, 0) + 1
            
            return {
                'total_requests': total_requests,
                'completed_requests': completed_requests,
                'error_requests': error_requests,
                'success_rate': completed_requests / total_requests if total_requests > 0 else 0,
                'average_processing_time': avg_processing_time,
                'agent_usage': agent_usage,
                'file_types_processed': file_types
            }
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {
                'total_requests': 0,
                'completed_requests': 0,
                'error_requests': 0,
                'average_processing_time': 0,
                'agent_usage': {},
                'file_types_processed': {},
                'error': str(e)
            }
    
    def export_logs(self, output_file: str, format: str = 'json'):
        """
        Export logs to a file
        
        Args:
            output_file: Path to output file
            format: Export format ('json' or 'csv')
        """
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            if format == 'json':
                with open(output_file, 'w') as f:
                    json.dump(logs, f, indent=2)
            elif format == 'csv':
                import pandas as pd
                df = pd.DataFrame(logs)
                df.to_csv(output_file, index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            print(f"Logs exported to {output_file}")
            
        except Exception as e:
            print(f"Error exporting logs: {e}")

# Global logger instance
logger = RequestLogger()


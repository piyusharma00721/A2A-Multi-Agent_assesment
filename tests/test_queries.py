"""
Test cases for the Multi-Agent Query Router system
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import MultiAgentOrchestrator
from agents.router import QueryRouter
from agents.web_search_agent import WebSearchAgent
from agents.file_analysis_agent import FileAnalysisAgent
from agents.synthesizer import ResponseSynthesizer
from config import Config

class TestQueryRouter(unittest.TestCase):
    """Test cases for the QueryRouter"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the Google API key for testing
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            self.router = QueryRouter()
    
    def test_web_search_classification(self):
        """Test classification of web search queries"""
        test_cases = [
            ("What is the capital of France?", False, "WEB_SEARCH"),
            ("Who won the last FIFA World Cup?", False, "WEB_SEARCH"),
            ("What is the current weather in Tokyo?", False, "WEB_SEARCH"),
        ]
        
        for query, has_files, expected in test_cases:
            with patch.object(self.router.llm, 'invoke') as mock_invoke:
                mock_invoke.return_value = MagicMock(content=f"{expected}\nThis is a web search query")
                agent_choice, reasoning = self.router.classify_query(query, has_files)
                self.assertEqual(agent_choice, expected)
    
    def test_file_analysis_classification(self):
        """Test classification of file analysis queries"""
        test_cases = [
            ("Summarize this document", True, "FILE_ANALYSIS"),
            ("Find all mentions of 'quantum computing'", True, "FILE_ANALYSIS"),
            ("Describe the main subject in this image", True, "FILE_ANALYSIS"),
        ]
        
        for query, has_files, expected in test_cases:
            with patch.object(self.router.llm, 'invoke') as mock_invoke:
                mock_invoke.return_value = MagicMock(content=f"{expected}\nThis is a file analysis query")
                agent_choice, reasoning = self.router.classify_query(query, has_files)
                self.assertEqual(agent_choice, expected)
    
    def test_both_classification(self):
        """Test classification of queries requiring both agents"""
        test_cases = [
            ("Compare this document with current news about the topic", True, "BOTH"),
            ("Find recent information about the subject in this file", True, "BOTH"),
        ]
        
        for query, has_files, expected in test_cases:
            with patch.object(self.router.llm, 'invoke') as mock_invoke:
                mock_invoke.return_value = MagicMock(content=f"{expected}\nThis requires both web search and file analysis")
                agent_choice, reasoning = self.router.classify_query(query, has_files)
                self.assertEqual(agent_choice, expected)
    
    def test_fallback_classification(self):
        """Test fallback classification when LLM fails"""
        with patch.object(self.router.llm, 'invoke') as mock_invoke:
            mock_invoke.side_effect = Exception("API Error")
            
            # Test with files
            agent_choice, reasoning = self.router.classify_query("Test query", True)
            self.assertIn(agent_choice, ["FILE_ANALYSIS", "BOTH"])
            
            # Test without files
            agent_choice, reasoning = self.router.classify_query("Test query", False)
            self.assertEqual(agent_choice, "WEB_SEARCH")

class TestWebSearchAgent(unittest.TestCase):
    """Test cases for the WebSearchAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.web_agent = WebSearchAgent()
    
    @patch('agents.web_search_agent.DDGS')
    def test_web_search(self, mock_ddgs):
        """Test web search functionality"""
        # Mock search results
        mock_results = [
            {
                'title': 'Test Result 1',
                'href': 'https://example.com/1',
                'body': 'This is a test result about the query topic.'
            },
            {
                'title': 'Test Result 2',
                'href': 'https://example.com/2',
                'body': 'Another test result with relevant information.'
            }
        ]
        
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = mock_results
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance
        
        result = self.web_agent.search("test query")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Test Result 1')
        self.assertEqual(result[0]['url'], 'https://example.com/1')
        self.assertEqual(result[0]['source'], 'web_search')
    
    def test_extract_key_information(self):
        """Test key information extraction"""
        results = [
            {
                'title': 'Test Result',
                'url': 'https://example.com',
                'snippet': 'This is about quantum computing and its applications.',
                'rank': 1
            }
        ]
        
        extracted = self.web_agent.extract_key_information(results, "quantum computing")
        
        self.assertIn('summary', extracted)
        self.assertIn('key_facts', extracted)
        self.assertIn('sources', extracted)
        self.assertIn('confidence', extracted)
        self.assertGreater(extracted['confidence'], 0)

class TestFileAnalysisAgent(unittest.TestCase):
    """Test cases for the FileAnalysisAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.file_agent = FileAnalysisAgent()
    
    def test_text_file_extraction(self):
        """Test text file extraction"""
        test_file = "test_files/sample_text.txt"
        if os.path.exists(test_file):
            result = self.file_agent.extract_text_from_file(test_file)
            
            self.assertTrue(result['success'])
            self.assertIn('quantum computing', result['text'].lower())
            self.assertEqual(result['metadata']['file_type'], 'text')
    
    def test_csv_file_extraction(self):
        """Test CSV file extraction"""
        test_file = "test_files/sample_data.csv"
        if os.path.exists(test_file):
            result = self.file_agent.extract_text_from_file(test_file)
            
            self.assertTrue(result['success'])
            self.assertIn('john smith', result['text'].lower())
            self.assertEqual(result['metadata']['file_type'], 'tabular')
            self.assertGreater(result['metadata']['rows'], 0)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent files"""
        result = self.file_agent.extract_text_from_file("nonexistent_file.txt")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result['metadata'])
    
    @patch('agents.file_analysis_agent.HuggingFaceEmbeddings')
    def test_vectorstore_building(self, mock_embeddings):
        """Test vector store building"""
        mock_embeddings.return_value = MagicMock()
        
        texts = ["This is a test document.", "Another test document."]
        metadatas = [{'source': 'test1'}, {'source': 'test2'}]
        
        vectorstore = self.file_agent.build_vectorstore(texts, metadatas)
        
        # Should return a FAISS vectorstore (mocked)
        self.assertIsNotNone(vectorstore)

class TestSynthesizer(unittest.TestCase):
    """Test cases for the ResponseSynthesizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            self.synthesizer = ResponseSynthesizer()
    
    def test_web_search_context_formatting(self):
        """Test web search context formatting"""
        web_results = {
            'results': [
                {
                    'title': 'Test Result',
                    'url': 'https://example.com',
                    'snippet': 'This is a test snippet.',
                    'rank': 1
                }
            ],
            'extracted_info': {
                'summary': 'Test summary',
                'key_facts': ['Fact 1', 'Fact 2']
            }
        }
        
        context = self.synthesizer.format_web_search_context(web_results)
        
        self.assertIn('WEB SEARCH RESULTS', context)
        self.assertIn('Test Result', context)
        self.assertIn('Test summary', context)
    
    def test_file_analysis_context_formatting(self):
        """Test file analysis context formatting"""
        file_results = {
            'files_processed': 1,
            'total_chunks': 5,
            'search_results': [
                {
                    'content': 'Test content from file',
                    'metadata': {'file_path': 'test.txt'},
                    'similarity_score': 0.8
                }
            ]
        }
        
        context = self.synthesizer.format_file_analysis_context(file_results)
        
        self.assertIn('FILE ANALYSIS RESULTS', context)
        self.assertIn('Files processed: 1', context)
        self.assertIn('Test content from file', context)
    
    @patch.object(ResponseSynthesizer, 'llm')
    def test_response_synthesis(self, mock_llm):
        """Test response synthesis"""
        mock_llm.invoke.return_value = MagicMock(content="This is a synthesized response.")
        
        web_results = {
            'results': [{'title': 'Test', 'url': 'https://example.com', 'snippet': 'Test snippet'}],
            'extracted_info': {'summary': 'Test summary'}
        }
        
        result = self.synthesizer.synthesize_response("test query", web_results)
        
        self.assertEqual(result['query'], "test query")
        self.assertEqual(result['answer'], "This is a synthesized response.")
        self.assertIn('confidence', result)
        self.assertIn('citations', result)

class TestMultiAgentOrchestrator(unittest.TestCase):
    """Test cases for the MultiAgentOrchestrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            self.orchestrator = MultiAgentOrchestrator()
    
    def test_workflow_structure(self):
        """Test workflow structure"""
        workflow_info = self.orchestrator.get_workflow_info()
        
        self.assertIn('router', workflow_info['nodes'])
        self.assertIn('web_search', workflow_info['nodes'])
        self.assertIn('file_analysis', workflow_info['nodes'])
        self.assertIn('synthesizer', workflow_info['nodes'])
        self.assertEqual(workflow_info['entry_point'], 'router')
    
    @patch.object(MultiAgentOrchestrator, 'orchestrator')
    def test_query_processing(self, mock_orchestrator):
        """Test query processing workflow"""
        # Mock the workflow execution
        mock_orchestrator.invoke.return_value = {
            'query': 'test query',
            'agent_choice': 'WEB_SEARCH',
            'final_response': {
                'answer': 'Test answer',
                'confidence': 0.8
            }
        }
        
        result = self.orchestrator.process_query("test query")
        
        self.assertEqual(result['query'], 'test query')
        self.assertIn('final_response', result)

class TestSampleQueries(unittest.TestCase):
    """Test cases for the sample queries from the specification"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            self.orchestrator = MultiAgentOrchestrator()
    
    def test_sample_queries_classification(self):
        """Test classification of sample queries"""
        sample_queries = [
            ("What is the capital of France?", False, "WEB_SEARCH"),
            ("Who won the last FIFA World Cup?", False, "WEB_SEARCH"),
            ("What is the current weather in Tokyo?", False, "WEB_SEARCH"),
            ("Summarize the key findings in this document", True, "FILE_ANALYSIS"),
            ("Find all mentions of 'quantum computing' in this text file", True, "FILE_ANALYSIS"),
        ]
        
        for query, has_files, expected_agent in sample_queries:
            with patch.object(self.orchestrator.router.llm, 'invoke') as mock_invoke:
                mock_invoke.return_value = MagicMock(content=f"{expected_agent}\nTest reasoning")
                agent_choice, reasoning = self.orchestrator.router.classify_query(query, has_files)
                self.assertEqual(agent_choice, expected_agent)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestQueryRouter,
        TestWebSearchAgent,
        TestFileAnalysisAgent,
        TestSynthesizer,
        TestMultiAgentOrchestrator,
        TestSampleQueries
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


"""
Complete RAG System Test
Comprehensive test for document ingestion, vector database, LLM recognition, and query functionality
"""

import asyncio
import json
import requests
from pathlib import Path
import time
from typing import Dict, List, Any

class RAGSystemTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_result(self, test_name: str, passed: bool, message: str, details: str = ""):
        """Log test result"""
        result = {
            'test': test_name,
            'passed': passed,
            'message': message,
            'details': details,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_server_health(self) -> bool:
        """Test 1: Server Health Check"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Server Health", True, "Server is healthy", f"Status: {data.get('status')}")
                return True
            else:
                self.log_result("Server Health", False, f"Server returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Server Health", False, f"Health check failed: {str(e)}")
            return False
    
    def test_document_upload(self) -> bool:
        """Test 2: Document Upload"""
        try:
            # Create a test document
            test_content = """# Test Document for RAG System

## Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that enables systems to learn from data.

### Key Concepts

1. **Supervised Learning**: Learning with labeled data
2. **Unsupervised Learning**: Finding patterns in unlabeled data  
3. **Deep Learning**: Neural networks with multiple layers

### Applications

- Healthcare: Medical diagnosis
- Finance: Fraud detection
- Technology: Image recognition

This document is specifically designed to test the RAG system's ability to ingest, index, and retrieve content accurately.
"""
            
            test_file = Path("test_rag_document.txt")
            test_file.write_text(test_content, encoding='utf-8')
            
            # Upload document
            with open(test_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.base_url}/api/v1/ingest", files=files, timeout=30)
            
            # Clean up test file
            test_file.unlink()
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Document Upload", True, "Document uploaded successfully", 
                              f"Doc ID: {data.get('doc_id', 'N/A')}")
                return data.get('doc_id')
            else:
                self.log_result("Document Upload", False, f"Upload failed with status {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Document Upload", False, f"Upload failed: {str(e)}")
            return None
    
    def test_document_registry(self) -> bool:
        """Test 3: Document Registry"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/documents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                doc_count = data.get('total', 0)
                self.log_result("Document Registry", True, f"Found {doc_count} documents in registry",
                              f"Documents: {doc_count}")
                return doc_count > 0
            else:
                self.log_result("Document Registry", False, f"Registry check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Document Registry", False, f"Registry check failed: {str(e)}")
            return False
    
    def test_vector_database(self) -> bool:
        """Test 4: Vector Database Status"""
        try:
            vdb_file = Path("lightrag_db/vdb_chunks.json")
            if vdb_file.exists():
                file_size = vdb_file.stat().st_size
                self.log_result("Vector Database", True, "Vector database file exists",
                              f"File size: {file_size} bytes")
                return True
            else:
                self.log_result("Vector Database", False, "Vector database file not found")
                return False
        except Exception as e:
            self.log_result("Vector Database", False, f"Vector database check failed: {str(e)}")
            return False
    
    def test_search_api_get(self) -> bool:
        """Test 5: Search API (GET Method)"""
        try:
            query = "Machine Learning"
            response = requests.get(f"{self.base_url}/api/v1/search", 
                                   params={'q': query, 'mode': 'hybrid'}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                has_answer = len(answer) > 10 and "未找到" not in answer
                self.log_result("Search API (GET)", True, "GET search successful",
                              f"Answer length: {len(answer)}, Has content: {has_answer}")
                return has_answer
            else:
                self.log_result("Search API (GET)", False, f"GET search failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Search API (GET)", False, f"GET search failed: {str(e)}")
            return False
    
    def test_search_api_post(self) -> bool:
        """Test 6: Search API (POST Method)"""
        try:
            query = "Supervised Learning"
            response = requests.post(f"{self.base_url}/api/v1/search",
                                    json={'q': query, 'mode': 'hybrid'}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                has_answer = len(answer) > 10 and "未找到" not in answer
                self.log_result("Search API (POST)", True, "POST search successful",
                              f"Answer length: {len(answer)}, Has content: {has_answer}")
                return has_answer
            else:
                self.log_result("Search API (POST)", False, f"POST search failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Search API (POST)", False, f"POST search failed: {str(e)}")
            return False
    
    def test_llm_knowledge_base_recognition(self) -> bool:
        """Test 7: LLM Knowledge Base Recognition"""
        try:
            # Test query that should be in knowledge base
            queries = [
                "Machine Learning",
                "Supervised Learning", 
                "Deep Learning",
                "Healthcare applications"
            ]
            
            successful_queries = 0
            for query in queries:
                response = requests.post(f"{self.base_url}/api/v1/search",
                                        json={'q': query, 'mode': 'hybrid'}, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('answer', '')
                    # Check if answer has meaningful content (not just "not found")
                    if len(answer) > 20 and "未找到" not in answer:
                        successful_queries += 1
            
            success_rate = successful_queries / len(queries)
            self.log_result("LLM Knowledge Base Recognition", success_rate > 0.5,
                          f"LLM recognized {successful_queries}/{len(queries)} queries",
                          f"Success rate: {success_rate:.1%}")
            return success_rate > 0.5
            
        except Exception as e:
            self.log_result("LLM Knowledge Base Recognition", False, f"Recognition test failed: {str(e)}")
            return False
    
    def test_context_assembly(self) -> bool:
        """Test 8: Context Assembly and Retrieval"""
        try:
            # Test specific query to check if context is properly assembled
            query = "What are the applications of machine learning?"
            response = requests.post(f"{self.base_url}/api/v1/search",
                                    json={'q': query, 'mode': 'hybrid'}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                # Check if answer contains expected keywords from the document
                expected_keywords = ['healthcare', 'finance', 'technology', 'application']
                found_keywords = [kw for kw in expected_keywords if kw.lower() in answer.lower()]
                
                has_context = len(found_keywords) >= 2
                self.log_result("Context Assembly", has_context,
                              f"Found {len(found_keywords)}/{len(expected_keywords)} expected keywords",
                              f"Keywords found: {found_keywords}")
                return has_context
            else:
                self.log_result("Context Assembly", False, f"Context test failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Context Assembly", False, f"Context test failed: {str(e)}")
            return False
    
    def test_anti_hallucination(self) -> bool:
        """Test 9: Anti-Hallucination (Knowledge Base Only)"""
        try:
            # Test query that should NOT be in knowledge base
            query = "What is quantum mechanics theory?"
            response = requests.post(f"{self.base_url}/api/v1/search",
                                    json={'q': query, 'mode': 'hybrid'}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                # Should return "not found" message for knowledge base content
                is_hallucination_free = "未找到" in answer or "没有" in answer
                self.log_result("Anti-Hallucination", is_hallucination_free,
                              "LLM correctly refused to answer outside knowledge base",
                              f"Answer contains 'not found': {is_hallucination_free}")
                return is_hallucination_free
            else:
                self.log_result("Anti-Hallucination", False, f"Anti-hallucination test failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Anti-Hallucination", False, f"Anti-hallucination test failed: {str(e)}")
            return False
    
    def test_response_time(self) -> bool:
        """Test 10: Response Time Performance"""
        try:
            query = "Machine Learning applications"
            start_time = time.time()
            response = requests.post(f"{self.base_url}/api/v1/search",
                                    json={'q': query, 'mode': 'hybrid'}, timeout=30)
            end_time = time.time()
            response_time = end_time - start_time
            
            is_fast = response_time < 10.0  # Should respond within 10 seconds
            self.log_result("Response Time", is_fast,
                          f"Query response time: {response_time:.2f}s",
                          f"Performance: {'Good' if is_fast else 'Slow'}")
            return is_fast
        except Exception as e:
            self.log_result("Response Time", False, f"Response time test failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print("=" * 60)
        print("COMPLETE RAG SYSTEM TEST")
        print("=" * 60)
        print()
        
        # Run all tests
        self.test_server_health()
        doc_id = self.test_document_upload()
        self.test_document_registry()
        self.test_vector_database()
        self.test_search_api_get()
        self.test_search_api_post()
        self.test_llm_knowledge_base_recognition()
        self.test_context_assembly()
        self.test_anti_hallucination()
        self.test_response_time()
        
        # Calculate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        print()
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1%}")
        print()
        
        if success_rate >= 0.8:
            print("🎉 OVERALL: EXCELLENT - System is working well!")
        elif success_rate >= 0.6:
            print("✅ OVERALL: GOOD - System is functional with minor issues")
        else:
            print("⚠️  OVERALL: NEEDS IMPROVEMENT - System has significant issues")
        
        print()
        print("DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': success_rate,
            'test_results': self.test_results
        }

def main():
    """Main test execution"""
    tester = RAGSystemTester()
    results = tester.run_all_tests()
    
    # Save results to file
    results_file = Path("rag_system_test_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nTest results saved to: {results_file}")
    
    return results['success_rate'] >= 0.6

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
from typing import Dict
import logging
from src.core.generator import WisdomResponseGenerator
from src.core.retriever import VedicKnowledgeRetriever

from src.core.query_preprocessor import QueryProcessor
class VedicWisdomPipeline:
    """Enhanced RAG pipeline for Vedic wisdom"""
    
    def __init__(self):
        """Initialize pipeline components"""
        try:
            self.preprocessor = QueryProcessor()
            self.retriever = VedicKnowledgeRetriever()
            self.generator = WisdomResponseGenerator()
            logging.info("VedicWisdomPipeline initialized successfully")
        except Exception as e:
            logging.error(f"Pipeline initialization failed: {e}")
            raise

    async def process_query(self, query: str) -> Dict:
        """Process user query and generate response"""
        try:
            # Preprocess query
            processed = self.preprocessor.process_query(query)
            
            # Check if clarification needed
            if processed['needs_clarification']:
                return self._handle_clarification_needed(processed['original_query'])
            
            # Retrieve relevant verses
            verses = self.retriever.get_verses_hybrid(processed['processed_query'])
            logging.info(f"Retrieved {len(verses)} verses")
            
            if not verses:
                return self._handle_no_verses()
            
            # Generate response with word count info
            result = await self.generator.generate_answer(
                processed['processed_query'], 
                verses,
                processed['word_count']
            )
            
            # Add preprocessing info to response
            result['query_info'] = {
                'original': processed['original_query'],
                'processed': processed['processed_query']
            }
            print(result)
            return result
            
        except Exception as e:
            logging.error(f"Query processing failed: {e}")
            return {"error": str(e)}

    def _handle_clarification_needed(self, query: str) -> Dict:
        """Handle queries that need clarification"""
        return {
            "type": "clarification_needed",
            "response": {
                "summary": f"Could you please provide more details about your question: '{query}'? "
                          "This will help me find the most relevant wisdom from the ancient texts.",
                "sources": []
            }
        }
    
    def _handle_no_verses():
        """Handle queries that nhas no verses"""
        return {
            "type": "clarification_needed",
            "response": {
                "summary": f"Could you please provide more details of the Question "
                          "This will help me find the most relevant wisdom from the ancient texts.",
                "sources": []
            }
        }
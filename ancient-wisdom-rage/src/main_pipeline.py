import logging
from typing import List, Dict, Optional, Tuple
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import networkx as nx
from groq import AsyncGroq
import json
import os
import datetime
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import asyncio
from config.sanskrit_mappings import SanskritMappings


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download all required NLTK data at initialization
def download_nltk_data():
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('omw-1.4', quiet=True)  # Open Multilingual Wordnet
        logging.info("Successfully downloaded all NLTK data")
    except Exception as e:
        logging.error(f"Error downloading NLTK data: {e}")
        raise

        
class EnhancedVerseRetriever:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        try:
            # Download NLTK data first
            download_nltk_data()
            
            self.model = SentenceTransformer(model_name)
            
            logging.info("Connecting to database...")
            self.conn = psycopg2.connect(
                dbname="ancient_wisdom",
                user="postgres",
                password="Nikhil@930",
                host="localhost"
            )
            self.conn.set_session(autocommit=True)  # Enable autocommit
            logging.info("Database connection successful")
        except Exception as e:
            logging.error(f"Initialization error: {e}")
            raise

    def get_verses_hybrid(self, query: str, top_k: int = 5) -> List[Dict]:
        try:
            logging.info(f"Processing query: {query}")
            
            results = []
            query_embedding = self.model.encode(query)
            
            # Debug: Check embedding dimensions
            logging.info(f"Embedding dimensions: {len(query_embedding)}")
            
            # Format vector string properly with square brackets
            vector_str = f"[{','.join(map(str, query_embedding))}]"
            
            # First, let's verify the table structure and a sample row
            with self.conn.cursor() as cur:
                # Check if table exists and its structure
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'verses';
                """)
                table_info = cur.fetchall()
                logging.info(f"Table structure: {table_info}")
                
                # Get a sample row to verify data
                cur.execute("SELECT id, embedding FROM verses LIMIT 1;")
                sample = cur.fetchone()
                if sample:
                    logging.info(f"Sample row id: {sample[0]}")
                    logging.info(f"Sample embedding dimensions: {len(sample[1])}")
                
                # Try query with lower similarity threshold
                query_sql = """
                    SELECT id, book, chapter, verse, sanskrit, translation, explanation,
                            1 - (embedding <=> %s::vector) as similarity
                    FROM verses 
                    WHERE 1 - (embedding <=> %s::vector) > 0.3  -- Lowered threshold
                    ORDER BY similarity DESC
                    LIMIT %s
                """
                
                logging.info(f"Executing query with vector: {vector_str[:100]}...")  # Log first 100 chars
                cur.execute(query_sql, (vector_str, vector_str, top_k))
                
                verses = cur.fetchall()
                logging.info(f"Query returned {len(verses)} results")
                
                if verses:
                    for verse in verses:
                        results.append({
                            'id': verse[0],
                            'book': verse[1],
                            'chapter': verse[2],
                            'verse': verse[3],
                            'sanskrit': verse[4],
                            'translation': verse[5],
                            'explanation': verse[6],
                            'confidence_score': float(verse[7])
                        })
        
            # Remove duplicates and sort by confidence score
            unique_results = {v['id']: v for v in results}
            sorted_results = sorted(unique_results.values(), 
                                    key=lambda x: x['confidence_score'], 
                                    reverse=True)
            
            logging.info(f"Found {len(sorted_results)} unique verses")
            return sorted_results[:top_k]
            
        except Exception as e:
            logging.error(f"Error in verse retrieval: {str(e)}")
            logging.error(f"Full error details:", exc_info=True)  # Add full traceback
            return []
        
class EnhancedAnswerGenerator:
    def __init__(self):
        try:
            self.client = AsyncGroq(
                api_key='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'
            )
            logging.info("Groq client initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing Groq client: {e}")
            self.client = None
    
    async def generate_answer(self, query: str, verses: List[Dict]) -> Dict:
        try:
            if not verses:
                return {"error": "No relevant verses found"}
            
            if self.client is None:
                return {"error": "LLM client not initialized properly"}
            
            # Prepare verse citations
            verse_citations = []
            for v in verses[:3]:  # Use top 3 verses
                citation = f"[{v['book']} {v['chapter']}.{v['verse']}]: {v['translation']}\nExplanation: {v['explanation']}"
                verse_citations.append(citation)
            
            prompt = f"""Question: {query}

Relevant verses from ancient texts:
{chr(10).join(verse_citations)}

Please provide a comprehensive answer that:
1. Directly addresses the question using wisdom from the provided verses
2. Cites specific verses using [Book Chapter.Verse] format
3. Explains the practical application of this wisdom
4. Connects the verses' teachings to the question

Answer in a clear, conversational style while maintaining philosophical accuracy."""
            
            # Await the async response
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                "type": "wisdom_response",
                "verse": verses[0],  # Include the most relevant verse
                "response": {
                    "summary": response.choices[0].message.content.strip(),
                    "sources": [f"{v['book']} {v['chapter']}.{v['verse']}" for v in verses[:3]]
                }
            }
            
        except Exception as e:
            logging.error(f"Error in answer generation: {e}")
            return {
                "error": f"Failed to generate answer: {str(e)}",
                "fallback_response": {
                    "type": "wisdom_response",
                    "verse": verses[0] if verses else None,
                    "response": {
                        "summary": "I apologize, but I encountered an error while generating the response. However, I found some relevant verses that might help answer your question. Please check the verse details below.",
                        "sources": [f"{v['book']} {v['chapter']}.{v['verse']}" for v in verses[:3]] if verses else []
                    }
                }
            }


# Also update the RAGPipeline class to handle async
class EnhancedRAGPipeline:
    def __init__(self):
        try:
            self.retriever = EnhancedVerseRetriever()
            self.generator = EnhancedAnswerGenerator()
            logging.info("RAG Pipeline initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing RAG Pipeline: {e}")
            raise
    
    async def process_query(self, query: str) -> Dict:
        try:
            # Get verses
            verses = self.retriever.get_verses_hybrid(query)
            logging.info(f"Retrieved {len(verses)} verses")
            
            if not verses:
                return {
                    "type": "wisdom_response",
                    "verse": None,
                    "response": {
                        "summary": "I apologize, but I couldn't find specific verses that directly address your question. Could you please rephrase your question or ask about a related topic?",
                        "sources": []
                    }
                }
            
            # Generate response
            result = await self.generator.generate_answer(query, verses)
            return result
            
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            return {"error": str(e)}
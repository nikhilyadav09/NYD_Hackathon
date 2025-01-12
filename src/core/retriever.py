from typing import List, Dict, Optional
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import logging
from src.config.settings import DatabaseConfig
from functools import lru_cache

class VedicKnowledgeRetriever:
    """Enhanced retriever for Vedic knowledge using hybrid search approach"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize retriever with embedding model and search components"""
        self.model = SentenceTransformer(model_name)
        self.bm25 = None
        self.setup_database()
        self.setup_bm25()
        logging.info("VedicKnowledgeRetriever initialized successfully")

    def setup_database(self):
        """Setup database connection with error handling"""
        try:
            self.conn = psycopg2.connect(**DatabaseConfig.CONNECTION_PARAMS)
            self.conn.set_session(autocommit=True)
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def setup_bm25(self):
        """Initialize BM25 for keyword-based search"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT translation, explanation FROM verses")
                docs = [f"{t} {e}" for t, e in cur.fetchall()]
                tokenized_docs = [word_tokenize(doc.lower()) for doc in docs]
                self.bm25 = BM25Okapi(tokenized_docs)
                logging.info("BM25 index created successfully")
        except Exception as e:
            logging.error(f"BM25 setup failed: {e}")
            raise
        
    @lru_cache(maxsize=1000)
    def get_verses_hybrid(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve verses using hybrid search approach"""
        try:
            semantic_results = self._semantic_search(query, top_k * 2)
            bm25_results = self._bm25_search(query, top_k * 2)
            
            # Combine and rerank results
            combined_results = self._rerank_results(query, semantic_results, bm25_results, top_k)
            logging.info(f"Retrieved {len(combined_results)} verses for query: {query}")
            
            return combined_results[:top_k]
        except Exception as e:
            logging.error(f"Verse retrieval failed: {e}")
            return []

    def _semantic_search(self, query: str, top_k: int) -> List[Dict]:
        """Perform semantic search using embeddings"""
        query_embedding = self.model.encode(query)
        vector_str = f"[{','.join(map(str, query_embedding))}]"
        
        with self.conn.cursor() as cur:
            query_sql = """
                SELECT id, book, chapter, verse, sanskrit, translation, explanation,
                        1 - (embedding <=> %s::vector) as similarity
                FROM verses 
                WHERE 1 - (embedding <=> %s::vector) > 0.3
                ORDER BY similarity DESC
                LIMIT %s
            """
            cur.execute(query_sql, (vector_str, vector_str, top_k))
            return self._format_results(cur.fetchall())

    def _bm25_search(self, query: str, top_k: int) -> List[Dict]:
        """Perform keyword-based search using BM25"""
        tokenized_query = word_tokenize(query.lower())
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, book, chapter, verse, sanskrit, translation, explanation FROM verses")
            verses = cur.fetchall()
            scores = self.bm25.get_scores(tokenized_query)
            
            # Combine verses with scores and sort
            scored_verses = [(verse, score) for verse, score in zip(verses, scores)]
            scored_verses.sort(key=lambda x: x[1], reverse=True)
            
            return self._format_results([v[0] for v in scored_verses[:top_k]])

    def _rerank_results(self, query: str, semantic_results: List[Dict], 
                       bm25_results: List[Dict], top_k: int) -> List[Dict]:
        """Rerank combined results using weighted scoring"""
        combined_dict = {}
        
        # Combine semantic and BM25 results with weights
        for i, result in enumerate(semantic_results):
            combined_dict[result['id']] = {
                **result,
                'final_score': 0.7 * (1 - i/len(semantic_results))
            }
        
        for i, result in enumerate(bm25_results):
            if result['id'] in combined_dict:
                combined_dict[result['id']]['final_score'] += 0.3 * (1 - i/len(bm25_results))
            else:
                combined_dict[result['id']] = {
                    **result,
                    'final_score': 0.3 * (1 - i/len(bm25_results))
                }
        
        # Sort by final score
        results = list(combined_dict.values())
        results.sort(key=lambda x: x['final_score'], reverse=True)
        return results

    def _format_results(self, verses: List[tuple]) -> List[Dict]:
        """Format database results into structured dictionaries"""
        return [{
            'id': verse[0],
            'book': verse[1],
            'chapter': verse[2],
            'verse': verse[3],
            'sanskrit': verse[4],
            'translation': verse[5],
            'explanation': verse[6],
            'confidence_score': verse[7] if len(verse) > 7 else None
        } for verse in verses]

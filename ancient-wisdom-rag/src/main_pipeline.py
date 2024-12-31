import logging
from typing import List, Dict, Optional
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
import os

# Load environment variables

class VerseRetriever:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.conn = psycopg2.connect(
            dbname="ancient_wisdom",
            user="postgres",
            password="Nikhil@930",
            host="localhost"
        )

    def get_similar_verses(self, query: str, k: int = 3) -> List[Dict]:
        try:
            query_embedding = self.model.encode(query)
            
            # Format the embedding as a PostgreSQL array string
            vector_str = f"'[{','.join(map(str, query_embedding))}]'"
            
            cur = self.conn.cursor()
            
            cur.execute(f"""
                WITH ranked_verses AS (
                    SELECT 
                        v.chapter,
                        v.verse,
                        v.sanskrit,
                        v.translation,
                        q.question,
                        1 - (embedding <#> {vector_str}::vector(384)) as similarity
                    FROM verses v
                    LEFT JOIN questions q ON v.id = q.verse_id
                    ORDER BY embedding <#> {vector_str}::vector(384)
                    LIMIT %s
                )
                SELECT DISTINCT chapter, verse, sanskrit, translation
                FROM ranked_verses
            """, (k,))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    'chapter': row[0],
                    'verse': row[1],
                    'sanskrit': row[2],
                    'translation': row[3],
                })
            
            cur.close()
            return results
            
        except Exception as e:
            logging.error(f"Error in retrieval: {e}")
            self.conn.rollback()
            return []

    def close(self):
        if self.conn:
            self.conn.close()

class GroqAnswerGenerator:

    def generate_prompt(self, query: str, verses: List[Dict]) -> str:
        prompt = f"""Based on the following verses from ancient texts, please answer the question: "{query}"

            Context verses:
            """
        for i, verse in enumerate(verses, 1):
            prompt += f"""
            Verse {i}:
            Chapter {verse['chapter']}, Verse {verse['verse']}
            Sanskrit: {verse['sanskrit']}
            Translation: {verse['translation']}
            """
                    
        prompt += """
            Please provide an answer that:
            1. Directly addresses the question
            2. References specific verses when relevant
            3. Maintains the philosophical depth of the original texts
            4. Avoids any information not supported by the given verses

            Answer: """
        return prompt

    def generate_answer(self, query: str, verses: List[Dict]) -> Dict:
        try:
            current_key = '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'
            client = Groq(api_key=current_key)
            
            prompt = self.generate_prompt(query, verses)
            messages = [{
                "role": "user",
                "content": prompt
            }]
            
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama3-8b-8192",
                max_tokens=500
            )
            
            response = chat_completion.choices[0].message.content
            
            result = {
                "query": query,
                "verses": verses,
                "answer": response,
                "metadata": {
                    "model": "llama3-8b-8192",
                    "num_verses": len(verses)
                }
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error in answer generation: {e}")
            return {"error": str(e)}

def rewrite_question(query: str) -> str:
    try:
        key1 = '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'
        client = Groq(api_key=key1)
        
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"""
                You are an expert in language refinement.
                Rephrase the following question:
                Original question: "{query}"
                Make sure the rewritten version:
                - Is grammatically correct and concise
                - Retains the original meaning
                - Sounds natural and professional
                """
            }],
            model="llama3-8b-8192",
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error in question rewriting: {e}")
        return query

class RAGPipeline:
    def __init__(self):
        self.retriever = VerseRetriever()
        self.generator = GroqAnswerGenerator()
        
    def validate_query(self, query: str) -> bool:
        if not query or len(query.strip()) < 5:
            return False
        return True
        
    def process_query(self, query: str, rewrite: bool = True) -> Dict:
        try:
            if not self.validate_query(query):
                return {"error": "Invalid or inappropriate query"}
            
            if rewrite:
                query = rewrite_question(query)
            
            verses = self.retriever.get_similar_verses(query, k=3)
            
            if not verses:
                return {"error": "No relevant verses found"}
            
            result = self.generator.generate_answer(query, verses)
            
            return result
            
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            return {"error": str(e)}
    
    def close(self):
        self.retriever.close()

def main():
    pipeline = RAGPipeline()
    
    try:

        query="How can one overcome suffering?"
        result = pipeline.process_query(query)
        print("Question :", query )
        print("Ans :", result)
            
    finally:
        pipeline.close()

if __name__ == "__main__":
    main()
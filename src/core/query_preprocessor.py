from typing import Dict
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging
import nltk

# Download required NLTK data
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
except Exception as e:
    logging.error(f"Failed to download NLTK data: {e}")

class QueryProcessor:
    """Core query processing component"""
    
    def __init__(self):
        """Initialize processor with required resources"""
        try:
            self.stop_words = set(stopwords.words('english'))
            self.question_starters = {
                'what': 'What is the nature of',
                'how': 'How can one achieve',
                'why': 'Why is it important to understand',
                'explain': 'Please explain the concept of',
                'tell': 'Please explain the significance of',
                'meaning': 'What is the deeper meaning of',
            }
            logging.info("QueryProcessor initialized successfully")
        except Exception as e:
            logging.error(f"QueryProcessor initialization failed: {e}")
            raise

    def process_query(self, query: str) -> Dict[str, str]:
        """
        Process and enhance the query
        Returns both original and enhanced versions with word count
        """
        try:
            # Basic cleaning
            cleaned_query = self._clean_text(query)
            
            # Enhance query if needed
            enhanced_query = self._enhance_query(cleaned_query)
            
            # Get word count for response length calculation
            word_count = len(word_tokenize(enhanced_query))
            
            return {
                'original_query': query,
                'processed_query': enhanced_query,
                'word_count': word_count,  # Added this line
                'needs_clarification': self._needs_clarification(enhanced_query)
            }
        except Exception as e:
            logging.error(f"Query processing failed: {e}")
            return {
                'original_query': query,
                'processed_query': query,
                'word_count': len(word_tokenize(query)),
                'needs_clarification': True
            }

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Add question mark if missing
        if not text.endswith('?'):
            text += '?'
        
        # Capitalize first letter
        text = text[0].upper() + text[1:]
        
        return text

    def _enhance_query(self, query: str) -> str:
        """Enhance query with better phrasing"""
        first_word = query.lower().split()[0]
        
        if first_word in self.question_starters:
            query_no_qmark = query[:-1] if query.endswith('?') else query
            rest_of_query = ' '.join(query_no_qmark.split()[1:])
            enhanced = f"{self.question_starters[first_word]} {rest_of_query}?"
            return enhanced
            
        return query

    def _needs_clarification(self, query: str) -> bool:
        """Check if query needs clarification"""
        if len(query.split()) < 3:
            return True
            
        meaningful_words = [word for word in word_tokenize(query.lower()) 
                          if word not in self.stop_words and word.isalnum()]
        
        return len(meaningful_words) < 2
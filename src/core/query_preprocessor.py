from typing import Dict
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging
import nltk

# Ensure NLTK data is available during setup
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
except Exception as e:
    logging.error(f"Failed to download NLTK data: {e}")

class QueryProcessor:
    """Core query processing component for user queries"""
    
    def __init__(self):
        """Initialize processor with stopwords and question starters"""
        try:
            self.stop_words = set(stopwords.words('english'))
            self.question_starters = {
                'what': 'What is the nature of',
                'how': 'How can one achieve',
                'why': 'Why is it important to understand',
                'who': 'Who is considered',
                'where': 'Where can one find guidance on',
                'when': 'When is it appropriate to consider',
                'which': 'Which aspects should be focused on in',
                'explain': 'Please explain the concept of',
                'tell': 'Please explain the significance of',
                'meaning': 'What is the deeper meaning of',
                'describe': 'Describe the principles of',
                'define': 'What is the definition of',
                'is': 'Is there any guidance about',
                'are': 'Are there teachings on',
                'can': 'Can you elaborate on',
                'could': 'Could you clarify the meaning of',
                'should': 'Should one consider the importance of',
                'would': 'Would it be helpful to understand',
            }

            logging.info("QueryProcessor initialized successfully")
        except Exception as e:
            logging.error(f"QueryProcessor initialization failed: {e}")
            raise

    def process_query(self, query: str) -> Dict[str, str]:
        """
        Process and enhance the query.
        Returns both original and enhanced versions with word count and clarification flag.
        """
        try:
            # Basic cleaning
            cleaned_query = self._clean_text(query)
            
            # Enhance query if applicable
            enhanced_query = self._enhance_query(cleaned_query)
            
            # Calculate word count
            word_count = len(word_tokenize(enhanced_query))
            
            # Determine if clarification is needed
            needs_clarification = self._needs_clarification(enhanced_query)
            
            return {
                'original_query': query,
                'processed_query': enhanced_query,
                'word_count': word_count,
                'needs_clarification': needs_clarification
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
        """
        Clean and normalize the query text.
        - Removes extra whitespace.
        - Ensures the text ends with a question mark.
        - Capitalizes the first letter.
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Ensure a question mark at the end
        if not text.endswith('?'):
            text += '?'
        
        # Capitalize the first letter
        text = text[0].upper() + text[1:]
        
        return text

    def _enhance_query(self, query: str) -> str:
        """
        Enhance the query with predefined phrasings for better context.
        If the query starts with a recognized question starter, rephrase it.
        """
        first_word = query.lower().split()[0]
        
        if first_word in self.question_starters:
            query_no_qmark = query[:-1] if query.endswith('?') else query
            rest_of_query = ' '.join(query_no_qmark.split()[1:])
            return f"{self.question_starters[first_word]} {rest_of_query}?"
        
        return query

    def _needs_clarification(self, query: str) -> bool:
        """
        Determine if the query is too vague or lacks enough meaningful words.
        - A query with fewer than 3 words likely needs clarification.
        - A query with fewer than 2 meaningful words also needs clarification.
        """
        if len(query.split()) < 3:
            return True
            
        meaningful_words = [
            word for word in word_tokenize(query.lower()) 
            if word not in self.stop_words and word.isalnum()
        ]
        
        return len(meaningful_words) < 2

from typing import List, Dict, Optional
import logging
from groq import AsyncGroq
from src.config.settings import LLMConfig
from src.config.prompts import PromptTemplates
from src.utils.query_classifier import classify_query
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt', quiet=True)

class WisdomResponseGenerator:
    """Enhanced response generator for Vedic wisdom"""
    
    def __init__(self):
        """Initialize generator with LLM client and templates"""
        try:
            self.api_keys = [LLMConfig.API_KEY1, LLMConfig.API_KEY2, LLMConfig.API_KEY3]
            self.current_key_index = 0
            self.templates = PromptTemplates
            self.client = self._get_client()
            logging.info("WisdomResponseGenerator initialized successfully")
        except Exception as e:
            logging.error(f"Generator initialization failed: {e}")
            self.client = None

    def _get_client(self):
        """Create a client using the current API key"""
        api_key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)  # Increment and reset index
        return AsyncGroq(api_key=api_key)
    
    def _determine_response_length(self, word_count: int) -> int:
        """Determine appropriate response length based on query complexity"""
        # Base token length - adjust these multipliers based on your needs
        base_tokens = max(200, word_count * 50)  # Minimum 200 tokens
        
        # Cap maximum tokens
        return min(base_tokens, 900)  # Maximum 800 tokens

    async def generate_answer(self, query: str, verses: List[Dict],word_count :int) -> Dict:
        """Generate contextual answers from retrieved verses"""
        try:
            if not verses or self.client is None:
                return self._handle_empty_results(verses)

            query_type = classify_query(query)
            if query_type == "non_philosophical":
                return self._generate_clarification_response(query)

            prompt = self._prepare_prompt(query, verses, query_type)
            
            # Determine appropriate response length
            max_tokens = self._determine_response_length(word_count)
            
            response = await self._generate_llm_response(prompt, max_tokens)
            return self._format_response(response, verses)
            
        except Exception as e:
            logging.error(f"Answer generation failed: {e}")
            return self._generate_fallback_response(e, verses)

    def _prepare_prompt(self, query: str, verses: List[Dict], query_type: str) -> str:
        """Prepare contextualized prompt based on query type"""
        verse_citations = self._format_verse_citations(verses[:3])
        
        # Access the template attribute based on query_type
        template = getattr(self.templates, query_type, self.templates.default)
        
        return template.format(query=query, verses=verse_citations)


    async def _generate_llm_response(self, prompt: str, max_tokens: int) -> str:
        """Generate response using LLM with enhanced error handling and validation"""
        try:
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # # Enhanced validation with specific checks
            # if not self._validate_response(response_text):
            #     # Generate a structured fallback response instead of failing
            #     return self._generate_structured_fallback(prompt)
            
            # Ensure complete sentences
            response_text = self._ensure_complete_sentences(response_text)
            
            return self._postprocess_response(response_text)
            
        except Exception as e:
            logging.error(f"LLM response generation failed: {e}")
            return self._generate_structured_fallback(prompt)
    def _format_verse_citations(self, verses: List[Dict]) -> str:
        """Format verses for citation in prompt"""
        citations = []
        for v in verses:
            citation = f"[{v['book']} {v['chapter']}.{v['verse']}]: {v['translation']}\n"
            citation += f"Explanation: {v['explanation']}"
            citations.append(citation)
        return "\n\n".join(citations)

    def _format_response(self, response: str, verses: List[Dict]) -> Dict:
        """Format final response with metadata"""
        return {
            "type": "wisdom_response",
            "verse": verses[0],
            "response": {
                "summary": response,
                "sources": [f"{v['book']} {v['chapter']}.{v['verse']}" for v in verses[:3]]
            }
        }

    def _generate_clarification_response(self, query: str) -> Dict:
        """Generate response for non-philosophical queries"""
        return {
            "type": "clarification",
            "response": {
                "summary": self.templates['clarification'].format(query=query),
                "sources": []
            }
        }

    def _handle_empty_results(self, verses: Optional[List[Dict]]) -> Dict:
        """Handle cases with no relevant verses"""
        if not verses:
            return {
                "type": "wisdom_response",
                "verse": None,
                "response": {
                    "summary": "I apologize, but I couldn't find specific verses that directly address your question. Could you please rephrase or ask about a related topic?",
                    "sources": []
                }
            }
        return {"error": "No relevant verses found"}
    
    def _validate_response(self, response: str) -> bool:
        """Enhanced response validation with detailed checks"""
        if not response:
            logging.warning("Empty response received")
            return False
            
        # Minimum length check (70 words)
        if len(response.split()) < 70:
            logging.warning(f"Response too short: {len(response.split())} words")
            return False
            
        # Check for complete sentences
        if not response.strip().endswith(('.', '?', '!')):
            logging.warning("Response doesn't end with proper punctuation")
            return False
            
        # Check for coherence (at least 2 sentences)
        sentences = response.split('.')
        if len([s for s in sentences if len(s.strip()) > 0]) < 2:
            logging.warning("Response lacks multiple complete sentences")
            return False
            
        # Check for excessive repetition
        words = response.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only check substantial words
                word_freq[word] = word_freq.get(word, 0) + 1
                if word_freq[word] > 3:  # Word appears more than 3 times
                    logging.warning(f"Excessive repetition of word: {word}")
                    return False
                    
        return True
            
    def _ensure_complete_sentences(self, text: str) -> str:
        """Ensure response ends with complete sentences"""
        sentences = sent_tokenize(text)
        
        if not sentences:
            return text
            
        # Keep only complete sentences
        complete_sentences = []
        for sentence in sentences:
            if sentence.strip().endswith(('.', '?', '!')):
                complete_sentences.append(sentence)
            else:
                # If last sentence is incomplete, try to complete it
                if sentence == sentences[-1]:
                    sentence = sentence.strip() + '.'
                complete_sentences.append(sentence)
                
        return ' '.join(complete_sentences)

    def _postprocess_response(self, response: str) -> str:
        """Clean and format the response"""
        import re
        
        # Ensure proper formatting
        response = response.strip()
        
        # Fix common issues
        response = re.sub(r'\s+', ' ', response)  # Fix multiple spaces
        response = re.sub(r'\[\s*(\d+)\s*\]', r'[\1]', response)  # Fix citation spacing
        
        # Ensure proper sentence endings
        response = re.sub(r'([a-z])\s+([A-Z])', r'\1. \2', response)
        
        return response

    def _generate_fallback_response(self) -> str:
            """Generate a fallback response when validation fails"""
            return ("I understand your question and have found relevant wisdom from the texts. "
                    "However, I need to ensure I provide a complete and accurate response. "
                    "Could you please rephrase your question or ask for specific aspects you'd like me to address?")
    
    def _generate_structured_fallback(self, prompt: str) -> str:
        """Generate a structured fallback response"""
        return (
            "Based on the ancient wisdom traditions, I understand your question "
            "about this important topic. While I've found relevant verses that "
            "address this, let me provide a clear and structured response that "
            "captures their essential teachings. The ancient texts emphasize "
            "the importance of approaching this matter with deep understanding "
            "and practical wisdom."
        )
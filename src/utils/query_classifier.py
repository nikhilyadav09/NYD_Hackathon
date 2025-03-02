def classify_query(query: str) -> str:
    """Classify query type for appropriate response generation"""
    # Add query classification logic here
    query_lower = query.lower()
    
    # Check for philosophical keywords
    philosophical_keywords = [
        'meaning', 'truth', 'nature', 'reality', 'consciousness', 'soul', 
        'dharma', 'karma', 'existence', 'purpose', 'wisdom', 'life', 
        'mind', 'self', 'enlightenment', 'essence', 'eternity', 'moksha', 
        'spiritual', 'nirvana', 'atman', 'brahman', 'divine', 'god', 
        'creation', 'cosmos', 'infinite'
    ]
                            
    # Check for practical keywords
    practical_keywords = [
        'how to', 'what should', 'guide', 'help', 'advice', 'practice', 
        'technique', 'method', 'way', 'steps', 'learn', 'teach', 'training', 
        'approach', 'exercise', 'habit', 'improve', 'develop', 'overcome', 
        'reduce', 'solve', 'build', 'start', 'tips', 'tricks'
    ]
                        
    # Classify based on keywords
    if any(keyword in query_lower for keyword in philosophical_keywords):
        return "philosophical"
    elif any(keyword in query_lower for keyword in practical_keywords):
        return "practical"
    elif len(query_lower.split()) < 3:  # Very short queries
        return "clarification"
    else:
        return "default"
class PromptTemplates:
    """Prompt templates for different query types"""
    
    default = """Question: {query}

Relevant verses from ancient texts:
{verses}

Please provide a comprehensive answer that:
1. Directly addresses the question using wisdom from the provided verses
2. Explains the practical application of this wisdom
3. Connects the verses' teachings to the question
4. Do not include verse citations in your response - they will be added automatically

Answer in a clear, conversational style while maintaining philosophical accuracy."""

    philosophical = """Question: {query}

Ancient wisdom relevant to your philosophical inquiry:
{verses}

Please provide a deep philosophical analysis that:
1. Examines the core concepts from these verses
2. Explores the philosophical implications
3. Connects to universal truths
4. Provides practical wisdom for modern life

Reference verses specifically and maintain philosophical rigor while being accessible."""

    practical = """Question: {query}

Practical wisdom from ancient texts:
{verses}

Please provide guidance that:
1. Extracts practical lessons from these verses
2. Offers specific, actionable advice
3. Explains how to apply this wisdom today
4. Addresses real-world challenges

Focus on practical application while preserving the depth of the teachings."""

    clarification = """I notice your question might be about {query}. While I'm knowledgeable about the ancient wisdom of the Bhagavad Gita and Yoga Sutras, I'd be best able to help if you could:

1. Rephrase your question to focus on the philosophical or spiritual aspects
2. Ask about specific teachings or principles
3. Seek guidance on applying ancient wisdom to this topic

Would you like to rephrase your question to explore the deeper wisdom these texts offer?"""
import asyncio
from typing import List, Dict
import json
import logging
from tqdm import tqdm
from src.core.pipeline import VedicWisdomPipeline
from src.evaluation.evaluator import WisdomEvaluator

async def run_evaluation(test_queries: List[str], model_name: str):
    """Run evaluation pipeline"""
    pipeline = VedicWisdomPipeline()
    evaluator = WisdomEvaluator()
    test_cases = []
    
    print(f"Running evaluation for model: {model_name}")
    for query in tqdm(test_queries):
        try:
            # Get response from pipeline
            response = await pipeline.process_query(query)
            
            if 'error' in response:
                logging.error(f"Error processing query '{query}': {response['error']}")
                continue
                
            test_case = {
                'query': query,
                'generated_response': response['response']['summary'],
                'reference_verse': response['verse']
            }
            test_cases.append(test_case)
            
        except Exception as e:
            logging.error(f"Error processing query '{query}': {e}")
            continue
    
    # Evaluate all test cases
    results_df = evaluator.batch_evaluate(test_cases)
    summary = evaluator.save_results(results_df, model_name)
    
    print("\nEvaluation Results Summary:")
    print(json.dumps(summary, indent=2))
    return summary

# Sample test queries
TEST_QUERIES = [
    # From the first group
    "Why was Krishna teaching Yoga to Arjuna?",
    "Why was Arjuna so grief-stricken?",
    "Where did Krishna place the chariot?",
    "Why was Arjuna scared after seeing Krishna's divine form?",
    "Why should we worship God?",
    
    # From the second group
    "What is the purpose of Yoga?",
    "What is the end result of Yoga practice?",
    "What is right perception?",
    "What are the five kinds of thoughts in Yoga?",
    "What is Ego?"
]


if __name__ == "__main__":
    asyncio.run(run_evaluation(TEST_QUERIES, "llama-3.3-70b-versatile"))
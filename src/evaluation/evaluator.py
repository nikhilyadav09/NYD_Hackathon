import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
import pandas as pd
from typing import List, Dict
import json
import logging

class WisdomEvaluator:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        # Load reference questions and translations
        self.bhagavad_gita_refs = pd.read_csv('/home/nikhil/sitare /others/NYD_Hackathon/data/Bhagwad_Gita_Verses_English_Questions.csv')
        self.yoga_sutras_refs = pd.read_csv('/home/nikhil/sitare /others/NYD_Hackathon/data/Bhagwad_Gita_Verses_English_Questions.csv')
        
    def find_matching_reference(self, query: str) -> Dict:
        """Find matching reference question and translation from CSV files"""
        # Calculate similarity with all questions from both sources
        gita_similarities = self.calculate_batch_similarities(query, self.bhagavad_gita_refs['question'].tolist())
        yoga_similarities = self.calculate_batch_similarities(query, self.yoga_sutras_refs['question'].tolist())
        
        # Find best match across both sources
        if max(gita_similarities) > max(yoga_similarities):
            idx = np.argmax(gita_similarities)
            ref = self.bhagavad_gita_refs.iloc[idx]
            source = 'bhagavad_gita'
        else:
            idx = np.argmax(yoga_similarities)
            ref = self.yoga_sutras_refs.iloc[idx]
            source = 'yoga_sutras'
            
        return {
            'question': ref['question'],
            'translation': ref['translation'],
            'source': source,
            'chapter': ref['chapter'],
            'verse': ref['verse'],
            'similarity_score': max(max(gita_similarities), max(yoga_similarities))
        }
    
    def calculate_batch_similarities(self, query: str, references: List[str]) -> List[float]:
        """Calculate semantic similarities between query and multiple references"""
        query_emb = self.model.encode([query])
        ref_emb = self.model.encode(references)
        return cosine_similarity(query_emb, ref_emb)[0]

    def calculate_semantic_similarity(self, generated: str, reference: str) -> float:
        """Calculate semantic similarity using sentence embeddings"""
        try:
            gen_emb = self.model.encode([generated])
            ref_emb = self.model.encode([reference])
            return float(cosine_similarity(gen_emb, ref_emb)[0][0])
        except Exception as e:
            logging.error(f"Error calculating semantic similarity: {e}")
            return 0.0

    def calculate_bleu_score(self, generated: str, reference: str) -> float:
        """Calculate BLEU score"""
        try:
            reference = reference.split()
            generated = generated.split()
            return sentence_bleu([reference], generated)
        except Exception as e:
            logging.error(f"Error calculating BLEU score: {e}")
            return 0.0

    def calculate_rouge_scores(self, generated: str, reference: str) -> Dict[str, float]:
        """Calculate ROUGE scores"""
        try:
            scores = self.rouge_scorer.score(reference, generated)
            return {
                'rouge1': scores['rouge1'].fmeasure,
                'rouge2': scores['rouge2'].fmeasure,
                'rougeL': scores['rougeL'].fmeasure
            }
        except Exception as e:
            logging.error(f"Error calculating ROUGE scores: {e}")
            return {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}

    def evaluate_response(self, query: str, generated_response: str) -> Dict:
        """Evaluate a single response against matched reference"""
        # Find matching reference question and translation
        reference = self.find_matching_reference(query)
        
        return {
            'reference_question': reference['question'],
            'reference_translation': reference['translation'],
            'reference_source': reference['source'],
            'reference_chapter': reference['chapter'],
            'reference_verse': reference['verse'],
            'question_match_score': reference['similarity_score'],
            'semantic_similarity': self.calculate_semantic_similarity(generated_response, reference['translation']),
            'bleu_score': self.calculate_bleu_score(generated_response, reference['translation']),
            **self.calculate_rouge_scores(generated_response, reference['translation'])
        }

    def batch_evaluate(self, test_cases: List[Dict]) -> pd.DataFrame:
        """Evaluate multiple test cases and return results DataFrame"""
        results = []
        
        for case in test_cases:
            try:
                metrics = self.evaluate_response(case['query'], case['generated_response'])
                results.append({
                    'query': case['query'],
                    **metrics
                })
            except Exception as e:
                logging.error(f"Error evaluating case: {e}")
                continue
        
        return pd.DataFrame(results)

    def save_results(self, results: pd.DataFrame, model_name: str):
        """Save evaluation results to file"""
        filename = f"evaluation_results_{model_name}.csv"
        results.to_csv(filename, index=False)
        
        # Calculate and save summary statistics
        summary = {
            'model_name': model_name,
            'average_semantic_similarity': float(results['semantic_similarity'].mean()),
            'average_bleu_score': float(results['bleu_score'].mean()),
            'average_rouge1': float(results['rouge1'].mean()),
            'average_rouge2': float(results['rouge2'].mean()),
            'average_rougeL': float(results['rougeL'].mean()),
            'average_question_match_score': float(results['question_match_score'].mean()),
            'num_samples': len(results)
        }
        
        with open(f"evaluation_summary_{model_name}.json", 'w') as f:
            json.dump(summary, f, indent=2)
            
        return summary
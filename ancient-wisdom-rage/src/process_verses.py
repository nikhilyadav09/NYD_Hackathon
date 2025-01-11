import pandas as pd
from sentence_transformers import SentenceTransformer
import logging
import torch
from typing import List, Dict
import numpy as np
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

class VersesProcessor:
    def __init__(self, batch_size: int = 32):
        self.batch_size = batch_size
        # Check if CUDA is available and has enough memory
        if torch.cuda.is_available():
            try:
                # Try to initialize model with CUDA
                self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
                logging.info("Using CUDA for processing")
            except RuntimeError:
                # Fall back to CPU if CUDA initialization fails
                self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                logging.info("Falling back to CPU due to CUDA memory constraints")
        else:
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            logging.info("Using CPU for processing")

    def split_questions(self, text: str) -> List[str]:
        """Split multiple questions into individual ones and validate"""
        if not isinstance(text, str):
            return []
        questions = [q.strip() + '?' for q in text.split('?') if q.strip()]
        return questions if questions else [text]

    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings in batches to manage memory"""
        embeddings = []
        
        try:
            for i in tqdm(range(0, len(texts), self.batch_size), desc="Batches"):
                batch = texts[i:i + self.batch_size]
                batch_embeddings = self.model.encode(batch, convert_to_numpy=True)
                embeddings.extend(batch_embeddings)
            
            return np.array(embeddings)
        except Exception as e:
            logging.error(f"Error generating embeddings: {str(e)}")
            # Return zero embeddings as fallback
            return np.zeros((len(texts), self.model.get_sentence_embedding_dimension()))

    def process_file(self, file_path: str) -> pd.DataFrame:
        try:
            # Read the CSV file
            logging.info(f"Reading file: {file_path}")
            df = pd.read_csv(file_path)
            logging.info(f"Original rows: {len(df)}")
            
            # Create expanded rows for multiple questions
            expanded_rows: List[Dict] = []
            for _, row in df.iterrows():
                questions = self.split_questions(row['question'])
                for question in questions:
                    try:
                        expanded_rows.append({
                            'chapter': row['chapter'],
                            'verse': row['verse'],
                            'sanskrit': row.get('sanskrit', ''),  # Handle optional columns
                            'translation': row['translation'],
                            'question': question
                        })
                    except Exception as e:
                        logging.error(f"Error processing row: {row}, Error: {str(e)}")
                        continue
            
            # Create new dataframe with expanded rows
            processed_df = pd.DataFrame(expanded_rows)
            logging.info(f"Processed rows after splitting questions: {len(processed_df)}")
            
            # Generate embeddings for translations in batches
            logging.info("Generating embeddings for translations...")
            translation_embeddings = self.generate_embeddings_batch(processed_df['translation'].tolist())
            
            # Convert embeddings to list format for storage
            processed_df['embedding'] = list(translation_embeddings)
            
            return processed_df
            
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")
            raise

def main():
    # Initialize processor with smaller batch size if memory is constrained
    processor = VersesProcessor(batch_size=16)
    
    files = {
        'gita': '/home/nikhil/sitare /others/NYD_hacathone/ancient-wisdom-rag/data/Bhagwad_Gita_Verses_English_Questions.csv',
        'yoga': '/home/nikhil/sitare /others/NYD_hacathone/ancient-wisdom-rag/data/Patanjali_Yoga_Sutras_Verses_English_Questions.csv'
    }
    
    for name, file_path in files.items():
        try:
            output_path = f'/home/nikhil/sitare /others/NYD_hacathone/ancient-wisdom-rag/data/processed_{name}.csv'
            
            df = processor.process_file(file_path)
            df.to_csv(output_path, index=False)
            logging.info(f"Saved processed {name} data to {output_path}")
            
            # Print sample to verify
            print(f"\nSample of processed {name} data:")
            print(df[['chapter', 'verse', 'question']].head())
            print(f"Total rows in processed {name} data: {len(df)}")
            
        except Exception as e:
            logging.error(f"Error processing {name} file: {str(e)}")
            continue

if __name__ == "__main__":
    main()
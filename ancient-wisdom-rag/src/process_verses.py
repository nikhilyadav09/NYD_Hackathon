import pandas as pd
from sentence_transformers import SentenceTransformer
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

class VersesProcessor:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def split_questions(self, text):
        """Split multiple questions into individual ones"""
        return [q.strip() + '?' for q in text.split('?') if q.strip()]
    
    def process_file(self, file_path):
        # Read the CSV file
        logging.info(f"Reading file: {file_path}")
        df = pd.read_csv(file_path)
        logging.info(f"Original rows: {len(df)}")
        
        # Create expanded rows for multiple questions
        expanded_rows = []
        for _, row in df.iterrows():
            questions = self.split_questions(row['question'])
            for question in questions:
                expanded_rows.append({
                    'chapter': row['chapter'],
                    'verse': row['verse'],
                    'sanskrit': row['sanskrit'],
                    'translation': row['translation'],
                    'question': question
                })
        
        # Create new dataframe with expanded rows
        processed_df = pd.DataFrame(expanded_rows)
        logging.info(f"Processed rows after splitting questions: {len(processed_df)}")
        
        # Generate embeddings for translations only
        logging.info("Generating embeddings for translations...")
        translation_embeddings = self.model.encode(processed_df['translation'].tolist())
        processed_df['embedding'] = translation_embeddings.tolist()
        
        return processed_df

def main():
    processor = VersesProcessor()
    
    # Process Gita file
    try:
        gita_df = processor.process_file('/home/nikhil/sitare /others/NYD_hacathone/ancient-wisdom-rag/data/Bhagwad_Gita_Verses_English_Questions.csv')
        gita_df.to_csv('/home/nikhil/sitare /others/NYD_hacathone/ancient-wisdom-rag/data/processed_gita.csv', index=False)
        logging.info("Saved processed Gita data")
        
        # Print sample to verify
        print("\nSample of processed Gita data:")
        print(gita_df[['chapter', 'verse', 'question']].head())
        print(f"Total rows in processed Gita data: {len(gita_df)}")
        
    except Exception as e:
        logging.error(f"Error processing Gita file: {e}")
    
    # Process Yoga Sutras file
    try:
        yoga_df = processor.process_file('/home/nikhil/sitare /others/NYD_hacathone/ancient-wisdom-rag/data/Patanjali_Yoga_Sutras_Verses_English_Questions.csv')
        yoga_df.to_csv('/home/nikhil/sitare /others/NYD_hacathone/ancient-wisdom-rag/data/processed_yoga_sutras.csv', index=False)
        logging.info("Saved processed Yoga Sutras data")
        
        # Print sample to verify
        print("\nSample of processed Yoga Sutras data:")
        print(yoga_df[['chapter', 'verse', 'question']].head())
        print(f"Total rows in processed Yoga Sutras data: {len(yoga_df)}")
        
    except Exception as e:
        logging.error(f"Error processing Yoga Sutras file: {e}")

if __name__ == "__main__":
    main()
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import logging
import sys
import ast

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_embedding_string_to_list(embedding_str):
    """Convert embedding string to list of floats"""
    try:
        # If it's already a list, return it
        if isinstance(embedding_str, list):
            return embedding_str
        # Otherwise, safely evaluate the string representation
        return ast.literal_eval(embedding_str)
    except:
        logging.error(f"Error converting embedding: {embedding_str[:100]}...")
        raise

def verify_data_files():
    """Verify the processed data files exist and have correct structure"""
    try:
        gita_path = '/home/nikhil/sitare /others/NYD_hacathone/ancient-wisdom-rag/data/processed_gita.csv'
        yoga_path = '/home/nikhil/sitare /others/NYD_hacathone/ancient-wisdom-rag/data/processed_yoga_sutras.csv'
        
        gita_df = pd.read_csv(gita_path)
        yoga_df = pd.read_csv(yoga_path)
        
        # Convert embedding strings to lists
        gita_df['embedding'] = gita_df['embedding'].apply(convert_embedding_string_to_list)
        yoga_df['embedding'] = yoga_df['embedding'].apply(convert_embedding_string_to_list)
        
        required_columns = ['chapter', 'verse', 'sanskrit', 'translation', 'embedding', 'question']
        for df, name in [(gita_df, 'Gita'), (yoga_df, 'Yoga Sutras')]:
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"{name} dataset missing columns: {missing_cols}")
            
            # Verify data types
            assert df['chapter'].dtype in ['int64', 'float64'], f"Chapter column in {name} must be numeric"
            assert all(isinstance(x, list) for x in df['embedding']), f"Embeddings in {name} must be lists"
        
        return gita_df, yoga_df
        
    except Exception as e:
        logging.error(f"Error verifying data files: {e}")
        raise

def setup_database():
    """Setup database with correct schema"""
    conn = psycopg2.connect(
        dbname="ancient_wisdom",
        user="postgres",
        password="Nikhil@930",
        host="localhost"
    )
    cur = conn.cursor()
    
    # Enable pgvector extension if not already enabled
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Drop existing tables if they exist
    cur.execute("""
    DROP TABLE IF EXISTS questions CASCADE;
    DROP TABLE IF EXISTS verses CASCADE;
    """)
    
    # Create verses table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS verses (
        id SERIAL PRIMARY KEY,
        chapter INTEGER,
        verse TEXT,
        sanskrit TEXT,
        translation TEXT,
        embedding vector(384)
    );
    """)
    
    # Create questions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id SERIAL PRIMARY KEY,
        verse_id INTEGER REFERENCES verses(id),
        question TEXT
    );
    """)
    
    # Create vector similarity search index
    cur.execute("""
    CREATE INDEX embedding_idx ON verses USING ivfflat (embedding vector_cosine_ops);
    """)
    
    conn.commit()
    return conn, cur

def insert_dataset(conn, cur, df, source_name):
    """Insert a single dataset into database"""
    try:
        # Insert verses first
        unique_verses = df.drop_duplicates(['chapter', 'verse'])
        verse_data = []
        
        for _, row in unique_verses.iterrows():
            # Convert chapter to int if it's float
            chapter = int(row['chapter'])
            verse_data.append((
                chapter,
                str(row['verse']),  # Ensure verse is string
                row['sanskrit'],
                row['translation'],
                row['embedding']
            ))
        
        logging.info(f"Inserting {len(verse_data)} verses from {source_name}")
        
        # Insert verses and get their IDs
        execute_values(
            cur,
            """
            INSERT INTO verses (chapter, verse, sanskrit, translation, embedding)
            VALUES %s
            RETURNING id, chapter, verse
            """,
            verse_data,
            template='(%s, %s, %s, %s, %s)'
        )
        
        verse_ids = cur.fetchall()
        verse_id_map = {(int(c), str(v)): id for id, c, v in verse_ids}
        
        # Insert questions
        question_data = []
        for _, row in df.iterrows():
            chapter = int(row['chapter'])
            verse = str(row['verse'])
            if (chapter, verse) in verse_id_map:
                question_data.append((
                    verse_id_map[(chapter, verse)],
                    row['question']
                ))
        
        logging.info(f"Inserting {len(question_data)} questions from {source_name}")
        
        if question_data:
            execute_values(
                cur,
                "INSERT INTO questions (verse_id, question) VALUES %s",
                question_data,
                template='(%s, %s)'
            )
        
        conn.commit()
        logging.info(f"Successfully inserted {source_name} data")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error inserting {source_name} data: {e}")
        raise

def verify_insertion(conn, cur):
    """Verify data was inserted correctly"""
    cur.execute("SELECT count(*) FROM verses")
    verse_count = cur.fetchone()[0]
    
    cur.execute("SELECT count(*) FROM questions")
    question_count = cur.fetchone()[0]
    
    logging.info(f"Database contains {verse_count} verses and {question_count} questions")
    
    # Sample check
    cur.execute("""
    SELECT v.chapter, v.verse, v.translation, q.question 
    FROM verses v 
    JOIN questions q ON v.id = q.verse_id 
    LIMIT 3
    """)
    
    logging.info("\nSample data:")
    for row in cur.fetchall():
        logging.info(f"Chapter {row[0]}, Verse {row[1]}")
        logging.info(f"Translation: {row[2]}")
        logging.info(f"Question: {row[3]}\n")

def main():
    try:
        # First verify data files
        logging.info("Verifying data files...")
        gita_df, yoga_df = verify_data_files()
        
        # Setup database
        logging.info("Setting up database...")
        conn, cur = setup_database()
        
        # Insert data
        insert_dataset(conn, cur, gita_df, "Bhagavad Gita")
        insert_dataset(conn, cur, yoga_df, "Yoga Sutras")
        
        # Verify insertion
        verify_insertion(conn, cur)
        
        logging.info("Process completed successfully!")
        
    except Exception as e:
        logging.error(f"Error in main process: {e}")
        sys.exit(1)
        
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    main()
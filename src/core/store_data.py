import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import logging
import sys
from sentence_transformers import SentenceTransformer
import numpy as np
import torch
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_embeddings(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """Generate embeddings for given texts using sentence-transformers with batching"""
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Using device: {device}")
        model = SentenceTransformer('all-MiniLM-L6-v2').to(device)

        if isinstance(texts, str):
            texts = [texts]

        embeddings = []
        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch = texts[i:i + batch_size]
            try:
                batch_embeddings = model.encode(batch, device=device)
                embeddings.extend(batch_embeddings.tolist())
            except RuntimeError as e:
                if "out of memory" in str(e):
                    logging.warning("CUDA out of memory, falling back to CPU")
                    torch.cuda.empty_cache()
                    model = model.to("cpu")
                    batch_embeddings = model.encode(batch)
                    embeddings.extend(batch_embeddings.tolist())
                else:
                    raise e
        
        return embeddings[0] if len(embeddings) == 1 else embeddings

    except Exception as e:
        logging.error(f"Error generating embeddings: {e}")
        return None

def verify_data_files() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Verify the processed data files exist and have correct structure"""
    try:
        gita_path = '/home/nikhil/sitare /others/NYD_Hackathon/data/processed_bhagwat_gita.csv'
        yoga_path = '/home/nikhil/sitare /others/NYD_Hackathon/data/processed_yoga_sutra.csv'

        gita_df = pd.read_csv(gita_path)
        yoga_df = pd.read_csv(yoga_path)

        gita_df['book'] = 'Bhagavad Gita'
        yoga_df['book'] = 'Yoga Sutras'

        logging.info("Generating embeddings for Bhagavad Gita...")
        gita_df['embedding'] = generate_embeddings(gita_df['explanation'].tolist())

        logging.info("Generating embeddings for Yoga Sutras...")
        yoga_df['embedding'] = generate_embeddings(yoga_df['explanation'].tolist())

        required_columns = ['book', 'chapter', 'verse', 'sanskrit', 'translation', 'explanation']
        for df, name in [(gita_df, 'Gita'), (yoga_df, 'Yoga Sutras')]:
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"{name} dataset missing columns: {missing_cols}")

            df['chapter'] = pd.to_numeric(df['chapter'], errors='coerce')
            missing_embeddings = df[df['embedding'].isnull()]
            if not missing_embeddings.empty:
                logging.warning(f"{len(missing_embeddings)} rows in {name} dataset have missing embeddings and will be removed.")
            df.dropna(subset=['embedding'], inplace=True)

        return gita_df, yoga_df

    except Exception as e:
        logging.error(f"Error verifying data files: {e}")
        raise

def setup_database():
    """Setup database with correct schema"""
    try:
        conn = psycopg2.connect(
            dbname="ancient_wisdoms",
            user="postgres",
            password= 'Nikhil@930',
            host="localhost"
        )
        cur = conn.cursor()

        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("DROP TABLE IF EXISTS verses CASCADE;")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS verses (
            id SERIAL PRIMARY KEY,
            book TEXT,
            chapter INTEGER,
            verse TEXT,
            sanskrit TEXT,
            translation TEXT,
            explanation TEXT,
            embedding vector(384)
        );
        """)

        cur.execute("""
        CREATE INDEX embedding_idx ON verses USING ivfflat (embedding vector_cosine_ops);
        """)

        conn.commit()
        return conn, cur

    except Exception as e:
        logging.error(f"Error setting up database: {e}")
        raise

def insert_dataset(conn, cur, df: pd.DataFrame, source_name: str):
    """Insert a single dataset into the database"""
    try:
        verse_data = []
        for _, row in df.iterrows():
            chapter = int(row['chapter'])
            verse_data.append((
                row['book'],
                chapter,
                str(row['verse']),
                row['sanskrit'],
                row['translation'],
                row['explanation'],
                row['embedding']
            ))

        logging.info(f"Inserting {len(verse_data)} verses from {source_name}")

        execute_values(
            cur,
            """
            INSERT INTO verses (book, chapter, verse, sanskrit, translation, explanation, embedding)
            VALUES %s
            """,
            verse_data,
            template='(%s, %s, %s, %s, %s, %s, %s)'
        )

        conn.commit()
        logging.info(f"Successfully inserted {source_name} data")

    except Exception as e:
        conn.rollback()
        logging.error(f"Error inserting {source_name} data: {e}")
        raise

def verify_insertion(conn, cur):
    """Verify data was inserted correctly"""
    try:
        cur.execute("SELECT COUNT(*), book FROM verses GROUP BY book")
        verse_counts = cur.fetchall()

        logging.info("\nDatabase contents:")
        for count, book in verse_counts:
            logging.info(f"{book}: {count} verses")

        cur.execute("""
        SELECT book, chapter, verse, translation, explanation 
        FROM verses 
        LIMIT 3
        """)

        logging.info("\nSample data:")
        for row in cur.fetchall():
            logging.info(f"Book: {row[0]}")
            logging.info(f"Chapter {row[1]}, Verse {row[2]}")
            logging.info(f"Translation: {row[3]}")
            logging.info(f"Explanation: {row[4]}\n")

    except Exception as e:
        logging.error(f"Error verifying insertion: {e}")
        raise

def main():
    try:
        logging.info("Verifying data files...")
        gita_df, yoga_df = verify_data_files()

        logging.info("Setting up database...")
        conn, cur = setup_database()

        insert_dataset(conn, cur, gita_df, "Bhagavad Gita")
        insert_dataset(conn, cur, yoga_df, "Yoga Sutras")

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

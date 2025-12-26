import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import os
import sys
import glob

# Fix path to import backend settings
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from backend.config import settings

def build_vector_db():
    print(f"🧠 Initializing ChromaDB at: {settings.CHROMA_PATH}")
    
    # 1. Setup Client
    client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    
    # 2. Setup Embedding Function (Must match what is used in rag_engine.py!)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=settings.EMBEDDING_MODEL
    )

    # 3. Reset Collection (Clean Start)
    try:
        client.delete_collection(name="vedic_wisdom")
        print("🗑️  Deleted old collection.")
    except Exception:
        pass

    collection = client.create_collection(
        name="vedic_wisdom",
        embedding_function=sentence_transformer_ef,
        metadata={"description": "Vedic Wisdom Multi-Source"}
    )

    # 4. Find all CSVs in data folder
    csv_pattern = os.path.join(settings.DATA_DIR, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    print(f"📂 Found {len(csv_files)} datasets: {[os.path.basename(f) for f in csv_files]}")

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        print(f"⚡ Indexing {file_name}...")
        
        df = pd.read_csv(file_path)
        
        documents = []
        metadatas = []
        ids = []

        for index, row in df.iterrows():
            # Determine source name
            if "source" in row:
                source_text = row['source']
            else:
                source_text = "Yoga Sutras" if "sutras" in file_name else "Bhagavad Gita"

            # Create the text to be embedded (Rich Context)
            text_to_embed = f"{row['translation']} (Sanskrit: {row['sanskrit']})"
            
            documents.append(text_to_embed)
            
            metadatas.append({
                "chapter": row['chapter'],
                "verse": row['verse'],
                "sanskrit": str(row['sanskrit']),
                "source": source_text
            })
            
            # Unique ID: Gita_1_1
            ids.append(f"{source_text}_{row['chapter']}_{row['verse']}")

        # Batch Insert (Chroma handles batching efficiently)
        if documents:
            collection.add(documents=documents, metadatas=metadatas, ids=ids)
            print(f"   --> Added {len(documents)} verses.")

    print("\n✅ Database built successfully!")

if __name__ == "__main__":
    build_vector_db()
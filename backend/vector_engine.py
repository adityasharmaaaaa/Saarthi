import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import os
import glob 

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
DATA_FOLDER = os.path.join(project_root, "data")
CHROMA_PATH = os.path.join(project_root, "chroma_db")
COLLECTION_NAME = "vedic_wisdom"

def build_vector_db():
    print(f"🧠 Initializing ChromaDB at: {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Reset Collection
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("🗑️  Deleted existing collection to rebuild.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef,
        metadata={"description": "Vedic Wisdom Multi-Source"}
    )

    csv_files = glob.glob(os.path.join(DATA_FOLDER, "*.csv"))
    print(f"📂 Found {len(csv_files)} datasets: {[os.path.basename(f) for f in csv_files]}")

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        print(f"⚡ Indexing {file_name}...")
        
        df = pd.read_csv(file_path)
        
        documents = []
        metadatas = []
        ids = []

        for index, row in df.iterrows():
            source_text = "Yoga Sutras" if "sutras" in file_name else "Bhagavad Gita"
            text_to_embed = f"{row['translation']} (Source: {source_text}, Sanskrit: {row['sanskrit']})"
            documents.append(text_to_embed)
            
            metadatas.append({
                "chapter": row['chapter'],
                "verse": row['verse'],
                "sanskrit": row['sanskrit'],
                "translation": row['translation'],
                "source": source_text # <--- CRITICAL NEW FIELD
            })
            
            ids.append(f"{source_text}_{row['chapter']}_{row['verse']}")

        # Batch Insert
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"   --> Added {len(documents)} items.")

    print("✅ All data indexed successfully!")

if __name__ == "__main__":
    build_vector_db()
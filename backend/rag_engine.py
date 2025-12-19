import os
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv
import re
import pandas as pd
import glob

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
CHROMA_PATH = os.path.join(project_root, "chroma_db")
DATA_FOLDER = os.path.join(project_root, "data")
COLLECTION_NAME = "vedic_wisdom"

# Initialize Clients
client = chromadb.PersistentClient(path=CHROMA_PATH)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)

groq_client = Groq(api_key=GROQ_API_KEY)

def check_for_exact_reference(query):
    """
    SCHOLAR MODE: Detects '2.47' or 'Chapter 2 Verse 47' and fetches EXACT row.
    """
    # Regex 1: Matches "2.47" or "2:47"
    simple_pattern = re.search(r"(\d+)[\.:](\d+)", query)
    
    # Regex 2: Matches "Chapter 2 Verse 47" (flexible spacing)
    verbose_pattern = re.search(r"chapter\s*(\d+).*verse\s*(\d+)", query, re.IGNORECASE)
    
    match = simple_pattern or verbose_pattern
    
    if match:
        target_ch = int(match.group(1))
        target_v = int(match.group(2))
        print(f"📚 Scholar Mode Activated: Looking for Ch {target_ch}, Verse {target_v}...")
        
        found_verses = []
        
        # Look through ALL CSV files (Gita, Sutras, etc.)
        csv_files = glob.glob(os.path.join(DATA_FOLDER, "*.csv"))
        
        for file_path in csv_files:
            try:
                df = pd.read_csv(file_path)
                # Filter for the specific chapter and verse
                row = df[(df['chapter'] == target_ch) & (df['verse'] == target_v)]
                
                if not row.empty:
                    # Determine source name from filename
                    filename = os.path.basename(file_path).lower()
                    source_name = "Yoga Sutras" if "sutra" in filename else "Bhagavad Gita"
                    
                    text = row.iloc[0]['translation']
                    sanskrit = row.iloc[0]['sanskrit']
                    
                    found_verses.append(f"**{source_name} {target_ch}.{target_v}**\nSanskrit: {sanskrit}\nTranslation: {text}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                
        if found_verses:
            return "\n\n".join(found_verses)
            
    return None

def retrieve_verses(query, n_results=3):
    """
    Hybrid Retrieval: Tries Exact Match first, then Vector Search.
    """
    # 1. Try Scholar Mode (Exact Match)
    exact_match = check_for_exact_reference(query)
    if exact_match:
        return exact_match, ["Direct Reference (Scholar Mode)"]

    # 2. Fallback to Vector Search (Semantic)
    results = collection.query(query_texts=[query], n_results=n_results)
    
    context_text = ""
    sources = []
    
    for i in range(len(results['ids'][0])):
        meta = results['metadatas'][0][i]
        source_label = meta.get('source', 'Unknown')
        verse_id = f"{source_label} {meta['chapter']}.{meta['verse']}"
        text = f"{verse_id}: {meta['translation']}\n"
        
        context_text += text
        sources.append(verse_id)
        
    return context_text, sources

def generate_answer(user_query, chat_history=[]):
    print(f"🔍 Processing: '{user_query}'...")
    
    # 1. RETRIEVE
    context, sources = retrieve_verses(user_query)
    
    # 2. AUGMENT
    system_prompt = """
    You are a wise Vedic Counselor. 
    Use the provided text to answer the user.
    
    - If the user asked for a specific verse (Scholar Mode), explain it deeply.
    - If the user asked a general question, use the verses to provide guidance.
    - Always remain empathetic and grounded in the text.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    
    final_user_content = f"""
    Reference Material:
    {context}
    
    User Input: {user_query}
    """
    messages.append({"role": "user", "content": final_user_content})
    
    # 3. GENERATE
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.5,
        )
        answer = chat_completion.choices[0].message.content
        return answer, sources
    except Exception as e:
        return f"Error connecting to AI: {e}", []
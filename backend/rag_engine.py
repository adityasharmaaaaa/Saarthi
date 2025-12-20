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
    simple_pattern = re.search(r"(\d+)[\.:](\d+)", query)
    verbose_pattern = re.search(r"chapter\s*(\d+).*verse\s*(\d+)", query, re.IGNORECASE)
    
    match = simple_pattern or verbose_pattern
    
    if match:
        target_ch = int(match.group(1))
        target_v = int(match.group(2))
        print(f"📚 Scholar Mode Activated: Looking for Ch {target_ch}, Verse {target_v}...")
        
        found_verses = []
        
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

def generate_answer(user_query, chat_history=[], mode="Beginner"):
    if not groq_client:
        return "⚠️ System Error: GROQ_API_KEY is missing.", []

    print(f"🔍 Processing ({mode} Mode): '{user_query}'...")
    
    context, sources = retrieve_verses(user_query)
    
    # DYNAMIC SYSTEM PROMPT
    if mode == "Scholar":
        tone_instruction = """
        - You are a Pundit and Vedantic Scholar.
        - Use precise Sanskrit terminology (e.g., 'Dharma', 'Gunas', 'Vrittis').
        - Explain the verse with deep philosophical rigor.
        - Quote the texts formally.
        """
    else: # Beginner
        tone_instruction = """
        - You are a friendly Guide explaining to a complete beginner.
        - Use simple English and modern analogies (like work, sports, or technology).
        - Avoid heavy jargon unless you explain it.
        - Focus on practical application in daily life.
        """

    system_prompt = f"""
    You are 'Saarthi', a wise Vedic Counselor.
    {tone_instruction}
    
    Use the provided reference text to answer the user.
    - If the context contains a "Direct Reference", explain that specific verse.
    - If the context is a general search, guide the user empathically.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    
    final_user_content = f"""
    Reference Material:
    {context}
    
    User Input: {user_query}
    """
    messages.append({"role": "user", "content": final_user_content})
    
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
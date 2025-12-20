import os
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# 1. SETUP
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    groq_client = None

# 2. VECTOR DB SETUP
# We use a persistent client so we don't have to rebuild the DB every time
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'chroma_db')
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="vedic_knowledge")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_verses(query, n_results=3):
    """
    Finds the most relevant verses from the Vector DB.
    """
    query_embedding = embedder.encode([query]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    
    context_text = ""
    sources = []
    
    if results['documents']:
        for i, doc in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][i]
            ref = f"{meta['source']} {meta['chapter']}.{meta['verse']}"
            context_text += f"[{ref}] {doc}\n\n"
            sources.append(ref)
            
    return context_text, sources

def generate_answer(user_query, chat_history=[], mode="Beginner"):
    """
    Generates an answer using Groq (Llama-3), referencing the retrieved verses.
    Now supports 'mode' for adaptive complexity.
    """
    if not groq_client:
        return "⚠️ System Error: GROQ_API_KEY is missing.", []

    # 1. Retrieve Context
    context, sources = retrieve_verses(user_query)
    
    # 2. Define Tone based on Mode
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

    # 3. Construct Prompt
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
    
    # 4. Call LLM
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
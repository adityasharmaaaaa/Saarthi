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
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'chroma_db')
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="vedic_knowledge")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_verses(query, n_results=3):
    """
    Finds the most relevant verses from the Vector DB.
    """
    try:
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
                ref = f"{meta.get('source', 'Scripture')} {meta.get('chapter', '?')}.{meta.get('verse', '?')}"
                context_text += f"[{ref}] {doc}\n\n"
                sources.append(ref)
                
        return context_text, sources
    except Exception as e:
        print(f"Retrieval Error: {e}")
        return "", []

def generate_answer(user_query, chat_history=[], mode="Beginner", language="English", focus="General"):
    """
    Generates an answer with specific Focus Modes (Relationships, Work, etc.)
    """
    if not groq_client:
        return "⚠️ System Error: GROQ_API_KEY is missing.", []

    # 1. Retrieve Context
    context, sources = retrieve_verses(user_query)
    
    # 2. Language Setup
    lang_instruction = "Answer strictly in Hindi (Devanagari)." if language == "Hindi" else "Answer in English."

    # 3. Tone & Focus Setup
    if mode == "Scholar":
        tone = "You are a Vedantic Scholar. Use precise Sanskrit terms and deep philosophical rigor."
    else:
        tone = "You are a friendly Guide. Use simple analogies and focus on practical application."

    # Focus Mode Logic (The New Feature)
    if focus == "Relationships":
        focus_instruction = """
        - Focus on Dharma in relationships (Parenting, Marriage, Friendship).
        - Draw examples from the Ramayana (Maryada Purushottam Ram) and Mahabharata (Family duty).
        - Emphasize empathy, duty (Kartavya), and detachment (Anasakti).
        """
    elif focus == "Work/Career":
        focus_instruction = """
        - Focus on Karma Yoga, leadership, and focus.
        - Quote Chanakya Niti where applicable for strategy.
        - Emphasize 'Nishkama Karma' (Action without anxiety for results).
        """
    else:
        focus_instruction = "- Answer generally based on Vedic wisdom."

    # 4. Construct Prompt
    system_prompt = f"""
    You are 'Saarthi', a wise Vedic Counselor.
    {lang_instruction}
    {tone}
    {focus_instruction}
    
    Reference Context:
    {context}
    
    User Query: {user_query}
    
    Guidelines:
    - If the context matches, explain it.
    - If context is missing, use general Vedic knowledge.
    - Be concise and empathetic.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_query})
    
    # 5. Call LLM
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.6,
        )
        answer = chat_completion.choices[0].message.content
        return answer, sources
    except Exception as e:
        return f"Error connecting to AI: {e}", []
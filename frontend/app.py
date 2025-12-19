import streamlit as st
import sys
import os
import pandas as pd
import random
from datetime import datetime

# --- PATH SETUP ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.rag_engine import generate_answer

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Saarthi (सारथी) AI",
    page_icon="☸️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- FAMOUS QUOTES (Sanskrit + English) ---
FAMOUS_QUOTES = [
    {
        "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन ।",
        "english": "You have a right to perform your prescribed duty, but you are not entitled to the fruits of action.",
        "ref": "Gita 2.47"
    },
    {
        "sanskrit": "न जायते म्रियते वा कदाचि-",
        "english": "The soul is neither born, nor does it ever die.",
        "ref": "Gita 2.20"
    },
    {
        "sanskrit": "योगः कर्मसु कौशलम् ।",
        "english": "Yoga is excellence in action.",
        "ref": "Gita 2.50"
    },
    {
        "sanskrit": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत ।",
        "english": "Whenever there is a decline in righteousness, O Arjuna, I manifest Myself.",
        "ref": "Gita 4.7"
    },
    {
        "sanskrit": "संशयात्मा विनश्यति ।",
        "english": "The person who doubts is ruined.",
        "ref": "Gita 4.40"
    }
]

# --- GLOBAL THEME / CSS ---
st.markdown("""
<style>
/* Import Fonts */
@import url('https://fonts.googleapis.com/css2?family=Martel:wght@300;400;800&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Poppins:wght@300;400;600&display=swap');

/* --- NUCLEAR TEXT COLOR FIX --- */
/* Force ALL text inside the main app to be dark, overriding Streamlit Dark Mode */
.stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6, span, div, li {
    color: #1e293b !important;
}

/* Exception: Sidebar text should remain light */
section[data-testid="stSidebar"] p, 
section[data-testid="stSidebar"] span, 
section[data-testid="stSidebar"] div, 
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2 {
    color: #f1f5f9 !important;
}

/* Main Background */
.stApp {
    background: linear-gradient(135deg, #fdfbf7 0%, #f4f4f9 100%);
}

/* Typography */
h1, h2, h3 {
    font-family: 'Poppins', sans-serif;
    color: #3d342b !important;
}

/* Sanskrit Text */
.sanskrit-text {
    font-family: 'Martel', serif;
    font-weight: 800;
    color: #8b4513 !important; /* Force SaddleBrown */
}

/* Chat Bubbles */
.stChatMessage {
    background-color: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(230, 230, 230, 0.5);
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    font-family: 'Merriweather', serif;
}

/* FORCE BLACK TEXT INSIDE CHAT BUBBLES */
.stChatMessage p, .stChatMessage div, .stChatMessage span, .stChatMessage li {
    color: #000000 !important;
}

/* User Bubble */
.stChatMessage.user {
    background: linear-gradient(135deg, #fff0e6 0%, #fff 100%) !important;
    border-left: 4px solid #d35400;
}

/* AI Bubble */
.stChatMessage.assistant {
    background: linear-gradient(135deg, #f4fcfc 0%, #fff 100%) !important;
    border-left: 4px solid #00897b;
}

/* Input Box Styling */
textarea, input {
    background-color: #ffffff !important;
    color: #000000 !important; /* Force input text black */
    border: 1px solid #ccc !important;
}

/* Header Box */
.header-box {
    background: linear-gradient(90deg, #2c3e50 0%, #4ca1af 100%);
    padding: 30px;
    border-radius: 15px;
    color: white !important;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}
/* Force header text white */
.header-box div, .header-box p, .header-box h1 {
    color: #ffffff !important;
}
.header-title {
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 5px;
}
.header-subtitle {
    font-size: 1rem;
    font-weight: 300;
    opacity: 0.9;
    font-style: italic;
}
.header-sanskrit {
    font-family: 'Martel', serif;
    font-size: 1.1rem;
    color: #f1c40f !important; /* Force Gold */
    margin-top: 15px;
}

/* Sidebar Background */
section[data-testid="stSidebar"] {
    background-color: #1a1a1a;
}
</style>
""", unsafe_allow_html=True)

# --- HELPER: RANDOM SHLOKA ---
@st.cache_data(ttl=3600)
def get_random_shloka():
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'gita_verses.csv')
        df = pd.read_csv(data_path)
        if not df.empty:
            row = df.sample(1).iloc[0]
            raw_sanskrit = row['sanskrit'].replace('\n', ' ').replace('|', '').strip()
            return {"text": raw_sanskrit, "meaning": row['translation'], "ref": f"Gita {row['chapter']}.{row['verse']}"}
    except:
        return None

# --- SIDEBAR CONTENT ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3663/3663344.png", width=80)
    st.markdown("<h2 style='color: white !important;'>Saarthi AI</h2>", unsafe_allow_html=True)
    st.caption("☸️ Your Digital Charioteer")

    daily_shloka = get_random_shloka()
    if daily_shloka:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.08); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); margin-top: 20px;">
            <p style="color: #94a3b8 !important; font-size: 0.7rem; margin:0; text-transform: uppercase; letter-spacing: 1px;">✨ Daily Wisdom</p>
            <p style="color: #f39c12 !important; font-family: 'Martel', serif; font-size: 1.05rem; line-height: 1.5; margin: 10px 0;">
                {daily_shloka['text']}
            </p>
            <p style="color: #dcdcdc !important; font-size: 0.85rem; font-style: italic;">
                "{daily_shloka['meaning'][:100]}..."
            </p>
            <div style="text-align: right; color: #7f8c8d !important; font-size: 0.75rem; margin-top: 5px;">— {daily_shloka['ref']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN HERO SECTION ---
quote = random.choice(FAMOUS_QUOTES)

st.markdown(f"""
<div class="header-box">
    <div class="header-title">Saarthi (सारथी)</div>
    <div class="header-subtitle">Your guide through the battlefield of life</div>
    <div class="header-sanskrit">{quote['sanskrit']}</div>
    <div style="font-size: 0.9rem; margin-top: 5px;">"{quote['english']}"</div>
</div>
""", unsafe_allow_html=True)

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        avatar_url = "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"
    else:
        avatar_url = "https://cdn-icons-png.flaticon.com/512/3663/3663344.png"

    with st.chat_message(message["role"], avatar=avatar_url):
        st.markdown(message["content"])

if prompt := st.chat_input("Arjuna asks Krishna... (Type your question)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="https://cdn-icons-png.flaticon.com/512/4140/4140048.png"):
        st.markdown(prompt)

    with st.spinner("The Charioteer is contemplating..."):
        history_for_ai = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
        
        answer, sources = generate_answer(prompt, history_for_ai)
        
        full_response = answer
        if sources:
             full_response += "\n\n---\n**📚 Shastra Pramana (References):**\n" + "\n".join([f"- {s}" for s in sources])

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    with st.chat_message("assistant", avatar="https://cdn-icons-png.flaticon.com/512/3663/3663344.png"):
        st.markdown(full_response)
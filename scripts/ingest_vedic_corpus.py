import pandas as pd
import os
import sys

# Fix path to import backend settings
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from backend.config import settings

def seed_scriptures():
    print("🚀 Starting Vedic Corpus Seeding...")
    
    # --- 1. THE UPANISHADS (Core Verses) ---
    print("\n🌱 Seeding Upanishads...")
    upanishad_data = [
        {"chapter": "Brihadaranyaka", "verse": "1.4.10", "sanskrit": "अहं ब्रह्मास्मि", "translation": "I am Brahman (the Ultimate Reality).", "source": "Upanishads"},
        {"chapter": "Chandogya", "verse": "6.8.7", "sanskrit": "तत् त्वम् असि", "translation": "You are That (the Ultimate Reality).", "source": "Upanishads"},
        {"chapter": "Mandukya", "verse": "2", "sanskrit": "अयमात्मा ब्रह्म", "translation": "This Self (Atman) is Brahman.", "source": "Upanishads"},
        {"chapter": "Aitareya", "verse": "3.3", "sanskrit": "प्रज्ञानं ब्रह्म", "translation": "Consciousness is Brahman.", "source": "Upanishads"},
        {"chapter": "Isha", "verse": "1", "sanskrit": "ईशा वास्यमिदं सर्वं...", "translation": "All this is pervaded by the Lord; enjoy through renunciation.", "source": "Upanishads"},
        {"chapter": "Katha", "verse": "1.2.20", "sanskrit": "अणोरणीयान्महतो महीयान्...", "translation": "The Self is subtler than the subtle, greater than the great.", "source": "Upanishads"},
        {"chapter": "Mundaka", "verse": "3.1.6", "sanskrit": "सत्यमेव जयते", "translation": "Truth alone triumphs, not falsehood.", "source": "Upanishads"},
        {"chapter": "Taittiriya", "verse": "2.1", "sanskrit": "सत्यं ज्ञानमनन्तं ब्रह्म", "translation": "Brahman is Truth, Knowledge, and Infinite.", "source": "Upanishads"},
        {"chapter": "Shvetashvatara", "verse": "4.10", "sanskrit": "मायां तु प्रकृतिं विद्यान्...", "translation": "Know Prakriti (Nature) to be Maya, and the Great Lord as the ruler of Maya.", "source": "Upanishads"},
    ]
    
    u_df = pd.DataFrame(upanishad_data)
    u_path = os.path.join(settings.DATA_DIR, "upanishads.csv")
    u_df.to_csv(u_path, index=False)
    print(f"✅ Saved {len(u_df)} Core Upanishad Verses.")

    # --- 2. BRAHMA SUTRAS (The Chatussutri) ---
    print("\n🌱 Seeding Brahma Sutras...")
    bs_data = [
        {"chapter": 1, "verse": 1, "sanskrit": "अथातो ब्रह्मजिज्ञासा", "translation": "Now, therefore, the inquiry into Brahman.", "source": "Brahma Sutras"},
        {"chapter": 1, "verse": 2, "sanskrit": "जन्माद्यस्य यतः", "translation": "Brahman is That from which the origin, sustenance, and dissolution of this universe proceed.", "source": "Brahma Sutras"},
        {"chapter": 1, "verse": 3, "sanskrit": "शास्त्रयोनित्वात्", "translation": "The scripture (Veda) is the source of right knowledge concerning Brahman.", "source": "Brahma Sutras"},
        {"chapter": 1, "verse": 4, "sanskrit": "तत्तु समन्वयात्", "translation": "But that Brahman is known from the Upanishads, because they all have It as their main purport.", "source": "Brahma Sutras"},
    ]
    
    bs_df = pd.DataFrame(bs_data)
    bs_path = os.path.join(settings.DATA_DIR, "brahma_sutras.csv")
    bs_df.to_csv(bs_path, index=False)
    print(f"✅ Saved {len(bs_df)} Brahma Sutras.")
    
    print("\n🎉 Seeding Complete!")

if __name__ == "__main__":
    seed_scriptures()
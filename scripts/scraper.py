import requests
import pandas as pd
import time
import sys
import os

# Fix path to allow importing backend settings
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from backend.config import settings

API_URL = "https://vedicscriptures.github.io/slok/{chapter}/{verse}/"
OUTPUT_FILE = os.path.join(settings.DATA_DIR, "gita_verses.csv")

def fetch_verse(chapter, verse):
    url = API_URL.format(chapter=chapter, verse=verse)
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        return {
            "chapter": chapter,
            "verse": verse,
            "sanskrit": data.get('slok', '').strip(),
            "translation": data.get('siva', {}).get('et', '').strip(),
            "source": "Bhagavad Gita"
        }
    except Exception as e:
        print(f"⚠️ Error fetching {chapter}.{verse}: {e}")
        return None

def main():
    print(f"🚀 Starting Gita Scraper...")
    print(f"📂 Output Path: {OUTPUT_FILE}")
    
    all_verses = []
    
    # Loop through all 18 chapters
    for chapter in range(1, 19):
        print(f"\n📘 Chapter {chapter} ", end="", flush=True)
        verse = 1
        while True:
            data = fetch_verse(chapter, verse)
            if not data:
                break # End of chapter
            
            all_verses.append(data)
            if verse % 5 == 0: print(".", end="", flush=True) # Progress dot
            verse += 1
            time.sleep(0.05) # Be polite to the API

    # Save
    if all_verses:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        df = pd.DataFrame(all_verses)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n\n✅ COMPLETED! Saved {len(df)} verses.")
    else:
        print("\n❌ No data fetched.")

if __name__ == "__main__":
    main()
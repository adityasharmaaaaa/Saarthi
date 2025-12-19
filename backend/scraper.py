import requests
import pandas as pd
import time
import os

API_URL = "https://vedicscriptures.github.io/slok/{chapter}/{verse}/"

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
OUTPUT_FILE = os.path.join(project_root, "data", "gita_verses.csv")

def fetch_verse_from_api(chapter, verse):
    """
    Fetches a specific verse. Returns None if the verse doesn't exist (End of Chapter).
    """
    url = API_URL.format(chapter=chapter, verse=verse)
    
    try:
        response = requests.get(url)
        
        # If 404, it means we reached the end of the chapter
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Extract Sanskrit and English (Swami Sivananda's translation)
        sanskrit = data.get('slok', '')
        translation = data.get('siva', {}).get('et', '')
        
        # Data validation
        if not sanskrit or not translation:
            return None

        return {
            "chapter": chapter,
            "verse": verse,
            "sanskrit": sanskrit,
            "translation": translation
        }

    except Exception as e:
        print(f"⚠️ Error {chapter}.{verse}: {e}")
        return None

def main():
    all_verses = []
    
    print("🚀 Starting Full Gita Scraper (Chapters 1-18)...")
    print(f"📂 Data will be saved to: {OUTPUT_FILE}")
    
    for chapter in range(1, 19): 
        print(f"\n📘 Processing Chapter {chapter}...")
        verse = 1
        
        while True:
            # Fetch data
            data = fetch_verse_from_api(chapter, verse)
            
            if data:
                data['translation'] = data['translation'].replace('\n', ' ').strip()
                all_verses.append(data)
                
                print(f".", end="", flush=True)
                
                verse += 1
                time.sleep(0.1) 
            else:
                # If data is None, we reached the end of this chapter
                print(f"\n✅ Finished Chapter {chapter} ({verse-1} verses found)")
                break

    # Save to CSV
    if all_verses:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        df = pd.DataFrame(all_verses)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n COMPLETED! Saved {len(df)} verses to {OUTPUT_FILE}")
    else:
        print("\n No data found.")

if __name__ == "__main__":
    main()
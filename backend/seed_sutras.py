import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
OUTPUT_FILE = os.path.join(project_root, "data", "yoga_sutras.csv")

# --- DATA: THE SAMADHI PADA (Chapter 1) ---
sutras_data = [
    {"chapter": 1, "verse": 1, "sanskrit": "अथ योगानुशासनम्", "translation": "Now, the instruction of Yoga begins.", "source": "Yoga Sutras"},
    {"chapter": 1, "verse": 2, "sanskrit": "योगश्चित्तवृत्तिनिरोधः", "translation": "Yoga is the settling of the mind into silence (cessation of mental fluctuations).", "source": "Yoga Sutras"},
    {"chapter": 1, "verse": 3, "sanskrit": "तदा द्रष्टुः स्वरूपेऽवस्थानम्", "translation": "Then the Seer (Self) abides in Its own true nature.", "source": "Yoga Sutras"},
    {"chapter": 1, "verse": 4, "sanskrit": "वृत्तिसारूप्यमितरत्र", "translation": "At other times, the Self appears to take the form of the mental modifications.", "source": "Yoga Sutras"},
    {"chapter": 1, "verse": 5, "sanskrit": "वृत्तयः पञ्चतय्यः क्लिष्टाक्लिष्टाः", "translation": "There are five kinds of mental modifications, which are either painful or painless.", "source": "Yoga Sutras"},
    {"chapter": 1, "verse": 12, "sanskrit": "अभ्यासवैराग्याभ्यां तन्निरोधः", "translation": "The mind is mastered through practice (Abhyasa) and non-attachment (Vairagya).", "source": "Yoga Sutras"},
    {"chapter": 1, "verse": 13, "sanskrit": "तत्र स्थितौ यत्नोऽभ्यासः", "translation": "Practice is the sustained effort to rest in that stillness.", "source": "Yoga Sutras"},
    {"chapter": 1, "verse": 33, "sanskrit": "मैत्रीकरुणामुदितोपेक्षाणां...", "translation": "The mind becomes serene by cultivating friendliness, compassion, delight, and equanimity toward all.", "source": "Yoga Sutras"},
]

def main():
    print(f"🧘 Genering Yoga Sutras Dataset...")
    df = pd.DataFrame(sutras_data)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Success! Saved {len(df)} Sutras to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
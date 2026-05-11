import os
import requests
from google import genai

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 2026 Client Setup
client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_market_pains():
    print("Fetching Market Data from Reddit/IndieHackers...")
    sources = [
        "https://r.jina.ai/https://www.reddit.com/r/SaaS/new",
        "https://r.jina.ai/https://www.indiehackers.com/groups/ideas-and-validation"
    ]
    combined_text = ""
    for url in sources:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                combined_text += response.text[:2000] 
        except: continue
    return combined_text

def analyze_and_factory(raw_data):
    print("AI Analysis (Gemini 2.5 Flash Lite) Starting...")
    if not raw_data: return "Data fetch fail ho gaya."

    prompt = f"Analyze these discussions and suggest 2 Micro-SaaS ideas. Format: Name, Gap, Tech Schema (Supabase), Marketing Kit, and Monetization. Language: Hinglish. Data: {raw_data}"
    
    try:
        # Using the model you found!
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error: {str(e)}")
        if "429" in str(e):
            return "⚠️ Quota Exhausted! Kal subah 9 baje automate ho jayega."
        return f"AI Logic Error: {str(e)}"

def send_telegram(message):
    print("Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    data = fetch_market_pains()
    blueprint = analyze_and_factory(data)
    send_telegram(blueprint)
    print("Process Complete!")

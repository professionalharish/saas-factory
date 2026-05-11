import os
import requests
from google import genai
import time

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_market_pains():
    print("Fetching Market Data...")
    sources = [
        "https://r.jina.ai/https://www.reddit.com/r/SaaS/new",
        "https://r.jina.ai/https://www.indiehackers.com/groups/ideas-and-validation"
    ]
    combined_text = ""
    for url in sources:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Sirf kaam ka data uthao (limit to 1500 chars to save tokens)
                combined_text += response.text[:1500] 
        except: continue
    return combined_text

def analyze_and_factory(raw_data):
    print("AI Analysis in progress...")
    if not raw_data: return "Data fetch fail ho gaya."

    prompt = f"Identify 2 Micro-SaaS ideas from this: {raw_data}. Give Name, Supabase Schema, and Marketing Kit in Hinglish."
    
    try:
        # Using 1.5-flash-8b: Better quota for free users in 2026
        response = client.models.generate_content(
            model="gemini-1.5-flash-8b", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ AI Quota Exhausted! Please try again after 1 hour or tomorrow."
        return f"AI Error: {str(e)}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"})

if __name__ == "__main__":
    data = fetch_market_pains()
    blueprint = analyze_and_factory(data)
    send_telegram(blueprint)

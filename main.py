import os
import requests
from google import genai

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 2026 New Client Setup
client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_market_pains():
    print("Fetching Market Data (No-API Mode)...")
    sources = [
        "https://r.jina.ai/https://www.reddit.com/r/SaaS/new",
        "https://r.jina.ai/https://www.indiehackers.com/groups/ideas-and-validation"
    ]
    combined_text = ""
    for url in sources:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                combined_text += response.text[:2500]
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return combined_text

def analyze_and_factory(raw_data):
    print("AI Analysis (Gemini 3 Flash Engine) in progress...")
    if len(raw_data) < 100:
        return "Data fetch nahi ho paya."

    prompt = f"Analyze these SaaS discussions and give 2 Viral Blueprints: {raw_data}. Provide Name, Tech Schema (Supabase), Marketing Kit, and Monetization in Hinglish Markdown."
    
    # Updated Model Call for 2026
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Latest stable model
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Logic Error: {str(e)}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    data = fetch_market_pains()
    blueprint = analyze_and_factory(data)
    send_telegram(blueprint)
    print("SaaS Factory Report Sent!")

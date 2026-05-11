import os
import requests
import google.generativeai as genai

# --- CONFIGURATION (Only Gemini & Telegram needed) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def fetch_market_pains():
    print("Fetching Market Data (No-API Mode)...")
    
    # Hum Jina Reader use karenge jo Reddit/IndieHackers ko text mein convert kar deta hai
    # Ye 100% free aur legal hai for research
    sources = [
        "https://r.jina.ai/https://www.reddit.com/r/SaaS/new",
        "https://r.jina.ai/https://www.reddit.com/r/Entrepreneur/new",
        "https://r.jina.ai/https://www.indiehackers.com/groups/ideas-and-validation"
    ]
    
    combined_text = ""
    for url in sources:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                combined_text += response.text[:2000] # Har source se main content uthana
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            
    return combined_text

def analyze_and_factory(raw_data):
    print("AI Analysis in progress...")
    if len(raw_data) < 100:
        return "Data fetch nahi ho paya. Internet connection ya source check karein."

    prompt = f"""
    Analyze these latest SaaS discussions and pain points:
    {raw_data}
    
    Identify the TOP 2 most 'Viral-Ready' Micro-SaaS ideas.
    For EACH idea, provide:
    1. 🚀 Blueprint: Name & 'Gap' (why current tools fail).
    2. 🛠 Technical: Database Schema (Supabase) & Core API Routes.
    3. 📢 Marketing Kit: A 'Cold Reply' for the lead & 3-tweet thread.
    4. 💰 Monetization: Suggested Pricing.
    
    Language: Hinglish. Format: Clean Markdown for Telegram.
    """
    response = model.generate_content(prompt)
    return response.text

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    data = fetch_market_pains()
    blueprint = analyze_and_factory(data)
    send_telegram(blueprint)
    print("Success! Report sent to Telegram.")

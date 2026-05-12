import os
import requests
import time
from google import genai

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_market_pains():
    print("Market data hunt shuru...")
    sources = [
        "https://r.jina.ai/https://www.reddit.com/r/SaaS/new",
        "https://r.jina.ai/https://www.reddit.com/r/SideProject/new",
        "https://r.jina.ai/https://www.indiehackers.com/groups/ideas-and-validation"
    ]
    combined_text = ""
    for url in sources:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                combined_text += f"\n--- SOURCE: {url} ---\n{response.text[:2000]}"
        except: continue
    return combined_text

def analyze_and_blueprint(raw_data):
    print("AI generating 3 high-quality separate blueprints...")
    prompt = f"""
    Identify exactly 3 High-Signal Micro-SaaS ideas. 
    Crucial: End each idea with |||IDEA_SPLIT|||
    Use very simple Markdown. Avoid complex symbols.
    Data: {raw_data}
    """
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return ""

def send_to_telegram(message):
    """Safe Telegram sender with fallback"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Pehle Markdown ke saath try karte hain
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    
    try:
        r = requests.post(url, json=payload)
        # Agar Markdown fail hota hai (400 error), toh Plain Text bhejte hain
        if r.status_code != 200:
            print(f"Markdown failed, sending plain text. Error: {r.text}")
            payload.pop("parse_mode")
            requests.post(url, json=payload)
        else:
            print("Message delivered successfully via Markdown.")
    except Exception as e:
        print(f"Telegram Request Failed: {e}")

def main():
    raw_data = fetch_market_pains()
    full_report = analyze_and_blueprint(raw_data)
    
    if not full_report:
        print("AI response was empty.")
        return

    ideas_list = full_report.split('|||IDEA_SPLIT|||')
    count = 0
    for idea in ideas_list:
        clean_idea = idea.strip()
        if len(clean_idea) > 100:
            send_to_telegram(clean_idea)
            count += 1
            time.sleep(2) # Telegram Flood limit se bachne ke liye delay
            
    print(f"Done! {count} separate ideas processed.")

if __name__ == "__main__":
    main()

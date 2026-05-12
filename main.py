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
    # Jina search use kar rahe hain taaki data block na ho
    queries = [
        "latest saas pain points reddit 2026",
        "annoying business tasks automation reddit 2026"
    ]
    combined_text = ""
    for q in queries:
        try:
            url = f"https://s.jina.ai/{q.replace(' ', '%20')}"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                combined_text += f"\n--- DATA ---\n{response.text[:1500]}"
        except: continue
    return combined_text

def analyze_and_blueprint(raw_data):
    print("AI generating 3 high-quality separate blueprints...")
    prompt = f"""
    Identify exactly 3 High-Signal Micro-SaaS ideas. 
    Crucial: End each idea with |||IDEA_SPLIT|||
    Avoid complex markdown. Use simple bold text only.
    Data: {raw_data}
    """
    try:
        # Using a more robust model name
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return ""

def send_to_telegram(message):
    """Safe Telegram sender with auto-fallback for markdown errors"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Attempt 1: With Markdown
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            # Attempt 2: If markdown fails, send as Plain Text
            print(f"Markdown failed (Error {r.status_code}), sending plain text...")
            payload.pop("parse_mode")
            retry = requests.post(url, json=payload)
            if retry.status_code == 200:
                print("Delivered as plain text.")
            else:
                print(f"Final Failure: {retry.text}")
        else:
            print("Delivered with Markdown.")
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
            time.sleep(2) # Flood control
            
    print(f"Done! {count} separate ideas processed.")

if __name__ == "__main__":
    main()

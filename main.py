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
    print("🧠 AI Analysis: Identifying 3 High-Signal Gold Mines...")
    
    # Ye prompt AI ko majboor karega deep analysis aur structured blueprint dene ke liye
    prompt = f"""
### ROLE: 
Venture Capitalist & Micro-SaaS Architect (Pieter Levels Style).
    
### TASK:
Analyze the provided market data AND use your own 2026 market intelligence to find EXACTLY 3 'High-Signal' Micro-SaaS ideas. 
If the provided data is thin/blocked, prioritize identifying recurring "Irritant Problems" from your internal knowledge of the 2026 SaaS landscape.

### EXECUTION:
1. Focus on 'Single-Feature' tools that solve a 10-minute daily pain.
2. Structure each idea clearly. 
3. Use Hinglish for explanations to keep it practical and grounded.
4. End every idea with this exact string: |||IDEA_SPLIT|||

🔥 **NAME & VIRAL HOOK**
Catchy name with a "Why share this?" factor.

💡 **PAIN ANALYSIS (2026)**
- Specific frustration: Log kis baat se pareshan hain?
- The Gap: Current solutions kyun fail ho rahi hain?

🚀 **TREND & VALIDATION**
- Why now? (Mention 2026 market trends like AI Agents, Local-first apps, or Privacy-tech).
- Target Market size and potential.

🛠 **TECH BLUEPRINT**
- **Supabase Schema**: Detailed tables and relations.
- **Core API Logic**: Logic for the main feature.
- **Stack**: Next.js (App Router), Supabase, Resend, Stripe.

📢 **GTM (Go-To-Market)**
- Launch Pad: Exactly kahan post karna hai (Subreddit/Discord/X).
- Cold Reply: A 2-line direct message to convert the first user.

💰 **MONETIZATION**
- Pricing model: (Free tier vs Credits vs Subscription).
- Validation Score (1-10) based on effort/reward ratio.

|||IDEA_SPLIT|||

### RAW DATA FOR CONTEXT:
{raw_data}
"""
    
    try:
        # gemini-2.0-flash is recommended for complex reasoning and structure
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        
        # Clean response ensure karna
        output = response.text if response.text else ""
        if not output:
            print("Warning: AI generated an empty response.")
        return output

    except Exception as e:
        print(f"AI Error in Analysis: {e}")
        return ""

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # --- DEBUG STEP: Ye line GitHub Logs mein poora message print karegi ---
    print("\n--- DEBUG: MESSAGE START ---")
    print(message)
    print("--- DEBUG: MESSAGE END ---\n")
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        r = requests.post(url, json=payload)
        # Agar Telegram reject karta hai toh asli wajah print hogi
        if r.status_code != 200:
            print(f"❌ Telegram Error Code: {r.status_code}")
            print(f"❌ Telegram Response: {r.text}")
            
            # Retry with Plain Text (Jab Markdown fail ho jaye)
            print("🔄 Retrying as plain text...")
            payload.pop("parse_mode")
            r2 = requests.post(url, json=payload)
            print(f"🔄 Plain Text Status: {r2.status_code}")
        else:
            print("✅ Message delivered successfully!")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

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

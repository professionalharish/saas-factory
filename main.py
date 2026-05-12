import os
import requests
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
    print("AI generating 5 separate blueprints...")
    
    # Humne AI ko instruction di hai ki har idea ke baad |||IDEA_SPLIT||| lagaye
    prompt = f"""
    You are an Elite Micro-SaaS Architect. Based on the data, extract 5 High-Signal ideas.
    
    CRITICAL INSTRUCTION: After finishing EACH idea, you MUST write the separator exactly like this: |||IDEA_SPLIT|||
    
    For each idea, provide this detailed structure:
    🔥 **Idea Name & Tagline**
    💡 **The Micro-Problem & Gap** (Detailed analysis)
    🚀 **Viral Hook & Acquisition Strategy**
    🛠 **Technical Blueprint** (Next.js + Supabase Schema + API Routes)
    📢 **Marketing Kit** (Cold Reply + Hero Headline)
    💰 **Monetization & Score**
    🔗 **Direct Lead/Context**

    Language: Hinglish. Use clean Markdown with bold headings.
    DATA: {raw_data}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return ""

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except: pass

def main():
    raw_data = fetch_market_pains()
    full_report = analyze_and_blueprint(raw_data)
    
    if not full_report:
        send_to_telegram("❌ Error: AI ne response generate nahi kiya.")
        return

    # Logic: Separator ke basis par split karna
    ideas_list = full_report.split('|||IDEA_SPLIT|||')
    
    count = 0
    for idea in ideas_list:
        clean_idea = idea.strip()
        if len(clean_idea) > 50: # Khali messages ya chote fragments avoid karne ke liye
            send_to_telegram(clean_idea)
            count += 1
            
    print(f"Done! {count} separate ideas sent to Telegram.")

if __name__ == "__main__":
    main()

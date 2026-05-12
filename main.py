import os
import requests
from google import genai

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_market_pains():
    print("Hunting for Gold Mines...")
    # Using Jina Reader to bypass Reddit API blocks
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
                combined_text += f"\n--- SOURCE: {url} ---\n"
                combined_text += response.text[:2500] 
        except: continue
    return combined_text

def analyze_and_blueprint(raw_data):
    print("AI Analysis: Viral SaaS Hunter Mode...")
    if not raw_data: return ""

    prompt = f"""
    You are an Elite Micro-SaaS Architect and a Viral Growth Hacker like Pieter Levels. 
    Analyze the following market data and extract exactly 5 'High-Signal Gold Mines'.
    
    IMPORTANT: Start each idea with the '🔥' emoji.
    
    For each idea, provide:
    🔥 **Idea Name & Tagline**
    💡 **The Micro-Problem & Gap** (Why enterprise tools fail)
    🚀 **Viral Hook & Acquisition Strategy** (Where to post)
    🛠 **Technical Blueprint (Next.js + Supabase Schema + API Routes)**
    📢 **Marketing Kit (Cold Reply + Hero Headline)**
    💰 **Monetization & Score (1-10)**
    🔗 **Direct Lead/Context**

    Language: Hinglish. Use clean Markdown.
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
    """Helper function to send a single message"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

def main():
    print("Starting SaaS Factory...")
    raw_data = fetch_market_pains()
    report = analyze_and_blueprint(raw_data)
    
    if not report:
        send_to_telegram("❌ Aaj koi naya data nahi mila ya AI fail ho gaya.")
        return

    # LOGIC: Splitting the report into 5 separate messages based on the emoji
    # ideas[0] will be any text before the first idea
    ideas = report.split('🔥')
    
    # Send Intro if it exists
    intro = ideas[0].strip()
    if intro:
        send_to_telegram(f"🚀 **SaaS Factory Report for Today**\n\n{intro}")

    # Send each idea as a separate message
    for idea in ideas[1:]:
        # Adding the emoji back because split removes it
        clean_message = "🔥" + idea.strip()
        send_to_telegram(clean_message)

    print("Process Complete! 5 messages sent.")

if __name__ == "__main__":
    main()

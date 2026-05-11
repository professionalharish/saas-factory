import os
import requests
from google import genai

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 2026 Gemini Client Setup
client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_market_pains():
    print("Hunting for Gold Mines (Reddit + Indie Hackers)...")
    
    # Hum Jina Reader aur RSS use karenge taaki Reddit API ke nakhre na rahein
    sources = [
        "https://r.jina.ai/https://www.reddit.com/r/SaaS/new",
        "https://r.jina.ai/https://www.reddit.com/r/SideProject/new",
        "https://r.jina.ai/https://www.indiehackers.com/groups/ideas-and-validation"
    ]
    
    combined_text = ""
    for url in sources:
        try:
            # Jina Reader converts web to clean text for AI
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                combined_text += f"\n--- SOURCE: {url} ---\n"
                combined_text += response.text[:2500] 
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            
    return combined_text

def analyze_and_blueprint(raw_data):
    print("AI Analysis: Viral SaaS Hunter Mode Activated...")
    if not raw_data: return "No data found to hunt."

    # --- HYBRID PROMPT (Senior PM + Viral Hunter) ---
    prompt = f"""
    You are an Elite Micro-SaaS Architect and a Viral Growth Hacker like Pieter Levels. 
    Analyze the following market data and extract 5 'High-Signal Gold Mines'.
    
    For each idea, follow this EXACT structure:

    🔥 **Idea Name & Tagline**: Catchy, SEO-friendly, and viral.
    
    💡 **The Micro-Problem & Gap**: 
    - Identify a problem that takes 10 mins but happens 10 times a day.
    - Why are 'Enterprise' tools failing? (Too complex/expensive).
    
    🚀 **Viral Hook & Acquisition**:
    - Why would someone share this on X (Twitter) or LinkedIn?
    - Exactly WHERE to post this first (Subreddit/Community) and how.
    
    🛠 **Technical Blueprint (Next.js + Supabase)**:
    - **Database Schema**: Essential tables and columns.
    - **Core API Routes**: Key backend logic.
    - **3rd Party Tools**: (e.g., Stripe, Resend, Claude API).

    📢 **Marketing Kit**:
    - **Cold Reply**: A 2-line helpful reply for the person who had the problem.
    - **Landing Page Hero**: A high-converting headline and 3 bullet points.

    💰 **Monetization & Score**:
    - Pricing model (Free/Paid/Credits).
    - Validation Score (1-10) based on effort vs. viral potential.

    🔗 **Direct Lead/Context**: Mention the source URL or thread context from data.

    Format: Use clean Markdown with bold headings and emojis.
    Language: Hinglish.
    
    DATA:
    {raw_data}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        if "429" in str(e): return "⚠️ API Quota Full. Try after some time."
        return f"AI Logic Error: {str(e)}"

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # Handling long messages
    if len(message) > 4000:
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for chunk in chunks:
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "Markdown"})
    else:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"})

if __name__ == "__main__":
    data = fetch_market_pains()
    report = analyze_and_blueprint(data)
    send_to_telegram(report)
    print("Success! Viral Blueprints sent to Telegram.")

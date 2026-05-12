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
        except: 
            continue
    return combined_text

def analyze_and_blueprint(raw_data):
    print("AI generating 3 high-quality separate blueprints...")
    
    # Corrected Indentation for prompt
    prompt = f"""
### ROLE: 
You are a World-Class Micro-SaaS Architect and a Venture Capitalist. Your specialty is finding 'Irritant Problems' that can be solved with a 'Single-Feature' tool and scaled to $1,000/mo in 30 days.

### TASK:
Analyze the provided market data and identify EXACTLY 3 (Three) High-Signal Gold Mines. 
Quality is more important than quantity. If you provide 3 ideas, each must be a complete 'Business-in-a-Box'.

### EXECUTION GUIDELINES:
1. **Focus on the 'Irritant'**: Find tasks that take 5-10 minutes but are done multiple times a day (High Frequency).
2. **Anti-Enterprise**: Suggest solutions that are 10x simpler than Salesforce, HubSpot, or Jira.
3. **Tech Stack**: Must be built using Next.js, Tailwind CSS, and Supabase.
4. **SEPARATOR**: You MUST end every idea with this exact string: |||IDEA_SPLIT|||

### FOR EACH IDEA, PROVIDE THIS STRUCTURE:

🔥 **IDEA NAME & VIRAL TAGLINE**

💡 **THE MICRO-PROBLEM & MARKET GAP**
- **The Pain**: What exactly is the user crying about in the data?
- **The Gap**: Why is the current solution failing them? 
- **User Psychology**: Why will they pay for THIS specific solution?

🚀 **VIRAL GROWTH & ACQUISITION PLAN**
- **The 'Viral Loop'**: Why would a user post a screenshot of this on X or LinkedIn?
- **Launch Strategy**: Which specific Subreddit and what exact hook to use?

🛠 **TECHNICAL ARCHITECTURE (THE BLUEPRINT)**
- **Supabase Schema**: Detailed tables and columns.
- **Critical Logic**: Explain the main API Route logic.
- **Stack**: Next.js, Supabase Auth, Resend, Stripe.

📢 **MARKETING & SALES KIT**
- **Hero Headline**: Magnetic H1.
- **3 Killer Bullet Points**: Benefits.
- **Cold Outreach Script**: Direct message to the source user.

💰 **MONETIZATION & VALIDATION**
- **Revenue Model**: Pricing details.
- **Difficulty Score (1-10)**
- **Viral Potential (1-10)**

🔗 **DIRECT LEAD & SOURCE**
- Link or context from data.

|||IDEA_SPLIT|||

### MARKET DATA TO ANALYZE:
{raw_data}
"""
    
    try:
        # Use the same model name you were using or 'gemini-2.0-flash'
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
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
    except: 
        pass

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
        if len(clean_idea) > 100: # Increased threshold for quality
            send_to_telegram(clean_idea)
            count += 1
            
    print(f"Done! {count} separate ideas sent to Telegram.")

if __name__ == "__main__":
    main()

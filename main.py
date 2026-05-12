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
    print("🚀 Global Intelligence Gathering (Last 30-90 days)...")
    
    # 20+ Targeted Queries for high-signal pain points
    # tbs=qdr:m ensures results from the LAST MONTH ONLY
    queries = [
        "site:reddit.com/r/SaaS 'wish there was a tool' after:2026-03-01",
        "site:reddit.com/r/smallbusiness 'manual task' annoying after:2026-03-01",
        "site:reddit.com/r/startups 'alternative to' expensive",
        "site:quora.com 'is there a simple app for' 2026",
        "site:news.ycombinator.com 'Ask HN: What are you struggling with'",
        "site:indiehackers.com 'looking for' automation tool",
        "site:trustpilot.com 'too complex' software review",
        "site:g2.com 'missing feature' simple version",
        "site:realtor.com/forums 'marketing automation' struggle",
        "site:accountingtoday.com 'excel' manual headache",
        "\"I would pay for a tool that\" 2026",
        "\"how to automate\" site:medium.com manual process"
    ]

    combined_text = ""
    for q in queries:
        encoded_q = q.replace(' ', '+')
        # Using s.jina.ai for fast search result formatting
        search_url = f"https://s.jina.ai/https://www.google.com/search?q={encoded_q}&tbs=qdr:m"
        
        try:
            print(f"🔍 Searching: {q[:40]}...")
            response = requests.get(search_url, timeout=12)
            if response.status_code == 200:
                combined_text += f"\n--- SOURCE DATA ---\n{response.text[:1500]}\n"
            
            time.sleep(1) # API Rate limit protection
        except:
            continue
            
    return combined_text

def analyze_and_blueprint(raw_data):
    print("🧠 AI Analysis: 3 High-Potential Gold Mines Only...")
    
    prompt = f"""
### ROLE: 
Venture Capitalist & Micro-SaaS Architect (Pieter Levels Style).
    
### GOAL:
Extract EXACTLY 3 (Three) 'High-Signal' Micro-SaaS ideas from the provided data.
Reject generic ideas. Find 'Irritant Problems' (5-min tasks done 10x/day).

### FORMAT: 
For each idea, provide the structure below. Use '|||IDEA_SPLIT|||' at the end of each.

🔥 **NAME & VIRAL HOOK**
💡 **PAIN ANALYSIS (LAST 90 DAYS)**: What specific recent frustration is this solving?
🚀 **TREND & VALIDATION**: Why is this trending now (2026)? Mention relevant keywords.
🛠 **TECH BLUEPRINT**: Next.js + Supabase schema + API Logic.
📢 **GTM (Go-To-Market)**: Specific community link and a 2-line cold DM for the lead.
💰 **MONETIZATION**: Pricing strategy (Free/Credits/Subscription).

|||IDEA_SPLIT|||

### MARKET DATA:
{raw_data}
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"AI ERROR: {e}")
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
        print(f"Telegram Response: {r.status_code}, {r.text}") # Ye logs mein dikhayega
    except:
        pass

def main():
    start_time = time.time()
    raw_data = fetch_market_pains()
    
    if not raw_data:
        send_to_telegram("❌ No fresh data found today.")
        return

    report = analyze_and_blueprint(raw_data)
    
    if not report:
        send_to_telegram("❌ AI failed to analyze data.")
        return

    # Splitting into separate messages
    ideas = report.split('|||IDEA_SPLIT|||')
    count = 0
    for idea in ideas:
        clean_idea = idea.strip()
        if len(clean_idea) > 100:
            send_to_telegram(clean_idea)
            count += 1
            time.sleep(1) # Prevent Telegram spam block

    duration = round((time.time() - start_time) / 60, 2)
    print(f"✅ Success! Sent {count} ideas in {duration} minutes.")

if __name__ == "__main__":
    main()

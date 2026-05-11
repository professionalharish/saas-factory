import os
import requests
import praw
import google.generativeai as genai

# --- CONFIGURATION (GitHub Secrets/Env Vars) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")

# AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def fetch_reddit_pains():
    print("Fetching Reddit data...")
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_SECRET,
            user_agent="SaaS-Hunter-v1"
        )
        
        keywords = ['"alternative to"', '"too expensive"', '"how to automate"', '"frustrated with"', '"missing feature"']
        subreddits = ['SaaS', 'Entrepreneur', 'SideProject', 'smallbusiness']
        data = []

        for sub in subreddits:
            for query in keywords:
                # Fetching latest posts from last 24 hours
                for post in reddit.subreddit(sub).search(query, time_filter='day', limit=5):
                    data.append(f"Source: r/{sub}\nTitle: {post.title}\nText: {post.selftext[:500]}\nURL: https://reddit.com{post.permalink}")
        
        return "\n---\n".join(data)
    except Exception as e:
        return f"Reddit API Error: {str(e)}"

def analyze_and_factory(raw_data):
    print("Generating SaaS Factory Blueprint...")
    if not raw_data or len(raw_data) < 50:
        return "Aaj market mein koi naya pain point nahi mila. Try changing keywords or wait for tomorrow."

    prompt = f"""
    You are an Elite Micro-SaaS Architect and Serial Maker. Analyze this raw data from Reddit:
    {raw_data}
    
    TASK: Pick the TOP 2 most 'Viral-Ready' and 'High-Passive-Income' ideas.
    
    For EACH idea, provide:
    1. 🚀 **Product Blueprint**: Catchy Name, Tagline, and the 'Gap' (why current tools fail).
    2. 🛠 **Technical Schema**: 
       - Core Database Tables (SQL format for Supabase).
       - Essential API Routes (Next.js App Router style).
    3. 📢 **Marketing Kit (Ready-to-Use)**:
       - A 'Cold Reply' for the original Reddit post (helpful, not spammy).
       - A 3-tweet 'Build in Public' thread with hooks.
       - A high-converting Hero Headline & Sub-headline.
    4. 💰 **Monetization**: Suggested Pricing (Freemium/SaaS tiers).
    5. 🔗 **Source Link**: The Reddit URL for direct outreach.

    Language: Hinglish. Format: Professional Markdown with Emojis.
    """
    response = model.generate_content(prompt)
    return response.text

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Split message if it's too long for Telegram (Limit 4096)
    if len(message) > 4000:
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    else:
        chunks = [message]

    for chunk in chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload)

if __name__ == "__main__":
    raw_pains = fetch_reddit_pains()
    blueprint = analyze_and_factory(raw_pains)
    send_telegram(blueprint)
    print("Report sent to Telegram successfully!")

# FULL WORKING SAM-Radar (Smart Adverse Media Radar) - Google Colab Version

# This version is:

# - Simple
# - No API keys required
# - Runs inside Colab
# - Fetches Adverse Media
# - Summarizes using fallback logic
# - Gives Risk Level (High/Medium/Low)
# - Exports CSV

# STEP 1 — Install Required Libraries

# Create a new notebook → add this cell → run:


# STEP 2 — Import Libraries
import requests, feedparser, pandas as pd, urllib.parse, matplotlib.pyplot as plt

# STEP 3 — Function: Fetch News (Google RSS)
def fetch_news(entity, limit=10):
    query = urllib.parse.quote(f"{entity} fraud OR scam OR money laundering OR crime OR corruption")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)

    articles = []
    for item in feed.entries[:limit]:
        articles.append({
            "title": item.title,
            "summary": item.summary,
            "link": item.link,
            "published": getattr(item, "published", "N/A"),
        })
    return articles

# STEP 4 — Summarizer Function (Simple Fallback)

# Since you want zero installs, we use a clean fallback summarizer.

def summarize(text):
    return text[:300] + "..."

# STEP 5 — Risk Level Logic
def risk_level(text):
    text_lower = text.lower()

    high_keywords = ["fraud", "money laundering", "scam", "crime", "corruption", "arrest", "lawsuit", "fine", "sanction", "fraudulent", "illegal"]
    medium_keywords = ["probe", "investigation", "regulatory", "unethical"]

    score = 0
    for w in high_keywords:
        if w in text_lower:
            score += 2
    for w in medium_keywords:
        if w in text_lower:
            score += 1

    if score >= 2:
        return "High"
    elif score == 1:
        return "Medium"
    else:
        return "Low"

# STEP 6 — Enter Entity Name
entity = input("Enter Company or Individual Name: ")

articles = fetch_news(entity, limit=8)
articles

# STEP 7 — Process Articles
processed = []

for art in articles:
    summary = summarize(art["summary"])
    risk = risk_level(summary)

    processed.append({
        "Title": art["title"],
        "Summary": summary,
        "Risk Level": risk,
        "Source Link": art["link"],
        "Published": art["published"],
    })

df = pd.DataFrame(processed)
df

# STEP 8 — Visualize Risk Levels
df['Risk Level'].value_counts().plot(kind='pie', autopct='%1.1f%%', figsize=(5,5))
plt.title("Risk Distribution")
plt.show()

# STEP 9 — Export CSV
df.to_csv(f"SAM-Radar_{entity.replace(' ','_')}.csv", index=False)
print("CSV Exported Successfully!")

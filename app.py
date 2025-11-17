import streamlit as st
import feedparser
import requests
import pandas as pd
import urllib.parse
import matplotlib.pyplot as plt

st.set_page_config(page_title="SAM-Radar", layout="wide")

st.title("🛰️ SAM-Radar — Smart Adverse Media Radar")
st.write("Scan multiple news sources for possible adverse media related to any entity.")

entity = st.text_input("Company or Individual Name")
limit = st.slider("Number of articles to fetch (per source)", 3, 15, 8)

# -------------------------------------------------------------------
# MULTI-SOURCE NEWS SEARCH
# -------------------------------------------------------------------
def fetch_news(entity, limit=10):
    articles = []

    # ---------------- GOOGLE NEWS ----------------
    try:
        query = urllib.parse.quote(entity + " sanctions fraud crime")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        for item in feed.entries[:limit]:
            articles.append({
                "source": "Google News",
                "title": item.title,
                "summary": getattr(item, "summary", ""),
                "link": item.link,
                "published": getattr(item, "published", "N/A")
            })
    except:
        pass

    # ---------------- DUCKDUCKGO NEWS ----------------
    try:
        ddg_url = f"https://duckduckgo.com/?q={entity}+sanctions+fraud+crime&ia=news"
        html = requests.get(ddg_url, headers={"User-Agent": "Mozilla/5.0"}).text
        blocks = html.split('"result__body"')[1:limit+1]

        for b in blocks:
            try:
                title = b.split('result__title">')[1].split("</a>")[0]
                link = b.split('href="')[1].split('"')[0]
                articles.append({
                    "source": "DuckDuckGo",
                    "title": title,
                    "summary": "",
                    "link": link,
                    "published": "N/A"
                })
            except:
                continue
    except:
        pass

    # ---------------- BING NEWS ----------------
    try:
        bing = f"https://www.bing.com/news/search?q={entity}+sanctions+fraud+crime"
        html = requests.get(bing, headers={"User-Agent": "Mozilla/5.0"}).text
        blocks = html.split('class="news-card"')[1:limit+1]

        for b in blocks:
            try:
                title = b.split("<a")[2].split(">")[1].split("</a>")[0]
                link = b.split('href="')[1].split('"')[0]
                articles.append({
                    "source": "Bing News",
                    "title": title,
                    "summary": "",
                    "link": link,
                    "published": "N/A"
                })
            except:
                continue
    except:
        pass

    return articles


# -------------------------------------------------------------------
# SIMPLE SUMMARIZER
# -------------------------------------------------------------------
def summarize(text):
    return text[:300] + "..."


# -------------------------------------------------------------------
# RISK SCORING LOGIC
# -------------------------------------------------------------------
def risk_level(text):
    t = text.lower()

    high = [
        "fraud","money laundering","scam","crime","corruption",
        "arrest","sanction","terrorist","lawsuit","illegal","charged"
    ]
    medium = ["investigation","probe","regulatory","unethical","review"]

    score = 0
    for w in high:
        if w in t:
            score += 2
    for w in medium:
        if w in t:
            score += 1

    if score >= 2:
        return "High"
    if score == 1:
        return "Medium"
    return "Low"


# -------------------------------------------------------------------
# RUN SCAN
# -------------------------------------------------------------------
if st.button("🔍 Scan Now"):
    with st.spinner("Scanning news across multiple sources..."):
        raw = fetch_news(entity, limit)

        processed = []
        for a in raw:
            text = a["title"] + " " + (a["summary"] or "")
            summary = summarize(text)
            risk = risk_level(summary)

            processed.append({
                "Source": a["source"],
                "Title": a["title"],
                "Summary": summary,
                "Risk Level": risk,
                "Published": a["published"],
                "Link": a["link"],
            })

        df = pd.DataFrame(processed)

        st.subheader("Results")
        st.dataframe(df, height=500)

        # ---------------- Risk Chart ----------------
        st.subheader("Risk Chart")

        if df.empty:
            st.warning("No articles found. Try alternative spelling.")
        else:
            fig, ax = plt.subplots()
            df["Risk Level"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax)
            st.pyplot(fig)

        # ---------------- CSV Export ----------------
        st.download_button(
            "⬇️ Download CSV Report",
            df.to_csv(index=False).encode("utf-8"),
            "SAM-Radar-Report.csv",
            "text/csv"
        )

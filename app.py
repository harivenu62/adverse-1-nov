import streamlit as st
import feedparser
import requests
import pandas as pd
import urllib.parse
import matplotlib.pyplot as plt

st.set_page_config(page_title="SAM-Radar", layout="wide")

st.title("🛰️ SAM-Radar — Smart Adverse Media Radar")
st.write("Enter an entity name to scan news for possible adverse media.")

entity = st.text_input("Company or Individual Name")
limit = st.slider("Number of articles to fetch", 5, 20, 8)

def fetch_news(entity, limit=10):
    query = urllib.parse.quote(f"{entity} fraud OR scam OR money laundering OR crime OR corruption")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    articles = []
    for i in feed.entries[:limit]:
        articles.append({
            "title": i.title,
            "summary": getattr(i, "summary", ""),
            "link": i.link,
            "published": getattr(i, "published", "N/A")
        })
    return articles

def summarize(text):
    return text[:300] + "..."

def risk_level(text):
    t = text.lower()
    high = ["fraud", "money laundering", "scam", "crime", "corruption", "arrest"]
    medium = ["probe", "investigation", "regulatory"]

    score = 0
    for w in high:
        if w in t:
            score += 2
    for w in medium:
        if w in t:
            score += 1

    if score >= 2: return "High"
    if score == 1: return "Medium"
    return "Low"

if st.button("🔍 Scan Now"):
    with st.spinner("Scanning news..."):
        articles = fetch_news(entity, limit)
        output = []
        for a in articles:
            summary = summarize(a["summary"])
            risk = risk_level(summary)
            output.append({
                "Title": a["title"],
                "Summary": summary,
                "Risk Level": risk,
                "Source Link": a["link"],
                "Published": a["published"],
            })

        df = pd.DataFrame(output)

        st.subheader("Results")
        st.dataframe(df)

        st.subheader("Risk Chart")
        fig, ax = plt.subplots()
        df["Risk Level"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax)
        st.pyplot(fig)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "SAM_Radar.csv", "text/csv")

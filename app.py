import streamlit as st
import feedparser
import requests
import pandas as pd
import urllib.parse
import matplotlib.pyplot as plt

st.set_page_config(page_title="SAM-Radar", layout="wide")

st.title("🛰️ SAM-Radar — Smart Adverse Media Radar")
st.write("Reliable multi-source adverse media scanner (GNews + NewsLookup RSS).")

entity = st.text_input("Company or Individual Name")
limit = st.slider("Number of articles to fetch", 5, 30, 10)


# -------------------------------------------------------------------
# SOURCE 1 — GNEWS API (demo token works)
# -------------------------------------------------------------------
def gnews_fetch(entity):
    url = f"https://gnews.io/api/v4/search?q={entity}%20sanctions&token=demo"
    r = requests.get(url)
    data = r.json()

    results = []
    if "articles" in data:
        for a in data["articles"]:
            results.append({
                "source": "GNews",
                "title": a.get("title", ""),
                "summary": a.get("description", ""),
                "link": a.get("url", ""),
                "published": a.get("publishedAt", "N/A"),
            })
    return results


# -------------------------------------------------------------------
# SOURCE 2 — NewsLookup RSS
# -------------------------------------------------------------------
def rss_fetch(entity, limit=10):
    query = urllib.parse.quote(entity)
    url = f"https://newslookup.com/rss/search?q={query}+sanctions+fraud+crime"
    feed = feedparser.parse(url)

    results = []
    for i in feed.entries[:limit]:
        results.append({
            "source": "NewsLookup",
            "title": i.title,
            "summary": getattr(i, "summary", ""),
            "link": i.link,
            "published": getattr(i, "published", "N/A"),
        })
    return results


# -------------------------------------------------------------------
# RISK SCORING
# -------------------------------------------------------------------
def risk_level(text):
    t = text.lower()
    high = ["fraud", "money laundering", "scam", "crime", "corruption", "sanction", "arrest"]
    medium = ["investigation", "probe", "review", "regulatory"]
    
    score = sum(w in t for w in high)*2 + sum(w in t for w in medium)
    return "High" if score >= 2 else "Medium" if score == 1 else "Low"


# -------------------------------------------------------------------
# RUN SCAN
# -------------------------------------------------------------------
if st.button("🔍 Scan Now"):
    with st.spinner("Scanning GNews and NewsLookup..."):
        
        g1 = gnews_fetch(entity)
        g2 = rss_fetch(entity, limit)

        combined = g1 + g2

        final = []
        for a in combined:
            text = a["title"] + " " + a["summary"]
            final.append({
                "Source": a["source"],
                "Title": a["title"],
                "Summary": a["summary"],
                "Risk Level": risk_level(text),
                "Published": a["published"],
                "Link": a["link"]
            })

        df = pd.DataFrame(final)

        st.subheader("Results")
        st.dataframe(df, height=500)

        if df.empty:
            st.warning("No articles found. Try another name.")
        else:
            st.subheader("Risk Chart")
            fig, ax = plt.subplots()
            df["Risk Level"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax)
            st.pyplot(fig)

        st.download_button("⬇️ Download CSV", df.to_csv(index=False), "SAM-Radar-Report.csv")

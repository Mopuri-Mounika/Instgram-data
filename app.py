import streamlit as st
import pandas as pd

# -----------------------------
# Load Data (replace with your file)
# -----------------------------
# Example DataFrame structure expected:
# URL | Date | Time | Captions | Likes | Comments | Sentiment_Label | Sentiment_Score
df = pd.read_csv("your_data.csv")  

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# -----------------------------
# Helper function for formatting likes
# -----------------------------
def format_indian_number(num):
    try:
        num = int(num)
        return f"{num:,}"
    except:
        return num

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

min_date, max_date = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

filtered = df[
    (df["Date"] >= pd.to_datetime(date_range[0]))
    & (df["Date"] <= pd.to_datetime(date_range[1]))
]

# -----------------------------
# Select Posts Section
# -----------------------------
st.markdown("## 🔗 Select Post(s)")

# Multi-select URLs
selected_post_urls = st.multiselect(
    "Choose one or more Post URLs", 
    filtered["URL"].unique().tolist()
)

# Confirm button
if st.button("View Selected Posts") and selected_post_urls:
    selected_posts = filtered[filtered["URL"].isin(selected_post_urls)]
    
    # --- Post Metadata Display ---
    st.subheader("📝 Post Details")
    for url in selected_post_urls:
        post_data = selected_posts[selected_posts["URL"] == url]
        caption_row = post_data[post_data["Captions"].notna()]
        if not caption_row.empty:
            caption_row = caption_row.iloc[0]
            st.markdown(f"**URL:** {url}")
            st.write(f"**Caption:** {caption_row['Captions']}")
            st.write(f"📅 {caption_row['Date'].date()} 🕒 {caption_row['Time']} ❤️ Likes: {format_indian_number(caption_row.get('Likes', 0))}")
            st.markdown("---")

    # --- Post Timeline ---
    st.subheader("📊 Post Timeline")

    if not selected_posts.empty:
        # Posts count per day
        posts_by_date = selected_posts.groupby("Date")["URL"].nunique().reset_index()
        posts_by_date.columns = ["Date", "Posts_Count"]
        st.markdown("**Number of Posts per Day**")
        st.bar_chart(posts_by_date.set_index("Date")["Posts_Count"])

        # Total comments per day
        comments_by_date = selected_posts[selected_posts["Comments"].notna()].groupby("Date")["Comments"].count().reset_index()
        comments_by_date.columns = ["Date", "Total_Comments"]
        st.markdown("**Total Comments per Day**")
        st.line_chart(comments_by_date.set_index("Date")["Total_Comments"])

        # Sentiment-wise comments per day
        sentiment_by_date = (
            selected_posts[selected_posts["Comments"].notna()]
            .groupby(["Date", "Sentiment_Label"])["Comments"]
            .count()
            .reset_index()
        )
        sentiment_pivot = sentiment_by_date.pivot(index="Date", columns="Sentiment_Label", values="Comments").fillna(0)
        st.markdown("**Sentiment-wise Comments per Day**")
        st.area_chart(sentiment_pivot)

    # --- Comments Explorer ---
    st.subheader("💬 Comments Explorer")

    sentiment_filter = st.selectbox("Filter Comments by Sentiment", ["All", "Positive", "Negative", "Neutral"])

    comments_only = selected_posts[selected_posts["Comments"].notna()].copy()
    comments_only["Sentiment_Label"] = comments_only["Sentiment_Label"].astype(str).str.strip().str.title()

    if sentiment_filter != "All":
        comments_only = comments_only[comments_only["Sentiment_Label"] == sentiment_filter]

    if not comments_only.empty:
        comment_table = comments_only[["URL", "Comments", "Sentiment_Label", "Sentiment_Score"]].reset_index(drop=True)
        st.dataframe(comment_table, use_container_width=True)
    else:
        st.info("No comments match your filter.")

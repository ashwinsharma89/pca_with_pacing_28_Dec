"""Retrieval Monitoring Dashboard."""
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

LOG_PATH = Path("data/vector_store/retrieval_metrics.jsonl")


@st.cache_data(show_spinner=False)
def load_metrics() -> pd.DataFrame:
    if not LOG_PATH.exists():
        return pd.DataFrame()

    records = []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                records.append(record)
            except json.JSONDecodeError:
                continue

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    if "timestamp" in df:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["date"] = df["timestamp"].dt.date
    df["filters"] = df.get("filters", {}).apply(lambda x: x or {})
    return df


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    st.sidebar.markdown("### Filter Metrics")

    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date) if min_date and max_date else (),
    )

    if date_range:
        start, end = date_range
        df = df[(df["date"] >= start) & (df["date"] <= end)]

    categories = sorted({filters.get("category") for filters in df["filters"] if filters})
    priorities = sorted({filters.get("priority") for filters in df["filters"] if filters})

    selected_categories = st.sidebar.multiselect("Category", [c for c in categories if c])
    selected_priorities = st.sidebar.multiselect("Priority", [p for p in priorities if p])

    if selected_categories:
        df = df[df["filters"].apply(lambda f: f.get("category") in selected_categories)]
    if selected_priorities:
        df = df[df["filters"].apply(lambda f: f.get("priority") in selected_priorities)]

    query_filter = st.sidebar.text_input("Search query substring")
    if query_filter:
        df = df[df["query"].str.contains(query_filter, case=False, na=False)]

    return df


def main():
    st.set_page_config(page_title="Retrieval Monitoring", page_icon="📈", layout="wide")
    st.title("📈 Retrieval Quality Dashboard")
    st.write("Track hybrid retriever performance, rerank usage, and metadata coverage.")

    df = load_metrics()
    if df.empty:
        st.warning("No retrieval metrics found. Run ingestion + queries to generate logs.")
        return

    df = filter_dataframe(df)
    if df.empty:
        st.info("No rows match the current filters.")
        return

    st.subheader("Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Queries", len(df))
    col2.metric("Avg Final Results", f"{df['final_results'].mean():.1f}")
    col3.metric("Vector Candidates", f"{df['vector_candidates'].mean():.1f}")
    col4.metric("Keyword Candidates", f"{df['keyword_candidates'].mean():.1f}")

    st.subheader("Query Volume")
    daily = df.groupby("date").size().reset_index(name="count")
    fig = px.line(daily, x="date", y="count", markers=True, title="Queries per Day")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Retriever Contributions")
    stacked = df[["vector_candidates", "keyword_candidates", "used_rerank"]].copy()
    stacked["cohere_rerank"] = stacked["used_rerank"].astype(int)
    stacked = stacked.melt(value_vars=["vector_candidates", "keyword_candidates", "cohere_rerank"],
                           var_name="source", value_name="value")
    fig = px.box(stacked, x="source", y="value", points="all",
                 title="Distribution of Candidates / Rerank usage")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Filter Distribution")
    filter_df = pd.DataFrame(df["filters"].tolist())
    if not filter_df.empty:
        filter_df["count"] = 1
        for col in [c for c in filter_df.columns if c != "count"]:
            top = (
                filter_df.groupby(col)["count"].sum().reset_index().sort_values("count", ascending=False)
            )
            fig = px.bar(top, x=col, y="count", title=f"Distribution: {col}")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No metadata filters recorded yet.")

    st.subheader("Raw Log")
    st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)


if __name__ == "__main__":
    main()

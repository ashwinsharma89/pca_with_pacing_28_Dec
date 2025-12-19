"""
Simple Q&A App - Skip complex analysis, go straight to questions
"""
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.express as px

# Load environment
load_dotenv()


def get_api_key(secret_key: str, env_var: str) -> str | None:
    """Prefer Streamlit secrets but fallback to environment variables."""
    try:
        api_keys = st.secrets["api_keys"]
        value = api_keys.get(secret_key)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(env_var)

# Page config
st.set_page_config(
    page_title="PCA Agent - Simple Q&A",
    page_icon="💬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'qa_engine' not in st.session_state:
    st.session_state.qa_engine = None

# Header
st.markdown('<h1 class="main-header">💬 PCA Agent - Simple Q&A</h1>', unsafe_allow_html=True)
st.markdown("**Upload your data and start asking questions immediately!**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### 📤 Upload Data")
    
    uploaded_file = st.file_uploader(
        "Upload campaign CSV",
        type=["csv"],
        help="CSV with campaign metrics"
    )
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        
        st.success(f"✅ Loaded {len(df):,} rows")
        
        with st.expander("📊 Data Summary"):
            st.write(f"**Columns:** {len(df.columns)}")
            st.write(f"**Rows:** {len(df):,}")
            
            if 'Total_Spent' in df.columns:
                st.metric("Total Spend", f"${df['Total_Spent'].sum():,.0f}")
            if 'Site_Visit' in df.columns:
                st.metric("Total Conversions", f"{df['Site_Visit'].sum():,.0f}")
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Tips")
    st.markdown("""
    - Ask questions naturally
    - Use suggested questions below
    - View SQL and results
    - Export data if needed
    """)

# Main content
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Initialize Q&A engine
    if st.session_state.qa_engine is None:
        api_key = get_api_key('OPENAI_API_KEY', 'OPENAI_API_KEY')
        if api_key:
            from src.query_engine import NaturalLanguageQueryEngine
            with st.spinner("🤖 Initializing Q&A Engine..."):
                engine = NaturalLanguageQueryEngine(api_key)
                engine.load_data(df)
                st.session_state.qa_engine = engine
            st.success("✅ Q&A Engine ready!")
        else:
            st.error("❌ OpenAI API key not found. Set OPENAI_API_KEY in .env file")
            st.stop()
    
    engine = st.session_state.qa_engine
    
    # Suggested questions
    st.markdown("### 🎯 Suggested Questions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 Basic Analysis**")
        basic_questions = [
            "What is the total spend by channel?",
            "Which campaigns have the highest ROAS?",
            "Show me top 10 campaigns by conversions"
        ]
        for q in basic_questions:
            if st.button(q, key=f"basic_{hash(q)}", use_container_width=True):
                st.session_state.current_question = q
    
    with col2:
        st.markdown("**🔍 Strategic Insights**")
        insight_questions = [
            "What hidden patterns exist in our top-performing campaigns?",
            "Identify top 20% of campaigns driving 80% of results",
            "What are the key drivers of campaign success?"
        ]
        for q in insight_questions:
            if st.button(q, key=f"insight_{hash(q)}", use_container_width=True):
                st.session_state.current_question = q
    
    with col3:
        st.markdown("**💡 Recommendations**")
        rec_questions = [
            "How should we reallocate budget to maximize conversions?",
            "Recommend which campaigns to scale or pause",
            "What specific actions should we take to improve performance?"
        ]
        for q in rec_questions:
            if st.button(q, key=f"rec_{hash(q)}", use_container_width=True):
                st.session_state.current_question = q
    
    st.markdown("---")
    
    # Question input
    st.markdown("### ❓ Ask Your Question")
    
    question = st.text_area(
        "Your question:",
        value=st.session_state.get('current_question', ''),
        placeholder="e.g., What are the top 3 optimization opportunities?",
        height=100,
        key="question_input"
    )
    
    col_a, col_b = st.columns([1, 4])
    with col_a:
        ask_button = st.button("🔍 Get Answer", type="primary", use_container_width=True)
    with col_b:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.current_question = ""
            st.rerun()
    
    if ask_button and question:
        with st.spinner("🤔 Analyzing your question..."):
            result = engine.ask(question)
            
            if result['success']:
                st.markdown("---")
                st.success("✅ Analysis Complete")
                
                # Answer
                st.markdown("### 📝 Answer")
                st.markdown(result['answer'])
                
                # Results
                st.markdown("### 📊 Data Results")
                
                if len(result['results']) > 0:
                    st.dataframe(result['results'], use_container_width=True)
                    
                    # Auto-generate chart if applicable
                    try:
                        if 'Date' in result['results'].columns and len(result['results']) > 1:
                            fig = px.line(result['results'], x='Date', y=result['results'].columns[1],
                                        title="Trend Over Time")
                            st.plotly_chart(fig, use_container_width=True)
                        elif len(result['results']) < 20 and len(result['results'].columns) >= 2:
                            fig = px.bar(result['results'], x=result['results'].columns[0], 
                                       y=result['results'].columns[1],
                                       title="Performance Comparison")
                            st.plotly_chart(fig, use_container_width=True)
                    except:
                        pass
                    
                    # Download button
                    csv = result['results'].to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name="query_results.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No results returned. This may be due to date filtering on historical data.")
                
                # SQL Query
                with st.expander("🔧 View Generated SQL Query"):
                    st.code(result['sql_query'], language="sql")
            
            else:
                st.error(f"❌ Error: {result['error']}")
                with st.expander("Error Details"):
                    st.code(result.get('error', 'Unknown error'))

else:
    # Welcome screen
    st.info("👆 Upload your campaign data CSV in the sidebar to get started!")
    
    st.markdown("### 🚀 Quick Start")
    st.markdown("""
    1. **Upload Data** - Use the file uploader in the sidebar
    2. **Ask Questions** - Use suggested questions or type your own
    3. **Get Insights** - View answers, data, and charts
    4. **Export Results** - Download data as CSV
    """)
    
    st.markdown("### 📊 Sample Questions You Can Ask")
    st.markdown("""
    **Basic Analysis:**
    - What is the total spend by channel?
    - Which campaigns have the highest ROAS?
    - Show me top 10 campaigns by conversions
    
    **Temporal Comparisons:**
    - Compare last week vs previous week performance
    - Show me the trend for CPA over the last 2 months
    - How did our CTR change month-over-month?
    
    **Strategic Insights:**
    - What hidden patterns exist in our top-performing campaigns?
    - Identify top 20% of campaigns driving 80% of results
    - What are the key drivers of campaign success?
    
    **Recommendations:**
    - How should we reallocate budget to maximize conversions?
    - Recommend which campaigns to scale or pause
    - What specific actions should we take to improve performance?
    
    **Advanced Analysis:**
    - Calculate performance volatility for each campaign
    - Identify performance anomalies using statistical outliers
    - Which campaigns show declining trends?
    """)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666;">PCA Agent - Simple Q&A | Built with Streamlit & OpenAI</div>',
    unsafe_allow_html=True
)

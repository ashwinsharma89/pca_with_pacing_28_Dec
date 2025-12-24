"""
Natural Language Q&A Page
Ask questions about your campaign data in plain English
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
from dotenv import load_dotenv

# Import shared components and utilities
from streamlit_apps.components import render_header, render_footer
from streamlit_apps.utils import apply_custom_css, init_session_state, load_historical_data
from streamlit_apps.config import APP_TITLE
from src.utils.data_loader import normalize_campaign_dataframe

# Load environment variables
load_dotenv()


def get_api_key(secret_key: str, env_var: str) -> str | None:
    """Prefer Streamlit secrets but fall back to os.getenv for local runs."""
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
    page_title=f"{APP_TITLE} - Q&A",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Initialize session state
init_session_state()

# Additional session state for this page
if 'qa_data' not in st.session_state:
    st.session_state.qa_data = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Page header
render_header(
    title="💬 Q&A",
    subtitle="Ask questions about your campaign data in plain English - No SQL required!"
)

# Sidebar info
with st.sidebar:
    st.markdown("### 💬 Q&A Capabilities")
    st.markdown("""
    - 🤖 **Natural Language**: Ask in plain English
    - 🔍 **Smart Search**: AI understands context
    - 📊 **Instant Results**: Get answers immediately
    - 📈 **Visual Insights**: Auto-generate charts
    - 💾 **Export Data**: Download results as CSV
    - 📝 **Query History**: Review past questions
    """)
    
    st.markdown("---")
    
    # Data status
    st.markdown("### 📊 Data Status")
    if st.session_state.qa_data is not None:
        st.success(f"✅ {len(st.session_state.qa_data)} campaigns loaded")
        st.metric("Rows", len(st.session_state.qa_data))
        st.metric("Columns", len(st.session_state.qa_data.columns))
    else:
        st.warning("⚠️ No data loaded")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🔄 Clear History", use_container_width=True):
        st.session_state.query_history = []
        st.success("✅ History cleared!")
    
    if st.session_state.qa_data is not None:
        if st.button("📥 Download Data", use_container_width=True):
            csv = st.session_state.qa_data.to_csv(index=False)
            st.download_button(
                label="Save CSV",
                data=csv,
                file_name=f"campaign_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# Main content
tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "📊 Data Explorer", "📖 Documentation"])

# ============================================================================
# TAB 1: Ask Questions
# ============================================================================
with tab1:
    # Data upload section
    if st.session_state.qa_data is None:
        st.markdown("## 📁 Upload Your Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload campaign data CSV",
                type=['csv'],
                help="Upload CSV with campaign performance metrics"
            )
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    df = normalize_campaign_dataframe(df)
                    st.session_state.qa_data = df
                    st.success(f"✅ Loaded {len(df)} rows with {len(df.columns)} columns")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
        
        with col2:
            st.info("💡 **Tip**: Upload CSV with campaign metrics like Spend, ROAS, Conversions, etc.")
            
            # Sample data button
            if st.button("📊 Load Sample Data", use_container_width=True):
                try:
                    sample_data = load_historical_data(use_sample=True)
                    if sample_data is not None:
                        df = normalize_campaign_dataframe(sample_data)
                        st.session_state.qa_data = df
                        st.success("✅ Sample data loaded!")
                        st.rerun()
                    else:
                        st.error("Sample data not found")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        
        # Sample CSV format
        st.markdown("### 📋 Expected CSV Format")
        st.code("""
Campaign_Name,Platform,Date,Spend,Conversions,ROAS,CPA,CTR,Impressions,Clicks
Q4_Holiday,google_ads,2024-10-01,45000,850,4.2,52.94,2.0,1250000,25000
Q4_Holiday,meta_ads,2024-10-01,32000,620,3.8,51.61,1.89,980000,18500
        """, language="csv")
    
    # Q&A Interface
    else:
        df = st.session_state.qa_data
        
        st.markdown("## 💬 Ask Your Question")
        
        # Query mode selection
        query_mode = st.radio(
            "Choose query mode:",
            options=["🤖 Natural Language (AI-powered)", "📝 Direct SQL Query"],
            horizontal=True
        )
        
        if query_mode == "🤖 Natural Language (AI-powered)":
            # Natural language mode
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**Ask any question about your data:**")
                
                # Suggested questions
                with st.expander("💡 Suggested Questions", expanded=True):
                    suggested_questions = [
                        "Which campaign had the highest ROAS?",
                        "What is the total spend across all campaigns?",
                        "Show me the top 5 campaigns by conversions",
                        "Which platform performs best on average?",
                        "Compare spend between google_ads and meta_ads",
                        "What is the average CPA for campaigns with ROAS > 4?",
                        "Which campaigns spent more than $50,000?",
                        "Show me campaigns with CTR above 2%"
                    ]
                    
                    cols = st.columns(2)
                    for i, q in enumerate(suggested_questions):
                        with cols[i % 2]:
                            if st.button(q, key=f"suggested_{i}", use_container_width=True):
                                st.session_state.current_question = q
                
                # Question input
                question = st.text_input(
                    "Your question:",
                    value=st.session_state.get('current_question', ''),
                    placeholder="e.g., Which campaign had the best ROAS?",
                    key="question_input"
                )
            
            with col2:
                st.markdown("**Quick Stats:**")
                st.metric("Total Campaigns", df['Campaign_Name'].nunique() if 'Campaign_Name' in df.columns else len(df))
                if 'Spend' in df.columns:
                    st.metric("Total Spend", f"${df['Spend'].sum():,.0f}")
                if 'ROAS' in df.columns:
                    st.metric("Avg ROAS", f"{df['ROAS'].mean():.2f}x")
            
            # Ask button
            if st.button("🔍 Get Answer", type="primary", use_container_width=True):
                if question:
                    with st.spinner("🤔 Thinking..."):
                        try:
                            from src.query_engine import NaturalLanguageQueryEngine
                            
                            api_key = get_api_key('OPENAI_API_KEY', 'OPENAI_API_KEY')
                            if not api_key or api_key == 'your_openai_api_key_here':
                                st.error("❌ OpenAI API key not found. Set OPENAI_API_KEY in .env file.")
                                st.info("💡 Get your key at: https://platform.openai.com/api-keys")
                            else:
                                # Initialize query engine
                                engine = NaturalLanguageQueryEngine(api_key)
                                engine.load_data(df)
                                result = engine.ask(question)
                                
                                if result['success']:
                                    # Add to history
                                    st.session_state.query_history.append({
                                        'question': question,
                                        'timestamp': datetime.now(),
                                        'result': result
                                    })
                                    
                                    # Display answer
                                    st.markdown("---")
                                    st.success("✅ Answer:")
                                    st.markdown(f"### {result['answer']}")
                                    
                                    # Show SQL query
                                    with st.expander("🔧 Generated SQL Query"):
                                        st.code(result['sql_query'], language="sql")
                                    
                                    # Show results
                                    if result.get('results') is not None and len(result['results']) > 0:
                                        st.markdown("---")
                                        st.markdown("### 📊 Detailed Results")
                                        st.dataframe(result['results'], use_container_width=True)
                                        
                                        # Download button
                                        csv = result['results'].to_csv(index=False)
                                        st.download_button(
                                            label="📥 Download Results",
                                            data=csv,
                                            file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                            mime="text/csv"
                                        )
                                        
                                        # Auto-visualize if applicable
                                        if len(result['results']) > 1 and len(result['results']) < 50:
                                            st.markdown("---")
                                            st.markdown("### 📈 Visualization")
                                            
                                            # Try to create a chart
                                            try:
                                                result_df = result['results']
                                                if len(result_df.columns) >= 2:
                                                    # Bar chart
                                                    fig = px.bar(
                                                        result_df,
                                                        x=result_df.columns[0],
                                                        y=result_df.columns[1],
                                                        title=f"{result_df.columns[1]} by {result_df.columns[0]}"
                                                    )
                                                    st.plotly_chart(fig, use_container_width=True)
                                            except:
                                                pass
                                else:
                                    st.error(f"❌ Error: {result['error']}")
                        
                        except ImportError:
                            st.error("❌ Query engine not found. Make sure src/query_engine.py exists.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            import traceback
                            with st.expander("Error Details"):
                                st.code(traceback.format_exc())
                else:
                    st.warning("⚠️ Please enter a question")
        
        else:
            # SQL mode
            st.markdown("**Write your SQL query:**")
            st.info("💡 Table name: `campaigns`")
            
            # SQL editor
            sql_query = st.text_area(
                "SQL Query:",
                height=150,
                placeholder="SELECT * FROM campaigns WHERE ROAS > 4.0 ORDER BY ROAS DESC LIMIT 10",
                help="Write SQL query to analyze your data"
            )
            
            # Execute button
            if st.button("▶️ Execute Query", type="primary"):
                if sql_query:
                    try:
                        import duckdb
                        
                        # Execute query
                        conn = duckdb.connect(':memory:')
                        conn.register('campaigns', df)
                        result_df = conn.execute(sql_query).fetchdf()
                        conn.close()
                        
                        # Display results
                        st.success(f"✅ Query executed! Returned {len(result_df)} rows.")
                        st.dataframe(result_df, use_container_width=True)
                        
                        # Download button
                        csv = result_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results",
                            data=csv,
                            file_name=f"sql_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    except Exception as e:
                        st.error(f"❌ SQL Error: {e}")
                else:
                    st.warning("⚠️ Please enter a SQL query")
        
        # Query history
        if st.session_state.query_history:
            st.markdown("---")
            st.markdown("## 📝 Query History")
            
            for i, item in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5
                with st.expander(f"🕐 {item['timestamp'].strftime('%H:%M:%S')} - {item['question'][:60]}..."):
                    st.markdown(f"**Question:** {item['question']}")
                    st.markdown(f"**Answer:** {item['result']['answer']}")
                    if item['result'].get('results') is not None:
                        st.dataframe(item['result']['results'], use_container_width=True)

# ============================================================================
# TAB 2: Data Explorer
# ============================================================================
with tab2:
    st.markdown("## 📊 Data Explorer")
    
    if st.session_state.qa_data is not None:
        df = st.session_state.qa_data
        
        # Data overview
        st.markdown("### 📋 Data Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            if 'Campaign_Name' in df.columns:
                st.metric("Unique Campaigns", df['Campaign_Name'].nunique())
        with col4:
            if 'Platform' in df.columns:
                st.metric("Platforms", df['Platform'].nunique())
        
        st.markdown("---")
        
        # Data preview
        st.markdown("### 🔍 Data Preview")
        st.dataframe(df.head(20), use_container_width=True)
        
        st.markdown("---")
        
        # Column info
        st.markdown("### 📊 Column Information")
        
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.astype(str),
            'Non-Null Count': df.count(),
            'Null Count': df.isnull().sum(),
            'Unique Values': df.nunique()
        })
        st.dataframe(col_info, use_container_width=True)
        
        st.markdown("---")
        
        # Summary statistics
        st.markdown("### 📈 Summary Statistics")
        
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            selected_col = st.selectbox("Select column for statistics:", numeric_cols)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean", f"{df[selected_col].mean():.2f}")
            with col2:
                st.metric("Median", f"{df[selected_col].median():.2f}")
            with col3:
                st.metric("Min", f"{df[selected_col].min():.2f}")
            with col4:
                st.metric("Max", f"{df[selected_col].max():.2f}")
            
            # Distribution chart
            fig = px.histogram(
                df,
                x=selected_col,
                nbins=30,
                title=f"Distribution of {selected_col}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Quick filters
        st.markdown("### 🔍 Quick Filters")
        
        filter_col = st.selectbox("Filter by column:", df.columns.tolist())
        
        if df[filter_col].dtype == 'object':
            # Categorical filter
            unique_values = df[filter_col].unique().tolist()
            selected_values = st.multiselect(f"Select {filter_col}:", unique_values, default=unique_values[:3] if len(unique_values) > 3 else unique_values)
            
            if selected_values:
                filtered_df = df[df[filter_col].isin(selected_values)]
                st.dataframe(filtered_df, use_container_width=True)
        else:
            # Numeric filter
            min_val = float(df[filter_col].min())
            max_val = float(df[filter_col].max())
            
            range_values = st.slider(
                f"Select {filter_col} range:",
                min_val,
                max_val,
                (min_val, max_val)
            )
            
            filtered_df = df[(df[filter_col] >= range_values[0]) & (df[filter_col] <= range_values[1])]
            st.dataframe(filtered_df, use_container_width=True)
    
    else:
        st.info("👆 Upload data in the 'Ask Questions' tab first!")

# ============================================================================
# TAB 3: Documentation
# ============================================================================
with tab3:
    st.markdown("## 📖 Documentation")
    
    st.markdown("""
    ### How to Use Natural Language Q&A
    
    #### 1. Upload Your Data
    - Click "Upload campaign data CSV"
    - Or use "Load Sample Data" to try it out
    - Supported formats: CSV files with campaign metrics
    
    #### 2. Ask Questions
    - **Natural Language Mode** (Recommended):
      - Type your question in plain English
      - AI converts it to SQL automatically
      - Get instant answers with visualizations
    
    - **SQL Mode** (Advanced):
      - Write SQL queries directly
      - Table name is `campaigns`
      - Full SQL syntax supported
    
    #### 3. Explore Results
    - View answers and detailed results
    - Download results as CSV
    - See generated SQL queries
    - Auto-generated visualizations
    
    #### 4. Review History
    - Check previous questions
    - Re-run past queries
    - Track your analysis
    
    ### 💡 Example Questions
    
    **Performance Analysis:**
    - "Which campaign had the highest ROAS?"
    - "Show me campaigns with ROAS above 4.0"
    - "What is the average CPA across all campaigns?"
    
    **Comparison:**
    - "Compare spend between Google Ads and Meta Ads"
    - "Which platform has the best conversion rate?"
    - "Show me the top 5 campaigns by revenue"
    
    **Filtering:**
    - "Which campaigns spent more than $50,000?"
    - "Show me campaigns with CTR above 2%"
    - "List campaigns from Q4 2024"
    
    **Aggregation:**
    - "What is the total spend across all campaigns?"
    - "Calculate average ROAS by platform"
    - "Sum of conversions by campaign type"
    
    ### 📊 Required CSV Columns
    
    **Recommended columns:**
    - `Campaign_Name`: Campaign identifier
    - `Platform`: Advertising platform
    - `Date`: Campaign date
    - `Spend`: Total spend
    - `Conversions`: Total conversions
    - `ROAS`: Return on ad spend
    - `CPA`: Cost per acquisition
    - `CTR`: Click-through rate
    - `Impressions`: Total impressions
    - `Clicks`: Total clicks
    
    **Optional columns:**
    - `Revenue`, `CPC`, `CPM`, `Reach`, `Frequency`, etc.
    
    ### 🔧 Technical Details
    
    **Natural Language Processing:**
    - Powered by OpenAI GPT models
    - Converts English to SQL
    - Understands context and intent
    - Handles complex queries
    
    **SQL Engine:**
    - DuckDB for fast in-memory queries
    - Full SQL syntax support
    - Optimized for analytics
    - No database setup required
    
    **Data Privacy:**
    - All processing is local
    - Data never leaves your environment
    - API calls only for NL processing
    - No data stored externally
    
    ### 🚀 Tips for Best Results
    
    1. **Be Specific**: "Show top 5 campaigns by ROAS" vs "Show campaigns"
    2. **Use Column Names**: Reference actual column names in your data
    3. **Start Simple**: Begin with basic questions, then get more complex
    4. **Check Results**: Review generated SQL to understand the query
    5. **Save Queries**: Download results for later analysis
    
    ### ❓ Troubleshooting
    
    **"API key not found"**
    - Set OPENAI_API_KEY in your .env file
    - Get key from https://platform.openai.com/api-keys
    
    **"Column not found"**
    - Check your CSV column names
    - Use Data Explorer tab to see available columns
    
    **"No results returned"**
    - Try rephrasing your question
    - Check if data matches your criteria
    - Use SQL mode to debug
    
    ### 📚 Additional Resources
    
    - Query Engine Guide: `docs/user-guides/QUERY_ENGINE_GUIDE.md`
    - Training Guide: `docs/user-guides/QA_TRAINING_GUIDE.md`
    - CSV Guide: `docs/user-guides/CSV_GUIDE.md`
    """)

# Footer
render_footer()

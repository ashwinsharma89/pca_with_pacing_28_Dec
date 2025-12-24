"""
Knowledge Base Page
Learn from URLs, YouTube videos, and PDFs to enhance analysis
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# Import shared components and utilities
from streamlit_apps.components import render_header, render_footer
from streamlit_apps.utils import apply_custom_css, init_session_state
from streamlit_apps.config import APP_TITLE

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title=f"{APP_TITLE} - Knowledge Base",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Initialize session state
init_session_state()

# Additional session state for this page
if 'knowledge_engine' not in st.session_state:
    st.session_state.knowledge_engine = None
if 'knowledge_items' not in st.session_state:
    st.session_state.knowledge_items = []

# Page header
render_header(
    title="📚 Knowledge Base",
    subtitle="Teach the AI by uploading URLs, YouTube videos, and PDFs"
)

# Sidebar info
with st.sidebar:
    st.markdown("### 📚 Knowledge Sources")
    st.markdown("""
    - 🌐 **Web URLs**: Articles, blogs, documentation
    - 🎥 **YouTube**: Video transcripts and tutorials
    - 📄 **PDFs**: Research papers, guides, reports
    """)
    
    st.markdown("---")
    st.markdown("### 💡 How It Works")
    st.markdown("""
    1. **Upload** knowledge sources
    2. **AI extracts** and processes content
    3. **Reasoning layer** uses knowledge for analysis
    4. **Enhanced insights** with best practices
    """)
    
    st.markdown("---")
    
    # Knowledge status
    if st.session_state.knowledge_items:
        st.markdown("### 📊 Knowledge Status")
        st.success(f"✅ {len(st.session_state.knowledge_items)} sources loaded")
        
        # Count by type
        url_count = sum(1 for item in st.session_state.knowledge_items if item['type'] == 'url')
        yt_count = sum(1 for item in st.session_state.knowledge_items if item['type'] == 'youtube')
        pdf_count = sum(1 for item in st.session_state.knowledge_items if item['type'] == 'pdf')
        
        st.metric("URLs", url_count)
        st.metric("YouTube", yt_count)
        st.metric("PDFs", pdf_count)
    else:
        st.info("No knowledge sources loaded yet")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear All Knowledge", use_container_width=True):
        st.session_state.knowledge_items = []
        st.session_state.knowledge_engine = None
        st.success("Knowledge base cleared!")
        st.rerun()

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["🌐 Add Knowledge", "📊 Knowledge Base", "🧠 Test Reasoning", "📖 Documentation"])

# ============================================================================
# TAB 1: Add Knowledge
# ============================================================================
with tab1:
    st.markdown("## 📥 Add Knowledge Sources")
    
    # Initialize engine if needed
    if st.session_state.knowledge_engine is None:
        try:
            from src.knowledge.enhanced_reasoning import EnhancedReasoningEngine
            
            # Check for API key
            use_anthropic = os.getenv('USE_ANTHROPIC', 'false').lower() == 'true'
            api_key = os.getenv('ANTHROPIC_API_KEY' if use_anthropic else 'OPENAI_API_KEY')
            
            if api_key and api_key not in ['your_openai_api_key_here', 'your_anthropic_api_key_here']:
                st.session_state.knowledge_engine = EnhancedReasoningEngine(use_anthropic=use_anthropic)
                st.success("✅ Knowledge engine initialized!")
            else:
                st.warning("⚠️ API key not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file.")
        except Exception as e:
            st.error(f"❌ Error initializing knowledge engine: {str(e)}")
            st.info("💡 Install required packages: `pip install youtube-transcript-api PyPDF2 beautifulsoup4 requests`")
    
    if st.session_state.knowledge_engine:
        # Source type selection
        source_type = st.radio(
            "Choose knowledge source type:",
            options=["🌐 Web URL", "🎥 YouTube Video", "📄 PDF Document"],
            horizontal=True
        )
        
        st.markdown("---")
        
        # URL Input
        if source_type == "🌐 Web URL":
            st.markdown("### 🌐 Learn from Web URL")
            st.info("💡 **Examples**: Blog posts, documentation, articles, research papers online")
            
            url = st.text_input(
                "Enter URL:",
                placeholder="https://example.com/article",
                help="Enter the full URL including https://"
            )
            
            if st.button("📥 Learn from URL", type="primary", use_container_width=True):
                if url:
                    with st.spinner("🤖 Extracting and processing content..."):
                        try:
                            result = st.session_state.knowledge_engine.learn_from_url(url)
                            
                            if result['success']:
                                st.success(f"✅ Successfully learned from URL!")
                                st.info(f"📊 Extracted {result['chunk_count']} chunks from: {result['title']}")
                                
                                # Show quality score
                                quality_score = result.get('quality_score', 0)
                                if quality_score >= 70:
                                    st.success(f"✅ Quality Score: {quality_score}/100 - Excellent")
                                elif quality_score >= 50:
                                    st.info(f"ℹ️ Quality Score: {quality_score}/100 - Good")
                                else:
                                    st.warning(f"⚠️ Quality Score: {quality_score}/100 - Fair")
                                
                                # Show validation warnings if any
                                validation = result.get('validation', {})
                                if validation.get('warnings'):
                                    with st.expander("⚠️ Quality Warnings"):
                                        for warning in validation['warnings']:
                                            st.warning(warning)
                                
                                # Add to knowledge items
                                st.session_state.knowledge_items.append({
                                    'type': 'url',
                                    'source': url,
                                    'title': result['title'],
                                    'chunks': result['chunk_count'],
                                    'quality_score': quality_score,
                                    'validation_warnings': validation.get('warnings', []),
                                    'timestamp': datetime.now()
                                })
                                
                                # Show preview
                                with st.expander("📄 Content Preview"):
                                    st.text(result['content'][:500] + "...")
                            else:
                                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a URL")
        
        # YouTube Input
        elif source_type == "🎥 YouTube Video":
            st.markdown("### 🎥 Learn from YouTube Video")
            st.info("💡 **Examples**: Tutorials, webinars, conference talks, product demos")
            
            video_url = st.text_input(
                "Enter YouTube URL:",
                placeholder="https://www.youtube.com/watch?v=VIDEO_ID",
                help="Enter the full YouTube video URL"
            )
            
            if st.button("📥 Learn from YouTube", type="primary", use_container_width=True):
                if video_url:
                    with st.spinner("🤖 Extracting video transcript..."):
                        try:
                            result = st.session_state.knowledge_engine.learn_from_youtube(video_url)
                            
                            if result['success']:
                                st.success(f"✅ Successfully learned from YouTube video!")
                                st.info(f"📊 Extracted {result['chunk_count']} chunks from {result.get('duration', 0):.0f}s video")
                                
                                # Add to knowledge items
                                st.session_state.knowledge_items.append({
                                    'type': 'youtube',
                                    'source': video_url,
                                    'video_id': result['video_id'],
                                    'chunks': result['chunk_count'],
                                    'duration': result.get('duration', 0),
                                    'timestamp': datetime.now()
                                })
                                
                                # Show preview
                                with st.expander("📄 Transcript Preview"):
                                    st.text(result['content'][:500] + "...")
                            else:
                                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                                if 'transcript' in result.get('error', '').lower():
                                    st.info("💡 This video may not have captions/subtitles available")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a YouTube URL")
        
        # PDF Input
        else:  # PDF Document
            st.markdown("### 📄 Learn from PDF Document")
            st.info("💡 **Examples**: Research papers, whitepapers, guides, reports")
            
            uploaded_file = st.file_uploader(
                "Upload PDF file:",
                type=['pdf'],
                help="Upload a PDF document to extract knowledge from"
            )
            
            if uploaded_file:
                if st.button("📥 Learn from PDF", type="primary", use_container_width=True):
                    with st.spinner("🤖 Extracting text from PDF..."):
                        try:
                            # Save uploaded file temporarily
                            temp_path = f"temp_{uploaded_file.name}"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            result = st.session_state.knowledge_engine.learn_from_pdf(temp_path)
                            
                            # Clean up temp file
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            
                            if result['success']:
                                st.success(f"✅ Successfully learned from PDF!")
                                st.info(f"📊 Extracted {result['chunk_count']} chunks from {result['page_count']} pages")
                                
                                # Add to knowledge items
                                st.session_state.knowledge_items.append({
                                    'type': 'pdf',
                                    'source': uploaded_file.name,
                                    'filename': result['filename'],
                                    'chunks': result['chunk_count'],
                                    'pages': result['page_count'],
                                    'timestamp': datetime.now()
                                })
                                
                                # Show preview
                                with st.expander("📄 Content Preview"):
                                    st.text(result['content'][:500] + "...")
                            else:
                                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

# ============================================================================
# TAB 2: Knowledge Base
# ============================================================================
with tab2:
    st.markdown("## 📚 Current Knowledge Base")
    
    if st.session_state.knowledge_items:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sources", len(st.session_state.knowledge_items))
        with col2:
            total_chunks = sum(item.get('chunks', 0) for item in st.session_state.knowledge_items)
            st.metric("Total Chunks", total_chunks)
        with col3:
            url_count = sum(1 for item in st.session_state.knowledge_items if item['type'] == 'url')
            st.metric("URLs", url_count)
        with col4:
            yt_count = sum(1 for item in st.session_state.knowledge_items if item['type'] == 'youtube')
            st.metric("YouTube", yt_count)
        
        st.markdown("---")
        
        # List all knowledge items
        st.markdown("### 📋 Knowledge Sources")
        
        for i, item in enumerate(st.session_state.knowledge_items, 1):
            with st.expander(f"{i}. {item['type'].upper()}: {item.get('title', item.get('filename', item.get('source', 'Unknown')))}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Type:** {item['type']}")
                    st.markdown(f"**Source:** {item['source']}")
                    st.markdown(f"**Chunks:** {item.get('chunks', 0)}")
                    st.markdown(f"**Added:** {item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    if item['type'] == 'youtube':
                        st.markdown(f"**Duration:** {item.get('duration', 0):.0f}s")
                    elif item['type'] == 'pdf':
                        st.markdown(f"**Pages:** {item.get('pages', 0)}")
                
                with col2:
                    if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.knowledge_items.pop(i-1)
                        st.rerun()
    else:
        st.info("👆 No knowledge sources added yet. Go to 'Add Knowledge' tab to start!")

# ============================================================================
# TAB 3: Test Reasoning
# ============================================================================
with tab3:
    st.markdown("## 🧠 Test Knowledge-Enhanced Reasoning")
    
    if not st.session_state.knowledge_engine:
        st.warning("⚠️ Knowledge engine not initialized. Please configure API keys.")
    elif not st.session_state.knowledge_items:
        st.info("👆 Add some knowledge sources first to test reasoning!")
    else:
        st.markdown("Ask a question and see how the AI uses learned knowledge:")
        
        question = st.text_area(
            "Your question:",
            placeholder="e.g., How can I improve my ROAS for Performance Max campaigns?",
            height=100
        )
        
        use_knowledge = st.checkbox("Use knowledge base", value=True)
        
        if st.button("🧠 Analyze with AI", type="primary", use_container_width=True):
            if question:
                with st.spinner("🤖 AI is thinking..."):
                    try:
                        result = st.session_state.knowledge_engine.analyze_with_knowledge(
                            query=question,
                            use_knowledge=use_knowledge
                        )
                        
                        if result['success']:
                            st.markdown("---")
                            st.markdown("### 💡 AI Response")
                            st.markdown(result['response'])
                            
                            st.markdown("---")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Used Knowledge Base", "Yes" if result['used_knowledge'] else "No")
                            with col2:
                                sources = result.get('knowledge_sources', {})
                                st.metric("Knowledge Sources", sources.get('total_documents', 0))
                        else:
                            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a question")

# ============================================================================
# TAB 4: Documentation
# ============================================================================
with tab4:
    st.markdown("## 📖 Knowledge Base Documentation")
    
    st.markdown("""
    ### How the Knowledge Base Works
    
    The PCA Agent can learn from external sources to enhance its analysis and recommendations.
    
    #### 🌐 Web URLs
    - Extracts text content from web pages
    - Processes articles, blog posts, documentation
    - Removes navigation, ads, and other non-content elements
    - **Use cases**: Industry best practices, platform updates, case studies
    
    #### 🎥 YouTube Videos
    - Extracts video transcripts/captions
    - Processes tutorial videos, webinars, conference talks
    - Includes timestamps for reference
    - **Use cases**: Video tutorials, product demos, expert talks
    
    #### 📄 PDF Documents
    - Extracts text from PDF files
    - Processes research papers, whitepapers, guides
    - Maintains page structure
    - **Use cases**: Research papers, detailed guides, reports
    
    ### Integration with Reasoning Layer
    
    When you ask questions or request analysis:
    
    1. **Query Processing**: Your question is analyzed
    2. **Context Retrieval**: Relevant knowledge chunks are retrieved
    3. **Enhanced Reasoning**: AI combines:
       - Your campaign data
       - Learned knowledge from sources
       - Built-in marketing expertise
    4. **Actionable Insights**: You get recommendations backed by both data and best practices
    
    ### Best Practices
    
    #### What to Upload
    - ✅ Industry best practices and guides
    - ✅ Platform-specific optimization tips
    - ✅ Case studies and success stories
    - ✅ Research papers on digital marketing
    - ✅ Product documentation and updates
    
    #### What NOT to Upload
    - ❌ Competitor confidential data
    - ❌ Copyrighted material without permission
    - ❌ Personal or sensitive information
    - ❌ Outdated information (check dates)
    
    ### Examples
    
    #### Example 1: Learning from Google Ads Blog
    ```
    URL: https://blog.google/products/ads/performance-max-tips/
    Use case: Learn latest Performance Max optimization strategies
    Result: AI can recommend PMax best practices when analyzing your campaigns
    ```
    
    #### Example 2: Learning from YouTube Tutorial
    ```
    Video: "Advanced Facebook Ads Targeting Strategies"
    Use case: Learn audience targeting techniques
    Result: AI suggests targeting improvements based on video insights
    ```
    
    #### Example 3: Learning from PDF Whitepaper
    ```
    PDF: "2024 Digital Marketing Benchmarks Report"
    Use case: Understand industry benchmarks
    Result: AI compares your performance against industry standards
    ```
    
    ### Technical Details
    
    **Text Processing:**
    - Content is split into chunks (1000 characters)
    - Chunks overlap by 200 characters for context
    - Metadata is preserved (source, timestamp, etc.)
    
    **Retrieval:**
    - Keyword-based matching (can be enhanced with embeddings)
    - Top 3-5 most relevant chunks are used
    - Source attribution is maintained
    
    **Privacy:**
    - All processing is local
    - Content is not shared externally
    - Knowledge base can be cleared anytime
    
    ### Required Packages
    
    To use all features, install:
    ```bash
    pip install youtube-transcript-api PyPDF2 beautifulsoup4 requests langchain
    ```
    
    ### Troubleshooting
    
    **"youtube-transcript-api not installed"**
    - Install: `pip install youtube-transcript-api`
    
    **"Video has no captions"**
    - YouTube video must have captions/subtitles
    - Try videos with auto-generated captions
    
    **"Could not extract from URL"**
    - Check if URL is accessible
    - Some sites block automated access
    - Try different URLs
    
    **"PDF extraction failed"**
    - Ensure PDF is text-based (not scanned images)
    - Try re-saving PDF with text layer
    - Install: `pip install PyPDF2`
    """)

# Footer
render_footer()

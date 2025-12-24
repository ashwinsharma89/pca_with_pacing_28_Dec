"""
Sidebar component
"""
import streamlit as st
from ..utils import init_session_state, has_historical_data, has_predictor_model
from ..utils.data_loader import load_historical_data
from ..config import APP_TITLE, VERSION


def render_sidebar():
    """Render the sidebar with navigation and status"""
    
    with st.sidebar:
        # Logo and title
        st.markdown(f"# {APP_TITLE}")
        st.markdown(f"**Version**: {VERSION}")
        st.markdown("---")
        
        # System status
        st.markdown("### 📊 System Status")
        
        # Data status
        if has_historical_data():
            st.success("✅ Data Loaded")
            data = st.session_state.get('historical_data')
            if data is not None:
                st.metric("Campaigns", len(data))
        else:
            st.warning("⚠️ No Data Loaded")
        
        # Model status
        if has_predictor_model():
            st.success("✅ Model Loaded")
            predictor = st.session_state.get('predictor')
            if predictor and hasattr(predictor, 'model_metrics'):
                metrics = predictor.model_metrics
                st.metric("Accuracy", f"{metrics.get('test_accuracy', 0):.1%}")
        else:
            st.info("ℹ️ Model Not Loaded")
        
        st.markdown("---")
        
        # Quick data upload
        st.markdown("### 📁 Quick Data Upload")
        st.caption("Upload historical campaign data")
        
        uploaded_file = st.file_uploader(
            "Upload CSV",
            type=['csv'],
            key='sidebar_upload',
            help="Upload historical campaign data"
        )
        
        if uploaded_file:
            data = load_historical_data(uploaded_file)
            if data is not None:
                st.session_state['historical_data'] = data
                st.success(f"✅ Loaded {len(data)} campaigns")
                st.rerun()
        
        # Load sample data button
        if not has_historical_data():
            if st.button("📊 Load Sample Data", use_container_width=True):
                data = load_historical_data(use_sample=True)
                if data is not None:
                    st.session_state['historical_data'] = data
                    st.success("✅ Sample data loaded!")
                    st.rerun()
                else:
                    st.error("❌ Sample data not found")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                init_session_state()
                st.rerun()
        
        st.markdown("---")
        
        # Help and documentation
        st.markdown("### 📚 Help & Support")
        st.markdown("- [📖 Documentation](https://github.com)")
        st.markdown("- [💬 Support](mailto:support@example.com)")
        st.markdown("- [🐛 Report Bug](https://github.com)")
        
        st.markdown("---")
        
        # Footer
        st.caption("© 2025 PCA Agent")
        st.caption("Powered by AI & ML")

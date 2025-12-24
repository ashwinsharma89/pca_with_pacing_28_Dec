# 🔄 Migration Guide - Moving to streamlit_apps/

This guide explains how to migrate existing Streamlit apps to the new organized structure.

---

## 📁 **New Folder Structure**

```
PCA_Agent/
├── streamlit_apps/              # ⭐ NEW - All Streamlit apps here
│   ├── __init__.py
│   ├── README.md
│   ├── app.py                   # Main unified dashboard
│   ├── config.py                # Configuration
│   │
│   ├── components/              # Reusable UI components
│   │   ├── __init__.py
│   │   ├── sidebar.py
│   │   ├── header.py
│   │   └── footer.py
│   │
│   ├── pages/                   # Individual feature pages
│   │   ├── __init__.py
│   │   ├── 1_📊_Campaign_Analysis.py
│   │   ├── 2_🔮_Predictive_Analytics.py
│   │   ├── 3_💬_Natural_Language_QA.py
│   │   ├── 4_📈_Reports.py
│   │   └── 5_⚙️_Settings.py
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── data_loader.py
│       ├── session_state.py
│       ├── styling.py
│       └── helpers.py
│
├── streamlit_app.py             # OLD - Campaign analysis
├── streamlit_predictive.py      # OLD - Predictive analytics
└── ... (other files)
```

---

## 🎯 **Migration Steps**

### **Step 1: Understand the New Structure**

The new structure separates:
- **Main app** (`app.py`) - Landing page with navigation
- **Pages** (`pages/`) - Individual features as separate pages
- **Components** (`components/`) - Reusable UI elements
- **Utils** (`utils/`) - Helper functions
- **Config** (`config.py`) - Centralized configuration

### **Step 2: Move Existing Apps**

#### **Option A: Keep Existing Apps (Temporary)**

For now, keep using existing apps:
```bash
# Campaign Analysis
streamlit run streamlit_app.py

# Predictive Analytics
streamlit run streamlit_predictive.py
```

#### **Option B: Use New Unified App**

Use the new unified dashboard:
```bash
# Main unified dashboard
streamlit run streamlit_apps/app.py
```

Then navigate to individual pages using sidebar.

### **Step 3: Migrate Content to Pages**

When ready to migrate, move content from old apps to new pages:

1. **Campaign Analysis** → `pages/1_📊_Campaign_Analysis.py`
   - Copy content from `streamlit_app.py`
   - Use shared components from `components/`
   - Use utilities from `utils/`

2. **Predictive Analytics** → `pages/2_🔮_Predictive_Analytics.py`
   - Copy content from `streamlit_predictive.py`
   - Use shared components
   - Use utilities

3. **Natural Language Q&A** → `pages/3_💬_Natural_Language_QA.py`
   - Create new page for Q&A features
   - Integrate DuckDB functionality
   - Use shared components

---

## 🔧 **How to Create a New Page**

### **Template for New Page**:

```python
"""
Page Title
Description of what this page does
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from streamlit_apps.components import render_header, render_footer
from streamlit_apps.utils import init_session_state, apply_custom_css
from streamlit_apps.config import APP_TITLE

# Page config
st.set_page_config(
    page_title=f"{APP_TITLE} - Page Name",
    page_icon="📊",
    layout="wide"
)

# Initialize
apply_custom_css()
init_session_state()

# Header
render_header(
    title="📊 Page Title",
    subtitle="Page description"
)

# Your page content here
st.write("Page content...")

# Footer
render_footer()
```

---

## 🎨 **Using Shared Components**

### **Sidebar**:
```python
from streamlit_apps.components import render_sidebar

render_sidebar()
```

### **Header**:
```python
from streamlit_apps.components import render_header

render_header(
    title="🔮 My Page",
    subtitle="Page description"
)
```

### **Footer**:
```python
from streamlit_apps.components import render_footer

render_footer()
```

---

## 🛠️ **Using Utilities**

### **Styling**:
```python
from streamlit_apps.utils import apply_custom_css

apply_custom_css()
```

### **Session State**:
```python
from streamlit_apps.utils import (
    init_session_state,
    get_session_value,
    set_session_value
)

init_session_state()
data = get_session_value('historical_data')
set_session_value('predictor', model)
```

### **Data Loading**:
```python
from streamlit_apps.utils import load_historical_data, load_model

data = load_historical_data(use_sample=True)
model = load_model('models/predictor.pkl')
```

### **Formatting**:
```python
from streamlit_apps.utils import (
    format_currency,
    format_percentage,
    format_number
)

st.write(format_currency(250000))  # $250.00K
st.write(format_percentage(0.85))   # 85.0%
st.write(format_number(1234567))    # 1,234,567
```

---

## 📊 **Configuration**

All configuration is in `config.py`:

```python
from streamlit_apps.config import (
    APP_TITLE,
    PRIMARY_COLOR,
    MODELS_DIR,
    DATA_DIR,
    SUPPORTED_PLATFORMS
)
```

---

## 🚀 **Running the Apps**

### **New Unified Dashboard**:
```bash
cd PCA_Agent
streamlit run streamlit_apps/app.py
```

### **Individual Pages** (if needed):
```bash
# Campaign Analysis only
streamlit run streamlit_apps/pages/1_📊_Campaign_Analysis.py

# Predictive Analytics only
streamlit run streamlit_apps/pages/2_🔮_Predictive_Analytics.py
```

### **Old Apps** (still work):
```bash
# Old campaign analysis
streamlit run streamlit_app.py

# Old predictive analytics
streamlit run streamlit_predictive.py
```

---

## ✅ **Benefits of New Structure**

### **Organization**:
- ✅ All Streamlit code in one place
- ✅ Clear separation of concerns
- ✅ Easy to find and maintain

### **Reusability**:
- ✅ Shared components (sidebar, header, footer)
- ✅ Shared utilities (formatting, data loading)
- ✅ Shared styling (consistent look)

### **Scalability**:
- ✅ Easy to add new pages
- ✅ Easy to add new features
- ✅ Easy to maintain

### **User Experience**:
- ✅ Unified navigation
- ✅ Consistent UI/UX
- ✅ Single entry point

---

## 📋 **Migration Checklist**

### **Phase 1: Setup** ✅
- [x] Create `streamlit_apps/` folder
- [x] Create folder structure
- [x] Create config file
- [x] Create utility files
- [x] Create component files
- [x] Create main app

### **Phase 2: Migration** (Next)
- [ ] Migrate Campaign Analysis to page
- [ ] Migrate Predictive Analytics to page
- [ ] Create Natural Language Q&A page
- [ ] Create Reports page
- [ ] Create Settings page

### **Phase 3: Testing** (After migration)
- [ ] Test all pages
- [ ] Test navigation
- [ ] Test data sharing
- [ ] Test components
- [ ] Test utilities

### **Phase 4: Cleanup** (Final)
- [ ] Remove old apps (optional)
- [ ] Update documentation
- [ ] Update README
- [ ] Create user guide

---

## 🎯 **Next Steps**

### **Immediate**:
1. ✅ Folder structure created
2. ✅ Config and utils ready
3. ✅ Components created
4. ✅ Main app ready

### **Next**:
1. Migrate existing apps to pages
2. Test unified dashboard
3. Add remaining features
4. Polish UI/UX

### **Future**:
1. Add more pages
2. Add more components
3. Add more utilities
4. Enhance features

---

## 💡 **Tips**

1. **Start Small**: Migrate one page at a time
2. **Test Often**: Test after each migration
3. **Use Components**: Leverage shared components
4. **Keep It Simple**: Don't over-engineer
5. **Document**: Update docs as you go

---

## 📚 **Resources**

- **Streamlit Multi-Page Apps**: https://docs.streamlit.io/library/get-started/multipage-apps
- **Streamlit Components**: https://docs.streamlit.io/library/components
- **Python Path Management**: https://docs.python.org/3/library/sys.html

---

**The new structure is ready! You can start migrating when ready.** 🚀

**For now, both old and new apps will work side by side.** ✅

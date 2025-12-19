# 🎨 PCA Agent - Streamlit Applications

This folder contains all Streamlit applications for the PCA Agent system.

---

## 📁 **Folder Structure**

```
streamlit_apps/
├── __init__.py                 # Package initialization
├── README.md                   # This file
├── app.py                      # Main unified dashboard (entry point)
├── config.py                   # Configuration and settings
│
├── components/                 # Reusable UI components
│   ├── __init__.py
│   ├── sidebar.py             # Sidebar component
│   ├── header.py              # Header component
│   ├── footer.py              # Footer component
│   ├── charts.py              # Chart components
│   └── forms.py               # Form components
│
├── pages/                      # Individual feature pages
│   ├── __init__.py
│   ├── 1_📊_Campaign_Analysis.py      # Vision-based analysis
│   ├── 2_🔮_Predictive_Analytics.py   # Predictive features
│   ├── 3_💬_Natural_Language_QA.py    # Q&A interface
│   ├── 4_📈_Reports.py                # Report generation
│   └── 5_⚙️_Settings.py               # Settings & config
│
└── utils/                      # Utility functions
    ├── __init__.py
    ├── data_loader.py         # Data loading utilities
    ├── session_state.py       # Session state management
    ├── styling.py             # CSS and styling
    └── helpers.py             # Helper functions
```

---

## 🚀 **How to Run**

### **Main Unified Dashboard**:
```bash
streamlit run streamlit_apps/app.py
```

### **Individual Features** (if needed):
```bash
# Campaign Analysis only
streamlit run streamlit_apps/pages/1_📊_Campaign_Analysis.py

# Predictive Analytics only
streamlit run streamlit_apps/pages/2_🔮_Predictive_Analytics.py

# Natural Language Q&A only
streamlit run streamlit_apps/pages/3_💬_Natural_Language_QA.py
```

---

## 📊 **Features**

### **1. Campaign Analysis** 📊
- Upload campaign screenshots
- Vision-based data extraction
- Automated insights generation
- PowerPoint report generation

### **2. Predictive Analytics** 🔮
- Campaign success prediction
- Early performance monitoring
- Budget allocation optimization
- Model training & management

### **3. Natural Language Q&A** 💬
- Ask questions about campaign data
- Natural language to SQL
- Interactive data exploration
- Training question system

### **4. Reports** 📈
- Generate PowerPoint reports
- Export data and insights
- Scheduled reporting
- Custom templates

### **5. Settings** ⚙️
- API configuration
- Model settings
- User preferences
- Data management

---

## 🎨 **Design Principles**

### **Unified Experience**:
- Consistent navigation
- Shared components
- Unified styling
- Single data model

### **Modular Architecture**:
- Reusable components
- Independent pages
- Shared utilities
- Easy maintenance

### **User-Friendly**:
- Intuitive navigation
- Clear instructions
- Helpful tooltips
- Error handling

---

## 🔧 **Configuration**

Configuration is managed in `config.py`:
- API keys
- Model paths
- Data directories
- UI settings
- Feature flags

---

## 📦 **Dependencies**

All dependencies are in the main `requirements.txt`:
- streamlit
- plotly
- pandas
- scikit-learn
- openai
- langchain
- And more...

---

## 🎯 **Development**

### **Adding a New Page**:
1. Create file in `pages/` folder
2. Follow naming convention: `N_emoji_Page_Name.py`
3. Import shared components from `components/`
4. Use utilities from `utils/`

### **Adding a New Component**:
1. Create file in `components/` folder
2. Define reusable function
3. Import in pages as needed

### **Styling**:
- Global styles in `utils/styling.py`
- Component-specific styles in component files
- Use consistent color scheme

---

## 📚 **Documentation**

- **User Guide**: See main documentation
- **API Reference**: See developer guide
- **Component Docs**: See individual component files

---

## 🎉 **Status**

- ✅ Folder structure created
- ✅ Main app template ready
- 🔄 Migration in progress
- 📝 Documentation ongoing

---

**This is the new home for all PCA Agent Streamlit applications!** 🏠

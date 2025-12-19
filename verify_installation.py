"""
Verify Predictive Analytics Installation
Check if all dependencies are installed correctly
"""
import sys

print("🔍 Verifying Predictive Analytics Installation...\n")

# Check Python version
print(f"✅ Python Version: {sys.version.split()[0]}")

# Check core dependencies
dependencies = {
    'scikit-learn': 'sklearn',
    'scipy': 'scipy',
    'xgboost': 'xgboost',
    'prophet': 'prophet',
    'joblib': 'joblib',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'streamlit': 'streamlit'
}

all_installed = True

for name, module in dependencies.items():
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✅ {name}: {version}")
    except ImportError:
        print(f"❌ {name}: NOT INSTALLED")
        all_installed = False

print("\n" + "="*50)

if all_installed:
    print("🎉 All dependencies installed successfully!")
    print("\n📊 Next Steps:")
    print("1. Launch dashboard: streamlit run streamlit_predictive.py")
    print("2. Upload historical data: data/historical_campaigns_sample.csv")
    print("3. Train your first model!")
else:
    print("⚠️  Some dependencies are missing.")
    print("Run: pip install -r requirements.txt")

print("="*50)

# Test predictive modules
print("\n🧪 Testing Predictive Modules...")

try:
    from src.predictive import (
        CampaignSuccessPredictor,
        EarlyPerformanceIndicators,
        BudgetAllocationOptimizer
    )
    print("✅ Campaign Success Predictor: Loaded")
    print("✅ Early Performance Indicators: Loaded")
    print("✅ Budget Allocation Optimizer: Loaded")
    print("\n🎉 All predictive modules are ready!")
except Exception as e:
    print(f"❌ Error loading modules: {str(e)}")

print("\n" + "="*50)
print("🚀 Ready to launch! Run: streamlit run streamlit_predictive.py")
print("="*50)

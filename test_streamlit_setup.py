#!/usr/bin/env python3
"""
Test Script for Streamlit Setup
Verifies that all modules can be imported and the setup is correct.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        from modules.auth import Auth
        print("✅ Auth module imported")
    except Exception as e:
        print(f"❌ Auth module import failed: {e}")
        return False
    
    try:
        from modules.task_manager import TaskManager
        print("✅ TaskManager module imported")
    except Exception as e:
        print(f"❌ TaskManager module import failed: {e}")
        return False
    
    try:
        from modules.time_tracker import TimeTracker
        print("✅ TimeTracker module imported")
    except Exception as e:
        print(f"❌ TimeTracker module import failed: {e}")
        return False
    
    try:
        from modules.analytics import Analytics
        print("✅ Analytics module imported")
    except Exception as e:
        print(f"❌ Analytics module import failed: {e}")
        return False
    
    try:
        from modules.intelligent_scheduler import IntelligentScheduler
        print("✅ IntelligentScheduler module imported")
    except Exception as e:
        print(f"❌ IntelligentScheduler module import failed: {e}")
        return False
    
    return True

def test_streamlit_imports():
    """Test if Streamlit and related packages can be imported."""
    print("\n🧪 Testing Streamlit imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported")
    except Exception as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported")
    except Exception as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported")
    except Exception as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported")
    except Exception as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    return True

def test_app_file():
    """Test if the app.py file exists and can be imported."""
    print("\n🧪 Testing app.py file...")
    
    if not os.path.exists("app.py"):
        print("❌ app.py file not found")
        return False
    
    try:
        # Try to import the app (this will test syntax)
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Basic syntax check
        compile(content, "app.py", "exec")
        print("✅ app.py syntax is valid")
        return True
    except Exception as e:
        print(f"❌ app.py syntax error: {e}")
        return False

def main():
    """Run all tests."""
    print("⏰ Smart Time-Tracking Streamlit Setup Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    if not test_streamlit_imports():
        all_passed = False
    
    if not test_app_file():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your Streamlit app is ready to run.")
        print("💡 Run 'streamlit run app.py' to start the application.")
    else:
        print("❌ Some tests failed. Please fix the issues before running the app.")
    
    return all_passed

if __name__ == "__main__":
    main()

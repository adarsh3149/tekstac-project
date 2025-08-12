#!/usr/bin/env python3
"""
Streamlit Launcher Script
Simple script to launch the Smart Time-Tracking Streamlit application.
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit application."""
    print("⏰ Starting Smart Time-Tracking & Task Scheduler...")
    print("=" * 60)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        print("✅ Streamlit installed successfully")
    
    # Check if other required packages are installed
    required_packages = [
        "plotly",
        "pandas",
        "numpy",
        "scikit-learn",
        "mysql-connector-python",
        "bcrypt"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed. Installing now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
    
    print("\n🚀 Launching Streamlit application...")
    print("📱 The app will open in your default browser")
    print("🌐 If it doesn't open automatically, go to: http://localhost:8501")
    print("\n" + "=" * 60)
    
    # Launch the Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        print("💡 Make sure you're in the correct directory and all files are present")

if __name__ == "__main__":
    main()

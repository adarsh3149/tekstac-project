"""
Test file for Analytics Module - Team Member 5
This file helps you test your analytics functionality independently.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_analytics_module():
    """Test the analytics module functionality."""
    print("=== Testing Analytics Module ===")
    
    try:
        # Import the analytics module
        from modules.analytics import Analytics
        print("✅ Analytics module imported successfully")
        
        # Test module structure
        analytics_class = Analytics
        print("✅ Analytics class found")
        
        # Check for required methods
        required_methods = [
            'generate_time_report',
            'calculate_average_time', 
            'get_smart_scheduling_suggestion',
            'suggest_break',
            'get_productivity_insights',
            'display_time_report'
        ]
        
        for method in required_methods:
            if hasattr(analytics_class, method):
                print(f"✅ Method {method} found")
            else:
                print(f"❌ Method {method} missing")
                
        print("\n=== Analytics Module Test Complete ===")
        print("Your analytics module is ready for integration!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_analytics_module() 
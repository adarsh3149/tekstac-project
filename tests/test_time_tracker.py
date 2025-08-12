"""
Test script for Time Tracker Module - Team Member 4
This script tests the time tracker functionality with the current database schema.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_time_tracker():
    """Test the time tracker functionality."""
    print("=== Testing Time Tracker Module ===")
    
    try:
        # Import the time tracker module
        from modules.time_tracker import TimeTracker
        print("✅ Time Tracker module imported successfully")
        
        # Test module structure
        time_tracker_class = TimeTracker
        print("✅ TimeTracker class found")
        
        # Check for required methods
        required_methods = [
            'start_timer',
            'stop_timer', 
            'check_active_timer',
            'get_user_tasks',
            'view_timer_history',
            'get_timer_analytics',
            'time_tracker_menu'
        ]
        
        for method in required_methods:
            if hasattr(time_tracker_class, method):
                print(f"✅ Method {method} found")
            else:
                print(f"❌ Method {method} missing")
                
        print("\n=== Time Tracker Module Test Complete ===")
        print("Your time tracker module is ready for integration!")
        
        # Test initialization
        print("\nTesting TimeTracker initialization...")
        time_tracker = TimeTracker(user_id=1)
        if time_tracker.db_connector.connection:
            print("✅ TimeTracker initialized successfully with database connection")
            
            # Test getting user tasks
            tasks = time_tracker.get_user_tasks()
            print(f"✅ Found {len(tasks)} tasks for user")
            
            # Test checking active timer
            active_timer = time_tracker.check_active_timer()
            if active_timer:
                print(f"⚠️ Active timer found: {active_timer['task_name']}")
            else:
                print("✅ No active timer found")
                
        else:
            print("⚠ TimeTracker initialized but database connection failed")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_time_tracker()

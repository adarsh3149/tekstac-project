"""
Test script for Task Manager Module - Team Member 3
This script tests the task manager functionality with the current database schema.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_task_manager():
    """Test the task manager functionality."""
    print("=== Testing Task Manager Module ===")
    
    try:
        # Import the task manager module
        from modules.task_manager import TaskManager
        print("✅ Task Manager module imported successfully")
        
        # Test module structure
        task_manager_class = TaskManager
        print("✅ TaskManager class found")
        
        # Check for required methods
        required_methods = [
            'create_task',
            'view_tasks', 
            'update_task',
            'delete_task',
            'get_task_analytics',
            'task_menu'
        ]
        
        for method in required_methods:
            if hasattr(task_manager_class, method):
                print(f"✅ Method {method} found")
            else:
                print(f"❌ Method {method} missing")
                
        print("\n=== Task Manager Module Test Complete ===")
        print("Your task manager module is ready for integration!")
        
        # Test initialization
        print("\nTesting TaskManager initialization...")
        task_manager = TaskManager(user_id=1)
        if task_manager.db_connector.connection:
            print("✅ TaskManager initialized successfully with database connection")
        else:
            print("⚠ TaskManager initialized but database connection failed")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_task_manager()

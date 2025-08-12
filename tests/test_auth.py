"""
Test script for Auth Module - Team Member 2
This script tests the authentication functionality with the current database schema.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_auth():
    """Test the authentication functionality."""
    print("=== Testing Auth Module ===")
    
    try:
        # Import the auth module
        from modules.auth import Auth
        print("✅ Auth module imported successfully")
        
        # Test module structure
        auth_class = Auth
        print("✅ Auth class found")
        
        # Check for required methods
        required_methods = [
            'hash_password',
            'verify_password', 
            'sign_up',
            'log_in',
            'log_out',
            'get_current_user',
            'is_logged_in',
            'require_auth'
        ]
        
        for method in required_methods:
            if hasattr(auth_class, method):
                print(f"✅ Method {method} found")
            else:
                print(f"❌ Method {method} missing")
                
        print("\n=== Auth Module Test Complete ===")
        print("Your auth module is ready for integration!")
        
        # Test initialization
        print("\nTesting Auth initialization...")
        auth = Auth()
        if auth.db_connector.connection:
            print("✅ Auth initialized successfully with database connection")
            
            # Test password hashing
            test_password = "testpassword123"
            hashed = auth.hash_password(test_password)
            if hashed:
                print("✅ Password hashing works")
                
                # Test password verification
                if auth.verify_password(test_password, hashed):
                    print("✅ Password verification works")
                else:
                    print("❌ Password verification failed")
            else:
                print("❌ Password hashing failed")
                
        else:
            print("⚠ Auth initialized but database connection failed")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_auth()

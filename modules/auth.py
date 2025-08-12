"""
Authentication Module - Team Member 2
Handles user authentication (login/signup) with password hashing.
Updated to work with the comprehensive database schema and integrate with other modules.
"""

import sys
import os
import bcrypt
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connector import DatabaseConnector

class Auth:
    def __init__(self):
        """
        Initialize Auth with database connection.
        """
        self.db_connector = DatabaseConnector()
        self.current_user = None
        
        # Connect to database
        if not self.db_connector.connect():
            print("❌ Failed to connect to database")
            return

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            print(f"❌ Error hashing password: {e}")
            return None

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            print(f"❌ Error verifying password: {e}")
            return False

    def sign_up(self, email=None, password=None, name=None) -> bool:
        """
        Register a new user.
        
        Args:
            email: User email (for Streamlit mode)
            password: User password (for Streamlit mode)
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            if email is None:  # CLI mode
                print("\n=== User Registration ===")
                
                # Get user details
                name = input("Full name: ").strip()
                if not name:
                    print("❌ Name is required!")
                    return False
                
                email = input("Email: ").strip().lower()
                if not email:
                    print("❌ Email is required!")
                    return False
                
                password = input("Password: ").strip()
                if len(password) < 6:
                    print("❌ Password must be at least 6 characters!")
                    return False
                
                confirm_password = input("Confirm password: ").strip()
                if password != confirm_password:
                    print("❌ Passwords don't match!")
                    return False
            else:
                # Streamlit mode validations
                email = (email or '').strip().lower()
                if not email:
                    print("❌ Email is required!")
                    return False
                if not password or len(password) < 6:
                    print("❌ Password must be at least 6 characters!")
                    return False
                # Derive a default name if none provided
                if not name:
                    name = email.split('@')[0] if '@' in email else email

            # Check if email already exists
            check_query = "SELECT user_id FROM users WHERE email = %s"
            existing_user = self.db_connector.execute_query(check_query, (email,))
            if existing_user:
                if email is None:
                    print("❌ Email already registered!")
                return False
            
            # Hash password
            hashed_password = self.hash_password(password)
            if not hashed_password:
                print("❌ Error hashing password!")
                return False
            
            # Insert new user
            insert_query = """
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
            """
            result = self.db_connector.execute_query(insert_query, (name, email, hashed_password))
            
            if result:
                print("✅ Registration successful!")
                print(f"   Welcome, {name}!")
                return True
            else:
                print("❌ Registration failed!")
                return False
                
        except Exception as e:
            print(f"❌ Error during registration: {e}")
            return False

    def log_in(self, email=None, password=None) -> bool:
        """
        Log in an existing user.
        
        Args:
            email: User email (for Streamlit mode)
            password: User password (for Streamlit mode)
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            if email is None:  # CLI mode
                print("\n=== User Login ===")
                
                email = input("Email: ").strip().lower()
                if not email:
                    print("❌ Email is required!")
                    return False
                
                password = input("Password: ").strip()
                if not password:
                    print("❌ Password is required!")
                    return False
            
            # Get user from database
            query = "SELECT user_id, name, email, password FROM users WHERE email = %s"
            user = self.db_connector.execute_query(query, (email,))
            
            if not user:
                if email is None:  # CLI mode
                    print("❌ Invalid email or password!")
                return False
            
            user = user[0]
            
            # Verify password
            if not self.verify_password(password, user['password']):
                if email is None:  # CLI mode
                    print("❌ Invalid email or password!")
                return False
            
            # Set current user
            self.current_user = {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email']
            }
            
            if email is None:  # CLI mode
                print(f"✅ Welcome back, {user['name']}!")
            return True
            
        except Exception as e:
            if email is None:  # CLI mode
                print(f"❌ Error during login: {e}")
            return False

    def log_out(self):
        """Log out the current user."""
        if self.current_user:
            print(f"👋 Goodbye, {self.current_user['name']}!")
            self.current_user = None
        else:
            print("⚠️ No user logged in.")

    def get_current_user(self):
        """Get the current logged-in user."""
        return self.current_user

    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in."""
        return self.current_user is not None

    def require_auth(self):
        """Decorator-like function to require authentication."""
        if not self.is_logged_in():
            print("❌ Please log in first!")
            return False
        return True

def main():
    """Main function to test authentication."""
    print("🔐 Authentication Module Test")
    
    auth = Auth()
    if not auth.db_connector.connection:
        print("❌ Failed to initialize Auth. Please check your database connection.")
        return
    
    while True:
        print("\n" + "="*50)
        print("🔐 AUTHENTICATION")
        print("="*50)
        print("1. 📝 Sign Up")
        print("2. 🔑 Log In")
        print("3. 🚪 Log Out")
        print("4. 👤 Current User")
        print("5. 🚪 Exit")
        print("-"*50)
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == '1':
            auth.sign_up()
        elif choice == '2':
            auth.log_in()
        elif choice == '3':
            auth.log_out()
        elif choice == '4':
            user = auth.get_current_user()
            if user:
                print(f"👤 Current user: {user['name']} ({user['email']})")
            else:
                print("👤 No user logged in")
        elif choice == '5':
            print("👋 Exiting Authentication. Goodbye!")
            break
        else:
            print("❌ Invalid option. Please choose 1-5.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()

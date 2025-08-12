"""
Database Connector Module - Team Member 1
Handles database connections and basic database operations.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnector:
    def __init__(self):
        """Initialize database connection parameters."""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', 'root')
        self.database = os.getenv('DB_NAME', 'smart_scheduler_db')
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Establish connection to the MySQL database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Successfully connected to the database.")
                return True
                
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query, params=None):
        """
        Execute a query and return results.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Parameters for the query
            
        Returns:
            list: Query results
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
                    
            self.cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            else:
                return self.cursor.rowcount
                
        except Error as e:
            print(f"Error executing query: {e}")
            return None

    def execute_many(self, query, params_list):
        """
        Execute multiple queries with different parameters.
        
        Args:
            query (str): SQL query to execute
            params_list (list): List of parameter tuples
            
        Returns:
            int: Number of affected rows
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
                    
            self.cursor.executemany(query, params_list)
            return self.cursor.rowcount
            
        except Error as e:
            print(f"Error executing multiple queries: {e}")
            return None

    def get_connection(self):
        """
        Get the current database connection.
        
        Returns:
            mysql.connector.connection: Database connection object
        """
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection

    def test_connection(self):
        """
        Test the database connection.
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        try:
            if self.connect():
                self.cursor.execute("SELECT 1")
                result = self.cursor.fetchone()
                self.disconnect()
                return result is not None
            return False
        except Error as e:
            print(f"Connection test failed: {e}")
            return False 
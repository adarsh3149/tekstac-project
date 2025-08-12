"""
Database Configuration - Team Member 1
Configuration settings for database connection.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'smart_scheduler_db'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Database connection settings
DB_SETTINGS = {
    'autocommit': True,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
} 
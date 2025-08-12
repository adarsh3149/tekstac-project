"""
Simple script to seed the database with dummy data for testing.
Run this script to populate your database with realistic test data.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.seed_data import SeedData

def main():
    """Main function to seed the database."""
    print("=== Smart Time-Tracking Database Seeder ===")
    print("This script will populate your database with dummy data for testing.")
    print("Make sure your database is running and accessible.")
    
    # Check if user wants to proceed
    response = input("\nDo you want to proceed with seeding the database? (y/n): ")
    if response.lower() != 'y':
        print("Seeding cancelled.")
        return
    
    seeder = SeedData()
    if seeder.seed_data():
        print("\n🎉 Database seeding completed successfully!")
        print("\nYou can now test your analytics module with realistic data.")
        print("\nSample data includes:")
        print("- 5 users with different work patterns")
        print("- 7 projects across different domains")
        print("- 25+ tasks with various statuses and categories")
        print("- 100+ time logs with realistic durations")
        print("\nNext steps:")
        print("1. Run 'python main.py' to test your analytics module")
        print("2. Run 'python test_analytics.py' to verify module functionality")
        print("3. Check the console output for analytics insights")
    else:
        print("\n❌ Database seeding failed. Please check your database connection.")
        print("\nTroubleshooting:")
        print("1. Make sure MySQL is running")
        print("2. Check your database credentials in .env file")
        print("3. Ensure the database 'smart_scheduler_db' exists")
        print("4. Run 'database/schema.sql' first to create the database structure")

if __name__ == "__main__":
    main() 
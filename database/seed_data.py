"""
Seed Data for Smart Time-Tracking and Task Scheduler
This file contains dummy data for testing the analytics module.
"""

import mysql.connector
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class SeedData:
    def __init__(self):
        """Initialize database connection for seeding data."""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', 'root')
        self.database = os.getenv('DB_NAME', 'smart_scheduler_db')
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish connection to the database."""
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
                print("Successfully connected to the database for seeding.")
                return True
                
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    def seed_data(self):
        """Seed the database with dummy data."""
        if not self.connect():
            return False

        try:
            print("Starting to seed database with dummy data...")
            
            # Clear existing data (optional - comment out if you want to keep existing data)
            self.clear_existing_data()
            
            # Seed users
            user_ids = self.seed_users()
            
            # Seed projects
            project_ids = self.seed_projects(user_ids)
            
            # Seed tasks
            task_ids = self.seed_tasks(user_ids, project_ids)
            
            # Seed time logs
            self.seed_time_logs(task_ids)
            
            print("✅ Database seeded successfully!")
            return True
            
        except Exception as e:
            print(f"Error seeding data: {e}")
            return False
        finally:
            self.disconnect()

    def clear_existing_data(self):
        """Clear existing data from tables (in reverse order of dependencies)."""
        try:
            print("Clearing existing data...")
            tables = ['time_logs', 'tasks', 'projects', 'users']
            for table in tables:
                self.cursor.execute(f"DELETE FROM {table}")
                print(f"Cleared {table} table")
        except mysql.connector.Error as e:
            print(f"Error clearing data: {e}")

    def seed_users(self):
        """Seed users table and return user IDs."""
        users_data = [
            ('John Doe', 'john.doe@email.com', 'hashed_password_123'),
            ('Jane Smith', 'jane.smith@email.com', 'hashed_password_456'),
            ('Mike Johnson', 'mike.johnson@email.com', 'hashed_password_789'),
            ('Sarah Wilson', 'sarah.wilson@email.com', 'hashed_password_101'),
            ('David Brown', 'david.brown@email.com', 'hashed_password_202')
        ]
        
        user_ids = []
        for user in users_data:
            self.cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                user
            )
            user_ids.append(self.cursor.lastrowid)
        
        print(f"✅ Seeded {len(users_data)} users")
        return user_ids

    def seed_projects(self, user_ids):
        """Seed projects table and return project IDs."""
        projects_data = [
            (user_ids[0], 'Web Application Development', 'Building a modern web app with React and Node.js'),
            (user_ids[0], 'Mobile App Project', 'iOS app development using Swift'),
            (user_ids[1], 'Data Analysis Project', 'Analyzing customer data for insights'),
            (user_ids[1], 'Marketing Campaign', 'Q4 marketing campaign planning'),
            (user_ids[2], 'Research Paper', 'Academic research on machine learning'),
            (user_ids[3], 'Design System', 'Creating a comprehensive design system'),
            (user_ids[4], 'Testing Framework', 'Building automated testing framework')
        ]
        
        project_ids = []
        for project in projects_data:
            self.cursor.execute(
                "INSERT INTO projects (user_id, project_name, description) VALUES (%s, %s, %s)",
                project
            )
            project_ids.append(self.cursor.lastrowid)
        
        print(f"✅ Seeded {len(projects_data)} projects")
        return project_ids

    def seed_tasks(self, user_ids, project_ids):
        """Seed tasks table and return task IDs."""
        # Get status and category IDs
        self.cursor.execute("SELECT status_id, status_name FROM task_status")
        statuses = {row['status_name']: row['status_id'] for row in self.cursor.fetchall()}
        
        self.cursor.execute("SELECT category_id, category_name FROM task_categories")
        categories = {row['category_name']: row['category_id'] for row in self.cursor.fetchall()}
        
        tasks_data = [
            # User 1 - Web Application Development
            (user_ids[0], project_ids[0], 'Design Database Schema', 'Create ERD and database design', statuses['completed'], categories['planning'], '2024-01-15'),
            (user_ids[0], project_ids[0], 'Setup React Project', 'Initialize React app with TypeScript', statuses['completed'], categories['coding'], '2024-01-20'),
            (user_ids[0], project_ids[0], 'Create User Authentication', 'Implement login/signup functionality', statuses['in-progress'], categories['coding'], '2024-01-25'),
            (user_ids[0], project_ids[0], 'Design UI Components', 'Create reusable UI components', statuses['pending'], categories['design'], '2024-01-30'),
            (user_ids[0], project_ids[0], 'Write Unit Tests', 'Create comprehensive test suite', statuses['pending'], categories['testing'], '2024-02-05'),
            
            # User 1 - Mobile App Project
            (user_ids[0], project_ids[1], 'Setup iOS Project', 'Initialize Xcode project', statuses['completed'], categories['coding'], '2024-01-10'),
            (user_ids[0], project_ids[1], 'Design App Interface', 'Create wireframes and mockups', statuses['in-progress'], categories['design'], '2024-01-18'),
            (user_ids[0], project_ids[1], 'Implement Core Features', 'Build main app functionality', statuses['pending'], categories['coding'], '2024-01-28'),
            
            # User 2 - Data Analysis Project
            (user_ids[1], project_ids[2], 'Data Collection', 'Gather customer data from various sources', statuses['completed'], categories['planning'], '2024-01-12'),
            (user_ids[1], project_ids[2], 'Data Cleaning', 'Clean and preprocess the data', statuses['completed'], categories['coding'], '2024-01-15'),
            (user_ids[1], project_ids[2], 'Exploratory Analysis', 'Perform initial data exploration', statuses['in-progress'], categories['coding'], '2024-01-20'),
            (user_ids[1], project_ids[2], 'Create Visualizations', 'Build charts and graphs', statuses['pending'], categories['design'], '2024-01-25'),
            
            # User 2 - Marketing Campaign
            (user_ids[1], project_ids[3], 'Campaign Planning', 'Plan Q4 marketing strategy', statuses['completed'], categories['planning'], '2024-01-08'),
            (user_ids[1], project_ids[3], 'Content Creation', 'Create marketing materials', statuses['in-progress'], categories['design'], '2024-01-15'),
            (user_ids[1], project_ids[3], 'Social Media Setup', 'Setup social media campaigns', statuses['pending'], categories['planning'], '2024-01-22'),
            
            # User 3 - Research Paper
            (user_ids[2], project_ids[4], 'Literature Review', 'Review existing research papers', statuses['completed'], categories['planning'], '2024-01-05'),
            (user_ids[2], project_ids[4], 'Data Collection', 'Collect research data', statuses['completed'], categories['coding'], '2024-01-12'),
            (user_ids[2], project_ids[4], 'Analysis', 'Perform statistical analysis', statuses['in-progress'], categories['coding'], '2024-01-18'),
            (user_ids[2], project_ids[4], 'Write Paper', 'Write the research paper', statuses['pending'], categories['documentation'], '2024-01-25'),
            
            # User 4 - Design System
            (user_ids[3], project_ids[5], 'Design Audit', 'Audit existing design patterns', statuses['completed'], categories['design'], '2024-01-10'),
            (user_ids[3], project_ids[5], 'Component Library', 'Create component library', statuses['in-progress'], categories['design'], '2024-01-15'),
            (user_ids[3], project_ids[5], 'Documentation', 'Document design system', statuses['pending'], categories['documentation'], '2024-01-20'),
            
            # User 5 - Testing Framework
            (user_ids[4], project_ids[6], 'Framework Design', 'Design testing framework architecture', statuses['completed'], categories['planning'], '2024-01-08'),
            (user_ids[4], project_ids[6], 'Core Implementation', 'Implement core testing functionality', statuses['in-progress'], categories['coding'], '2024-01-12'),
            (user_ids[4], project_ids[6], 'Integration Tests', 'Write integration tests', statuses['pending'], categories['testing'], '2024-01-18')
        ]
        
        task_ids = []
        for task in tasks_data:
            self.cursor.execute(
                """INSERT INTO tasks (user_id, project_id, task_name, description, status_id, category_id, due_date) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                task
            )
            task_ids.append(self.cursor.lastrowid)
        
        print(f"✅ Seeded {len(tasks_data)} tasks")
        return task_ids

    def seed_time_logs(self, task_ids):
        """Seed time logs table with realistic time tracking data."""
        time_logs_data = []
        
        # Generate time logs for the past 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for task_id in task_ids:
            # Generate 1-5 time logs per task
            num_logs = random.randint(1, 5)
            
            for _ in range(num_logs):
                # Random date within the last 30 days
                log_date = start_date + timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(9, 17),  # Work hours
                    minutes=random.randint(0, 59)
                )
                
                # Random duration between 15 minutes and 4 hours
                duration = random.randint(15, 240)
                
                # Calculate start and end times
                start_time = log_date
                end_time = start_time + timedelta(minutes=duration)
                
                time_logs_data.append((task_id, start_time, end_time, duration))
        
        # Insert time logs
        for time_log in time_logs_data:
            self.cursor.execute(
                "INSERT INTO time_logs (task_id, start_time, end_time, duration_minutes) VALUES (%s, %s, %s, %s)",
                time_log
            )
        
        print(f"✅ Seeded {len(time_logs_data)} time logs")
        return time_logs_data

def main():
    """Main function to seed the database."""
    print("=== Smart Time-Tracking Database Seeder ===")
    
    seeder = SeedData()
    if seeder.seed_data():
        print("\n🎉 Database seeding completed successfully!")
        print("\nYou can now test your analytics module with realistic data.")
        print("\nSample data includes:")
        print("- 5 users with different work patterns")
        print("- 7 projects across different domains")
        print("- 25+ tasks with various statuses and categories")
        print("- 100+ time logs with realistic durations")
        print("\nRun 'python main.py' to test your analytics module!")
    else:
        print("\n❌ Database seeding failed. Please check your database connection.")

if __name__ == "__main__":
    main() 
"""
Task Management Module - Team Member 3
Handles all CRUD operations related to tasks.
Updated to work with the comprehensive database schema and integrate with analytics.
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connector import DatabaseConnector
from modules.analytics import Analytics
from modules.intelligent_scheduler import IntelligentScheduler

class TaskManager:
    def __init__(self, user_id=1):
        """
        Initialize TaskManager with database connection and analytics.
        
        Args:
            user_id: ID of the logged-in user
        """
        self.user_id = user_id
        self.db_connector = DatabaseConnector()
        self.analytics = None
        self.scheduler = None
        
        # Connect to database
        if self.db_connector.connect():
            self.analytics = Analytics(self.db_connector.get_connection())
            self.scheduler = IntelligentScheduler(user_id)
            print("✅ Task Manager initialized successfully")
        else:
            print("❌ Failed to connect to database")
            return

    def get_categories(self):
        """Get all available task categories."""
        try:
            query = "SELECT category_id, category_name FROM task_categories ORDER BY category_name"
            categories = self.db_connector.execute_query(query)
            return categories if categories else []
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []

    def get_statuses(self):
        """Get all available task statuses."""
        try:
            query = "SELECT status_id, status_name FROM task_status ORDER BY status_name"
            statuses = self.db_connector.execute_query(query)
            return statuses if statuses else []
        except Exception as e:
            print(f"Error fetching statuses: {e}")
            return []

    def get_projects(self):
        """Get all projects for the current user."""
        try:
            query = "SELECT project_id, project_name FROM projects WHERE user_id = %s ORDER BY project_name"
            projects = self.db_connector.execute_query(query, (self.user_id,))
            return projects if projects else []
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []

    def create_project(self, project_name: str, description: str = None):
        """Create a project for the current user if it doesn't already exist.

        Returns the project_id of the existing or newly created project.
        """
        try:
            if not project_name or not project_name.strip():
                return None

            # Check if project exists
            exists_query = """
                SELECT project_id FROM projects
                WHERE user_id = %s AND LOWER(project_name) = LOWER(%s)
                LIMIT 1
            """
            existing = self.db_connector.execute_query(exists_query, (self.user_id, project_name.strip()))
            if existing:
                return existing[0]['project_id']

            insert_query = """
                INSERT INTO projects (user_id, project_name, description)
                VALUES (%s, %s, %s)
            """
            result = self.db_connector.execute_query(insert_query, (self.user_id, project_name.strip(), description))
            if result:
                id_result = self.db_connector.execute_query("SELECT LAST_INSERT_ID() AS last_id")
                return id_result[0]['last_id'] if id_result else None
            return None
        except Exception as e:
            print(f"Error creating project: {e}")
            return None

    def create_task(self, task_name=None, description=None, category_id=None, project_id=None, priority=None, due_date=None):
        """Create a new task with smart suggestions."""
        if task_name is None:  # CLI mode
            print("\n=== Create New Task ===")
            task_name = input("Task name: ").strip()
            if not task_name:
                print("❌ Task name is required!")
                return None
            
            description = input("Description (optional): ").strip() or None
            
            # Get categories
            categories = self.get_categories()
            if categories:
                print("\nAvailable categories:")
                for cat in categories:
                    print(f"  {cat['category_id']}. {cat['category_name']}")
                category_id = input("Category ID (optional): ").strip() or None
            else:
                category_id = None
            
            # Get projects
            projects = self.get_projects()
            if projects:
                print("\nAvailable projects:")
                for proj in projects:
                    print(f"  {proj['project_id']}. {proj['project_name']}")
                project_id = input("Project ID (optional): ").strip() or None
            else:
                project_id = None
            
            # Get due date
            due_date = input("Due date (YYYY-MM-DD) [optional]: ").strip() or None
            
            # Get smart duration prediction
            if self.scheduler:
                prediction = self.scheduler.predict_task_duration(
                    task_name, description, category_id, project_id
                )
                print(f"\n🤖 Smart Prediction:")
                print(f"   Estimated duration: {prediction['predicted_duration']} minutes")
                print(f"   Confidence: {prediction['confidence']}%")
                print(f"   Method: {prediction['method']}")
                
                use_prediction = input("\nUse this prediction for scheduling? (y/n): ").strip().lower()
                if use_prediction == 'y':
                    # Auto-schedule the task
                    scheduled_task = self.scheduler.create_smart_schedule([{
                        'name': task_name,
                        'description': description,
                        'category_id': category_id,
                        'project_id': project_id
                    }])
                    
                    if scheduled_task:
                        start_time = scheduled_task[0]['start_time']
                        print(f"\n📅 Task auto-scheduled for: {start_time.strftime('%Y-%m-%d %H:%M')}")
                        print(f"   Duration: {scheduled_task[0]['duration']} minutes")
                        print(f"   Category: {scheduled_task[0]['category']}")
            
            # Get status (default to pending)
            statuses = self.get_statuses()
            if statuses:
                print("\nAvailable statuses:")
                for status in statuses:
                    print(f"  {status['status_id']}. {status['status_name']}")
                status_id = input(f"Status ID (default: 1 for pending): ").strip() or 1
            else:
                status_id = 1
        
        else:  # Streamlit mode
            if not task_name:
                return None
            
            # Default status to pending (status_id = 1)
            status_id = 1
        
        try:
            # Insert the task
            query = """
                INSERT INTO tasks (user_id, project_id, task_name, description, status_id, category_id, due_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            result = self.db_connector.execute_query(
                query, 
                (self.user_id, project_id, task_name, description, status_id, category_id, due_date)
            )
            
            if result:
                # Get the inserted task ID
                task_id_result = self.db_connector.execute_query("SELECT LAST_INSERT_ID() AS last_id")
                task_id = task_id_result[0]['last_id'] if task_id_result else None
                
                if task_name is None:  # CLI mode
                    print("✅ Task created successfully!")
                    
                    # Get smart scheduling suggestion
                    if self.analytics:
                        suggestion = self.analytics.get_smart_scheduling_suggestion(self.user_id, task_name, category_id)
                        if suggestion['estimated_duration'] > 0:
                            print(f"\n💡 Smart Suggestion:")
                            print(f"   Estimated duration: {suggestion['estimated_duration']} minutes")
                            print(f"   Confidence level: {suggestion['confidence_level']}")
                            if suggestion['recommended_breaks']:
                                print(f"   Recommended breaks: {len(suggestion['recommended_breaks'])} break(s)")
                
                return task_id
            else:
                if task_name is None:  # CLI mode
                    print("❌ Failed to create task")
                return None
                
        except Exception as e:
            if task_name is None:  # CLI mode
                print(f"❌ Error creating task: {e}")
            return None

    def view_tasks(self):
        """View all tasks for the current user with detailed information."""
        try:
            query = """
                SELECT t.task_id, t.task_name, t.description, t.due_date,
                       ts.status_name, tc.category_name, p.project_name,
                       t.created_at
                FROM tasks t
                LEFT JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN projects p ON t.project_id = p.project_id
                WHERE t.user_id = %s
                ORDER BY t.created_at DESC
            """
            tasks = self.db_connector.execute_query(query, (self.user_id,))
            
            if not tasks:
                print("\n📝 No tasks found.")
                return
            
            print(f"\n📋 Your Tasks ({len(tasks)} total):")
            print("-" * 80)
            
            for task in tasks:
                status_emoji = {
                    'pending': '⏳',
                    'in-progress': '🔄',
                    'completed': '✅',
                    'cancelled': '❌'
                }.get(task['status_name'], '📝')
                
                print(f"{status_emoji} [{task['task_id']}] {task['task_name']}")
                if task['description']:
                    print(f"    Description: {task['description']}")
                print(f"    Status: {task['status_name']}")
                if task['category_name']:
                    print(f"    Category: {task['category_name']}")
                if task['project_name']:
                    print(f"    Project: {task['project_name']}")
                if task['due_date']:
                    print(f"    Due: {task['due_date']}")
                print()
                
        except Exception as e:
            print(f"❌ Error viewing tasks: {e}")

    def update_task(self):
        """Update an existing task."""
        print("\n=== Update Task ===")
        
        # First, show available tasks
        self.view_tasks()
        
        task_id = input("\nEnter task ID to update: ").strip()
        if not task_id:
            print("❌ Task ID is required!")
            return
        
        try:
            # Check if task exists and belongs to user
            check_query = "SELECT task_id FROM tasks WHERE task_id = %s AND user_id = %s"
            task_exists = self.db_connector.execute_query(check_query, (task_id, self.user_id))
            
            if not task_exists:
                print("❌ Task not found or doesn't belong to you!")
                return
            
            # Get current task info
            current_query = """
                SELECT t.task_name, t.description, t.due_date, ts.status_name, 
                       tc.category_name, p.project_name
                FROM tasks t
                LEFT JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN projects p ON t.project_id = p.project_id
                WHERE t.task_id = %s
            """
            current_task = self.db_connector.execute_query(current_query, (task_id,))
            
            if current_task:
                task = current_task[0]
                print(f"\nCurrent task: {task['task_name']}")
                print(f"Current status: {task['status_name']}")
                
                # Get new status
                statuses = self.get_statuses()
                if statuses:
                    print("\nAvailable statuses:")
                    for status in statuses:
                        print(f"  {status['status_id']}. {status['status_name']}")
                    new_status_id = input("New status ID: ").strip()
                    
                    if new_status_id:
                        update_query = "UPDATE tasks SET status_id = %s WHERE task_id = %s AND user_id = %s"
                        result = self.db_connector.execute_query(update_query, (new_status_id, task_id, self.user_id))
                        
                        if result:
                            print("✅ Task updated successfully!")
                        else:
                            print("❌ Failed to update task")
                    else:
                        print("❌ Status ID is required!")
                else:
                    print("❌ No statuses available")
            else:
                print("❌ Task not found!")
                
        except Exception as e:
            print(f"❌ Error updating task: {e}")

    def delete_task(self):
        """Delete a task."""
        print("\n=== Delete Task ===")
        
        # First, show available tasks
        self.view_tasks()
        
        task_id = input("\nEnter task ID to delete: ").strip()
        if not task_id:
            print("❌ Task ID is required!")
            return
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete task {task_id}? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Deletion cancelled.")
            return
        
        try:
            # Check if task exists and belongs to user
            check_query = "SELECT task_name FROM tasks WHERE task_id = %s AND user_id = %s"
            task_exists = self.db_connector.execute_query(check_query, (task_id, self.user_id))
            
            if not task_exists:
                print("❌ Task not found or doesn't belong to you!")
                return
            
            # Delete the task
            delete_query = "DELETE FROM tasks WHERE task_id = %s AND user_id = %s"
            result = self.db_connector.execute_query(delete_query, (task_id, self.user_id))
            
            if result:
                print("✅ Task deleted successfully!")
            else:
                print("❌ Failed to delete task")
                
        except Exception as e:
            print(f"❌ Error deleting task: {e}")

    def get_task_analytics(self):
        """Get analytics for the current user's tasks."""
        if not self.analytics:
            print("❌ Analytics module not available")
            return
        
        print("\n=== Task Analytics ===")
        
        try:
            # Get productivity insights
            insights = self.analytics.get_productivity_insights(self.user_id)
            print(f"📊 Productivity Insights:")
            print(f"   Most productive time: {insights['most_productive_time'] or 'Not enough data'}")
            print(f"   Average session length: {insights['average_session_length']} minutes")
            print(f"   Completion rate: {insights['completion_rate']}%")
            
            # Get category analytics
            category_analytics = self.analytics.get_category_analytics(self.user_id)
            if category_analytics['categories']:
                print(f"\n📈 Category Breakdown:")
                for category in category_analytics['categories']:
                    print(f"   {category['category_name']}: {category['total_tasks']} tasks, {category['total_time'] or 0} min")
            
        except Exception as e:
            print(f"❌ Error getting analytics: {e}")

    def get_total_tasks(self):
        """Get total number of tasks for the current user."""
        try:
            query = "SELECT COUNT(*) as count FROM tasks WHERE user_id = %s"
            result = self.db_connector.execute_query(query, (self.user_id,))
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"Error getting total tasks: {e}")
            return 0

    def get_completed_tasks(self):
        """Get number of completed tasks for the current user."""
        try:
            query = """
                SELECT COUNT(*) as count FROM tasks t
                JOIN task_status ts ON t.status_id = ts.status_id
                WHERE t.user_id = %s AND ts.status_name = 'completed'
            """
            result = self.db_connector.execute_query(query, (self.user_id,))
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"Error getting completed tasks: {e}")
            return 0

    def get_pending_tasks(self):
        """Get number of pending tasks for the current user."""
        try:
            query = """
                SELECT COUNT(*) as count FROM tasks t
                JOIN task_status ts ON t.status_id = ts.status_id
                WHERE t.user_id = %s AND ts.status_name IN ('pending', 'in_progress')
            """
            result = self.db_connector.execute_query(query, (self.user_id,))
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"Error getting pending tasks: {e}")
            return 0

    def get_todays_tasks(self):
        """Get tasks due today for the current user."""
        try:
            query = """
                SELECT t.task_id, t.task_name, t.description, t.due_date, ts.status_name as status,
                       tc.category_name, p.project_name
                FROM tasks t
                LEFT JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN projects p ON t.project_id = p.project_id
                WHERE t.user_id = %s AND DATE(t.due_date) = CURDATE()
                ORDER BY t.due_date ASC
            """
            return self.db_connector.execute_query(query, (self.user_id,)) or []
        except Exception as e:
            print(f"Error getting today's tasks: {e}")
            return []

    def get_active_tasks(self):
        """Get active tasks (pending and in progress) for the current user."""
        try:
            query = """
                SELECT t.task_id, t.task_name, t.description, t.due_date, ts.status_name as status,
                       tc.category_name, p.project_name
                FROM tasks t
                LEFT JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN projects p ON t.project_id = p.project_id
                WHERE t.user_id = %s AND ts.status_name IN ('pending', 'in-progress')
                ORDER BY t.due_date ASC
            """
            return self.db_connector.execute_query(query, (self.user_id,)) or []
        except Exception as e:
            print(f"Error getting active tasks: {e}")
            return []

    def update_task_category(self, task_id: int, category_id: int) -> bool:
        """Update the category of a task for the current user."""
        try:
            if not task_id:
                return False
            query = """
                UPDATE tasks
                SET category_id = %s
                WHERE task_id = %s AND user_id = %s
            """
            result = self.db_connector.execute_query(query, (category_id, task_id, self.user_id))
            return bool(result)
        except Exception as e:
            print(f"Error updating task category: {e}")
            return False

    def _get_status_id(self, status_name: str) -> int:
        """Resolve a human-readable status name to its status_id."""
        try:
            q = "SELECT status_id FROM task_status WHERE status_name = %s LIMIT 1"
            res = self.db_connector.execute_query(q, (status_name,))
            return res[0]['status_id'] if res else None
        except Exception:
            return None

    def update_task_status(self, task_id: int, status_name: str) -> bool:
        """Update task status by name for current user."""
        try:
            status_id = self._get_status_id(status_name)
            if not task_id or status_id is None:
                return False
            q = """
                UPDATE tasks
                SET status_id = %s
                WHERE task_id = %s AND user_id = %s
            """
            res = self.db_connector.execute_query(q, (status_id, task_id, self.user_id))
            return bool(res)
        except Exception as e:
            print(f"Error updating task status: {e}")
            return False

    def update_task_details(
        self,
        task_id: int,
        task_name: str = None,
        description: str = None,
        category_id: int = None,
        project_id: int = None,
        due_date: str = None,
    ) -> bool:
        """Update task details. Only provided fields are updated."""
        try:
            if not task_id:
                return False
            fields = []
            params = []
            if task_name is not None:
                fields.append("task_name = %s")
                params.append(task_name)
            if description is not None:
                fields.append("description = %s")
                params.append(description)
            if category_id is not None:
                fields.append("category_id = %s")
                params.append(category_id)
            if project_id is not None:
                fields.append("project_id = %s")
                params.append(project_id)
            if due_date is not None:
                fields.append("due_date = %s")
                params.append(due_date)

            if not fields:
                return True

            q = f"UPDATE tasks SET {', '.join(fields)} WHERE task_id = %s AND user_id = %s"
            params.extend([task_id, self.user_id])
            res = self.db_connector.execute_query(q, tuple(params))
            return bool(res)
        except Exception as e:
            print(f"Error updating task details: {e}")
            return False

    def get_pending_tasks_list(self):
        """Get list of pending tasks for scheduling."""
        try:
            query = """
                SELECT t.task_id, t.task_name, t.description, t.due_date, ts.status_name as status,
                       tc.category_id, p.project_id
                FROM tasks t
                LEFT JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN projects p ON t.project_id = p.project_id
                WHERE t.user_id = %s AND ts.status_name = 'pending'
                ORDER BY t.due_date ASC
            """
            return self.db_connector.execute_query(query, (self.user_id,)) or []
        except Exception as e:
            print(f"Error getting pending tasks list: {e}")
            return []

    def get_task_status_counts(self):
        """Get count of tasks by status for the current user."""
        try:
            query = """
                SELECT ts.status_name as status, COUNT(*) as count
                FROM tasks t
                JOIN task_status ts ON t.status_id = ts.status_id
                WHERE t.user_id = %s
                GROUP BY ts.status_name
                ORDER BY count DESC
            """
            return self.db_connector.execute_query(query, (self.user_id,)) or []
        except Exception as e:
            print(f"Error getting task status counts: {e}")
            return []

    def get_tasks_by_status(self, status_name: str):
        """Get tasks filtered by a given status name (pending, in-progress, completed, cancelled)."""
        try:
            query = """
                SELECT t.task_id, t.task_name, t.description, t.due_date,
                       ts.status_name, tc.category_name, p.project_name
                FROM tasks t
                JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN projects p ON t.project_id = p.project_id
                WHERE t.user_id = %s AND ts.status_name = %s
                ORDER BY COALESCE(t.due_date, t.created_at) ASC
            """
            return self.db_connector.execute_query(query, (self.user_id, status_name)) or []
        except Exception as e:
            print(f"Error getting tasks by status: {e}")
            return []

    def create_task(self, task_name=None, description=None, category_id=None, project_id=None, priority=None, due_date=None):
        """Create a new task with smart suggestions."""
        if task_name is None:  # CLI mode
            print("\n=== Create New Task ===")
            task_name = input("Task name: ").strip()
            if not task_name:
                print("❌ Task name is required!")
                return
            
            description = input("Description (optional): ").strip() or None
            
            # Get categories
            categories = self.get_categories()
            if categories:
                print("\nAvailable categories:")
                for cat in categories:
                    print(f"  {cat['category_id']}. {cat['category_name']}")
                category_id = input("Category ID (optional): ").strip() or None
            else:
                category_id = None
            
            # Get projects
            projects = self.get_projects()
            if projects:
                print("\nAvailable projects:")
                for proj in projects:
                    print(f"  {proj['project_id']}. {proj['project_name']}")
                project_id = input("Project ID (optional): ").strip() or None
            else:
                project_id = None
            
            # Get due date
            due_date = input("Due date (YYYY-MM-DD) [optional]: ").strip() or None
            
            # Get status (default to pending)
            statuses = self.get_statuses()
            if statuses:
                print("\nAvailable statuses:")
                for status in statuses:
                    print(f"  {status['status_id']}. {status['status_name']}")
                status_id = input(f"Status ID (default: 1 for pending): ").strip() or 1
            else:
                status_id = 1
        
        else:  # Streamlit mode
            if not task_name:
                return None
            
            # Default status to pending (status_id = 1)
            status_id = 1
        
        try:
            # Insert the task
            query = """
                INSERT INTO tasks (user_id, project_id, task_name, description, status_id, category_id, due_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            result = self.db_connector.execute_query(
                query, 
                (self.user_id, project_id, task_name, description, status_id, category_id, due_date)
            )
            
            if result:
                # Get the inserted task ID
                task_id = self.db_connector.execute_query("SELECT LAST_INSERT_ID()")[0]['LAST_INSERT_ID()']
                
                if task_name is None:  # CLI mode
                    print("✅ Task created successfully!")
                    
                    # Get smart scheduling suggestion
                    if self.analytics:
                        suggestion = self.analytics.get_smart_scheduling_suggestion(self.user_id, task_name, category_id)
                        if suggestion['estimated_duration'] > 0:
                            print(f"\n💡 Smart Suggestion:")
                            print(f"   Estimated duration: {suggestion['estimated_duration']} minutes")
                            print(f"   Confidence level: {suggestion['confidence_level']}")
                            if suggestion['recommended_breaks']:
                                print(f"   Recommended breaks: {len(suggestion['recommended_breaks'])} break(s)")
                
                return task_id
            else:
                if task_name is None:  # CLI mode
                    print("❌ Failed to create task")
                return None
                
        except Exception as e:
            if task_name is None:  # CLI mode
                print(f"❌ Error creating task: {e}")
            return None

    def task_menu(self):
        """Main task management menu."""
        while True:
            print("\n" + "="*50)
            print("🎯 TASK MANAGER")
            print("="*50)
            print("1. 📋 View Tasks")
            print("2. ➕ Create Task")
            print("3. ✏️  Update Task")
            print("4. 🗑️  Delete Task")
            print("5. 📊 Task Analytics")
            print("6. 🚪 Exit")
            print("-"*50)
            
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                self.view_tasks()
            elif choice == '2':
                self.create_task()
            elif choice == '3':
                self.update_task()
            elif choice == '4':
                self.delete_task()
            elif choice == '5':
                self.get_task_analytics()
            elif choice == '6':
                print("👋 Exiting Task Manager. Goodbye!")
                break
            else:
                print("❌ Invalid option. Please choose 1-6.")
            
            input("\nPress Enter to continue...")

def main():
    """Main function to run the task manager."""
    print("🔧 Task Manager is running...")
    
    # Initialize task manager with user ID 1 (John Doe)
    task_manager = TaskManager(user_id=1)
    
    if task_manager.db_connector.connection:
        task_manager.task_menu()
    else:
        print("❌ Failed to initialize Task Manager. Please check your database connection.")

if __name__ == "__main__":
    main()

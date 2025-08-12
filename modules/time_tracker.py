"""
Time Tracking Module - Team Member 4
Handles start/stop timer functionality with integration to tasks and analytics.
Updated to work with the comprehensive database schema and integrate with other modules.
"""

import sys
import os
from datetime import datetime, timedelta
import time
import threading

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connector import DatabaseConnector
from modules.analytics import Analytics
from modules.task_manager import TaskManager

class TimeTracker:
    def __init__(self, user_id=1):
        """
        Initialize TimeTracker with database connection and analytics.
        
        Args:
            user_id: ID of the logged-in user
        """
        self.user_id = user_id
        self.db_connector = DatabaseConnector()
        self.analytics = None
        self.task_manager = None
        self.active_timer = None
        self.timer_thread = None
        self.stop_timer_flag = False
        
        # Connect to database
        if self.db_connector.connect():
            self.analytics = Analytics(self.db_connector.get_connection())
            self.task_manager = TaskManager(user_id)
            print("✅ Time Tracker initialized successfully")
        else:
            print("❌ Failed to connect to database")
            return

    def get_user_tasks(self):
        """Get all tasks for the current user that can be tracked."""
        try:
            query = """
                SELECT t.task_id, t.task_name, ts.status_name, tc.category_name, p.project_name
                FROM tasks t
                LEFT JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN projects p ON t.project_id = p.project_id
                WHERE t.user_id = %s AND ts.status_name != 'completed'
                ORDER BY t.task_name
            """
            tasks = self.db_connector.execute_query(query, (self.user_id,))
            return tasks if tasks else []
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []

    def check_active_timer(self):
        """Check if there's an active timer for the current user."""
        try:
            query = """
                SELECT tl.log_id, tl.task_id, tl.start_time, t.task_name, ts.status_name
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                JOIN task_status ts ON t.status_id = ts.status_id
                WHERE t.user_id = %s AND tl.end_time IS NULL
                ORDER BY tl.start_time DESC
                LIMIT 1
            """
            active_timer = self.db_connector.execute_query(query, (self.user_id,))
            return active_timer[0] if active_timer else None
        except Exception as e:
            print(f"Error checking active timer: {e}")
            return None

    def start_timer(self, task_id=None):
        """Start a timer for a given task."""
        try:
            # Check if there's already an active timer
            active_timer = self.check_active_timer()
            if active_timer:
                print(f"⏳ Timer is already running for task: {active_timer['task_name']}")
                print(f"   Started at: {active_timer['start_time']}")
                return False

            # If no task_id provided, show available tasks
            if not task_id:
                tasks = self.get_user_tasks()
                if not tasks:
                    print("📝 No tasks available for time tracking.")
                    return False

                print("\n📋 Available Tasks:")
                for task in tasks:
                    status_emoji = {
                        'pending': '⏳',
                        'in-progress': '🔄',
                        'completed': '✅',
                        'cancelled': '❌'
                    }.get(task['status_name'], '📝')
                    
                    print(f"{status_emoji} [{task['task_id']}] {task['task_name']}")
                    if task['category_name']:
                        print(f"    Category: {task['category_name']}")
                    if task['project_name']:
                        print(f"    Project: {task['project_name']}")

                task_id = input("\nEnter task ID to start timer: ").strip()
                if not task_id:
                    print("❌ No task ID provided.")
                    return False

            # Validate task belongs to user
            task_query = """
                SELECT t.task_id, t.task_name, ts.status_name
                FROM tasks t
                JOIN task_status ts ON t.status_id = ts.status_id
                WHERE t.task_id = %s AND t.user_id = %s
            """
            task = self.db_connector.execute_query(task_query, (task_id, self.user_id))
            
            if not task:
                print("❌ Task not found or doesn't belong to you!")
                return False

            task = task[0]
            if task['status_name'] == 'completed':
                print("❌ Cannot start timer for completed task!")
                return False

            # Start the timer
            start_time = datetime.now()
            insert_query = """
                INSERT INTO time_logs (task_id, start_time)
                VALUES (%s, %s)
            """
            result = self.db_connector.execute_query(insert_query, (task_id, start_time))
            
            if result:
                print(f"✅ Timer started for task: {task['task_name']}")
                print(f"   Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Update task status to in-progress if it's pending
                if task['status_name'] == 'pending':
                    status_query = "SELECT status_id FROM task_status WHERE status_name = 'in-progress'"
                    status_result = self.db_connector.execute_query(status_query)
                    if status_result:
                        update_query = "UPDATE tasks SET status_id = %s WHERE task_id = %s"
                        self.db_connector.execute_query(update_query, (status_result[0]['status_id'], task_id))
                        print(f"   📝 Task status updated to 'in-progress'")

                # Start timer display thread
                self.active_timer = {
                    'task_id': task_id,
                    'task_name': task['task_name'],
                    'start_time': start_time,
                    'log_id': result
                }
                self.start_timer_display()
                
                return True
            else:
                print("❌ Failed to start timer")
                return False

        except Exception as e:
            print(f"❌ Error starting timer: {e}")
            return False

    def stop_timer(self, task_id=None):
        """Stop the active timer for a given task."""
        try:
            # Check for active timer
            active_timer = self.check_active_timer()
            if not active_timer:
                print("⚠️ No active timer found.")
                return False

            # If task_id provided, validate it matches active timer
            if task_id and str(active_timer['task_id']) != str(task_id):
                print(f"❌ Active timer is for task {active_timer['task_id']}, not {task_id}")
                return False

            # Stop the timer
            end_time = datetime.now()
            start_time = active_timer['start_time']
            duration_minutes = int((end_time - start_time).total_seconds() // 60)

            update_query = """
                UPDATE time_logs
                SET end_time = %s, duration_minutes = %s
                WHERE log_id = %s
            """
            result = self.db_connector.execute_query(update_query, (end_time, duration_minutes, active_timer['log_id']))
            
            if result:
                print(f"✅ Timer stopped for task: {active_timer['task_name']}")
                print(f"   Stopped at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   🕒 Duration: {duration_minutes} minutes ({duration_minutes//60}h {duration_minutes%60}m)")

                # Stop timer display
                self.stop_timer_display()

                # Get break suggestion
                if self.analytics and duration_minutes > 30:
                    break_suggestion = self.analytics.suggest_break(self.user_id)
                    if break_suggestion['should_take_break']:
                        print(f"\n💡 Break Suggestion:")
                        print(f"   {break_suggestion['reason']}")
                        if break_suggestion['recommended_duration']:
                            print(f"   Recommended break duration: {break_suggestion['recommended_duration']} minutes")

                return True
            else:
                print("❌ Failed to stop timer")
                return False

        except Exception as e:
            print(f"❌ Error stopping timer: {e}")
            return False

    def start_timer_display(self):
        """Start a thread to display timer progress."""
        if self.active_timer and not self.timer_thread:
            self.stop_timer_flag = False
            self.timer_thread = threading.Thread(target=self._timer_display_loop)
            self.timer_thread.daemon = True
            self.timer_thread.start()

    def stop_timer_display(self):
        """Stop the timer display thread."""
        self.stop_timer_flag = True
        if self.timer_thread:
            self.timer_thread.join(timeout=1)
            self.timer_thread = None
        self.active_timer = None

    def _timer_display_loop(self):
        """Display timer progress in a separate thread."""
        while not self.stop_timer_flag and self.active_timer:
            try:
                elapsed = datetime.now() - self.active_timer['start_time']
                hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                
                print(f"\r⏱️  Timer running: {hours:02d}:{minutes:02d}:{seconds:02d} - {self.active_timer['task_name']}", end='', flush=True)
                time.sleep(1)
            except:
                break
        print()  # New line after timer stops

    def view_timer_history(self):
        """View timer history for the current user."""
        try:
            query = """
                SELECT t.task_name, tl.start_time, tl.end_time, tl.duration_minutes,
                       ts.status_name, tc.category_name, p.project_name
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN projects p ON t.project_id = p.project_id
                WHERE t.user_id = %s AND tl.end_time IS NOT NULL
                ORDER BY tl.start_time DESC
                LIMIT 10
            """
            history = self.db_connector.execute_query(query, (self.user_id,))
            
            if not history:
                print("📝 No timer history found.")
                return

            print(f"\n📊 Recent Timer History ({len(history)} entries):")
            print("-" * 80)
            
            for entry in history:
                start_time = entry['start_time'].strftime('%Y-%m-%d %H:%M')
                end_time = entry['end_time'].strftime('%H:%M') if entry['end_time'] else 'Running'
                duration = f"{entry['duration_minutes']}m" if entry['duration_minutes'] else 'N/A'
                
                print(f"🕒 {start_time} - {end_time} ({duration})")
                print(f"   📝 {entry['task_name']}")
                if entry['category_name']:
                    print(f"   🏷️  {entry['category_name']}")
                if entry['project_name']:
                    print(f"   📁 {entry['project_name']}")
                print()

        except Exception as e:
            print(f"❌ Error viewing timer history: {e}")

    def get_timer_analytics(self):
        """Get analytics for the current user's time tracking."""
        if not self.analytics:
            print("❌ Analytics module not available")
            return

        print("\n=== Time Tracking Analytics ===")
        
        try:
            # Get productivity insights
            insights = self.analytics.get_productivity_insights(self.user_id)
            print(f"📊 Productivity Insights:")
            print(f"   Most productive time: {insights['most_productive_time'] or 'Not enough data'}")
            print(f"   Average session length: {insights['average_session_length']} minutes")
            print(f"   Completion rate: {insights['completion_rate']}%")

            # Get recent time report
            time_report = self.analytics.generate_time_report(self.user_id, "weekly")
            if time_report['total_time'] > 0:
                print(f"\n📈 This Week's Summary:")
                print(f"   Total time tracked: {time_report['total_time']} minutes")
                print(f"   Tasks completed: {time_report['tasks_completed']}")
                print(f"   Average duration: {time_report['average_duration']} minutes")

        except Exception as e:
            print(f"❌ Error getting analytics: {e}")

    def get_total_time_today(self):
        """Get total time tracked today for the current user."""
        try:
            query = """
                SELECT COALESCE(SUM(tl.duration_minutes), 0) as total_time
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                WHERE t.user_id = %s AND DATE(tl.start_time) = CURDATE()
            """
            result = self.db_connector.execute_query(query, (self.user_id,))
            return result[0]['total_time'] if result else 0
        except Exception as e:
            print(f"Error getting total time today: {e}")
            return 0

    def get_recent_time_logs(self, days=7):
        """Get recent time logs for the specified number of days."""
        try:
            query = """
                SELECT tl.start_time, tl.duration_minutes AS duration, t.task_name
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                WHERE t.user_id = %s AND tl.start_time >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                ORDER BY tl.start_time DESC
            """
            return self.db_connector.execute_query(query, (self.user_id, days)) or []
        except Exception as e:
            print(f"Error getting recent time logs: {e}")
            return []

    def get_todays_time_logs(self):
        """Get today's time logs for the current user."""
        try:
            query = """
                SELECT tl.start_time, tl.duration_minutes AS duration, t.task_name
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                WHERE t.user_id = %s AND DATE(tl.start_time) = CURDATE()
                ORDER BY tl.start_time DESC
            """
            return self.db_connector.execute_query(query, (self.user_id,)) or []
        except Exception as e:
            print(f"Error getting today's time logs: {e}")
            return []

    def time_tracker_menu(self):
        """Main time tracking menu."""
        while True:
            print("\n" + "="*50)
            print("⏱️  TIME TRACKER")
            print("="*50)
            
            # Show active timer if any
            active_timer = self.check_active_timer()
            if active_timer:
                elapsed = datetime.now() - active_timer['start_time']
                hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"🔄 ACTIVE TIMER: {hours:02d}:{minutes:02d}:{seconds:02d} - {active_timer['task_name']}")
                print("-" * 50)
            
            print("1. 🚀 Start Timer")
            print("2. ⏹️  Stop Timer")
            print("3. 📋 View Available Tasks")
            print("4. 📊 View Timer History")
            print("5. 📈 Timer Analytics")
            print("6. 🚪 Exit")
            print("-"*50)
            
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                self.start_timer()
            elif choice == '2':
                if active_timer:
                    self.stop_timer()
                else:
                    print("⚠️ No active timer to stop.")
            elif choice == '3':
                tasks = self.get_user_tasks()
                if tasks:
                    print(f"\n📋 Available Tasks ({len(tasks)} total):")
                    for task in tasks:
                        status_emoji = {
                            'pending': '⏳',
                            'in-progress': '🔄',
                            'completed': '✅',
                            'cancelled': '❌'
                        }.get(task['status_name'], '📝')
                        
                        print(f"{status_emoji} [{task['task_id']}] {task['task_name']}")
                        if task['category_name']:
                            print(f"    Category: {task['category_name']}")
                        if task['project_name']:
                            print(f"    Project: {task['project_name']}")
                else:
                    print("📝 No tasks available for time tracking.")
            elif choice == '4':
                self.view_timer_history()
            elif choice == '5':
                self.get_timer_analytics()
            elif choice == '6':
                if active_timer:
                    confirm = input("⚠️ Active timer is running. Stop it before exiting? (y/n): ").strip().lower()
                    if confirm == 'y':
                        self.stop_timer()
                print("👋 Exiting Time Tracker. Goodbye!")
                break
            else:
                print("❌ Invalid option. Please choose 1-6.")
            
            input("\nPress Enter to continue...")

def main():
    """Main function to run the time tracker."""
    print("⏱️ Time Tracker is running...")
    
    # Initialize time tracker with user ID 1 (John Doe)
    time_tracker = TimeTracker(user_id=1)
    
    if time_tracker.db_connector.connection:
        time_tracker.time_tracker_menu()
    else:
        print("❌ Failed to initialize Time Tracker. Please check your database connection.")

if __name__ == "__main__":
    main()

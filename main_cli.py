"""
Main CLI Interface - Team Member 2
The main application interface that integrates all modules.
Handles user authentication, routing, and the main menu system.
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.auth import Auth
from modules.task_manager import TaskManager
from modules.time_tracker import TimeTracker
from modules.analytics import Analytics
from modules.intelligent_scheduler import IntelligentScheduler

class SmartTimeTrackerCLI:
    def __init__(self):
        """
        Initialize the main CLI application.
        """
        self.auth = Auth()
        self.task_manager = None
        self.time_tracker = None
        self.analytics = None
        self.scheduler = None
        
        print("🚀 Smart Time-Tracking and Task Scheduler")
        print("=" * 50)

    def initialize_modules(self):
        """Initialize modules for the current user."""
        if not self.auth.is_logged_in():
            return False
        
        user_id = self.auth.get_current_user()['user_id']
        
        try:
            # Initialize modules with current user
            self.task_manager = TaskManager(user_id)
            self.time_tracker = TimeTracker(user_id)
            self.analytics = Analytics(self.auth.db_connector.get_connection())
            self.scheduler = IntelligentScheduler(user_id)
            
            return True
        except Exception as e:
            print(f"❌ Error initializing modules: {e}")
            return False

    def show_welcome_screen(self):
        """Show the welcome screen and handle authentication."""
        print("\n🎯 Welcome to Smart Time-Tracking and Task Scheduler!")
        print("A time-tracking application that doesn't just log time, but intelligently uses it.")
        print("\nBased on your past performance and task complexity, it can:")
        print("• Automatically create realistic schedules for new projects")
        print("• Send reminders and notifications")
        print("• Suggest 'micro-breaks' to prevent burnout")
        print("• Provide data-driven insights and analytics")
        
        while True:
            print("\n" + "="*50)
            print("🔐 AUTHENTICATION")
            print("="*50)
            print("1. 📝 Sign Up (New User)")
            print("2. 🔑 Log In (Existing User)")
            print("3. 🚪 Exit")
            print("-"*50)
            
            choice = input("Choose an option (1-3): ").strip()
            
            if choice == '1':
                if self.auth.sign_up():
                    print("\n✅ Registration successful! Please log in to continue.")
                else:
                    print("\n❌ Registration failed. Please try again.")
            elif choice == '2':
                if self.auth.log_in():
                    print("\n✅ Login successful!")
                    if self.initialize_modules():
                        return True
                    else:
                        print("❌ Failed to initialize modules. Please try again.")
                        self.auth.log_out()
                else:
                    print("\n❌ Login failed. Please check your credentials.")
            elif choice == '3':
                print("👋 Thank you for using Smart Time-Tracking and Task Scheduler!")
                return False
            else:
                print("❌ Invalid option. Please choose 1-3.")
            
            input("\nPress Enter to continue...")

    def show_main_menu(self):
        """Show the main application menu."""
        while True:
            user = self.auth.get_current_user()
            print("\n" + "="*60)
            print(f"🎯 SMART TIME-TRACKING AND TASK SCHEDULER")
            print("="*60)
            print(f"👤 Welcome, {user['name']}!")
            print(f"📧 Email: {user['email']}")
            print(f"🕒 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-"*60)
            
            # Check for active timer
            if self.time_tracker:
                active_timer = self.time_tracker.check_active_timer()
                if active_timer:
                    elapsed = datetime.now() - active_timer['start_time']
                    hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    print(f"🔄 ACTIVE TIMER: {hours:02d}:{minutes:02d}:{seconds:02d} - {active_timer['task_name']}")
                    print("-"*60)
            
            print("📋 MAIN MENU")
            print("1. 🎯 Task Management")
            print("2. ⏱️  Time Tracking")
            print("3. 📊 Analytics & Reports")
            print("4. 🤖 Smart Scheduling")
            print("5. 👤 User Profile")
            print("6. 🚪 Log Out")
            print("7. 🚪 Exit Application")
            print("-"*60)
            
            choice = input("Choose an option (1-7): ").strip()
            
            if choice == '1':
                self.show_task_management_menu()
            elif choice == '2':
                self.show_time_tracking_menu()
            elif choice == '3':
                self.show_analytics_menu()
            elif choice == '4':
                self.show_smart_scheduling_menu()
            elif choice == '5':
                self.show_user_profile_menu()
            elif choice == '6':
                self.auth.log_out()
                print("👋 You have been logged out successfully!")
                return False
            elif choice == '7':
                if self.time_tracker and self.time_tracker.check_active_timer():
                    confirm = input("⚠️ Active timer is running. Stop it before exiting? (y/n): ").strip().lower()
                    if confirm == 'y':
                        self.time_tracker.stop_timer()
                print("👋 Thank you for using Smart Time-Tracking and Task Scheduler!")
                return False
            else:
                print("❌ Invalid option. Please choose 1-7.")
            
            input("\nPress Enter to continue...")

    def show_task_management_menu(self):
        """Show the task management menu."""
        if not self.task_manager:
            print("❌ Task manager not initialized!")
            return
        
        while True:
            print("\n" + "="*50)
            print("🎯 TASK MANAGEMENT")
            print("="*50)
            print("1. 📋 View Tasks")
            print("2. ➕ Create Task")
            print("3. ✏️  Update Task")
            print("4. 🗑️  Delete Task")
            print("5. 📊 Task Analytics")
            print("6. 🔙 Back to Main Menu")
            print("-"*50)
            
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                self.task_manager.view_tasks()
            elif choice == '2':
                self.task_manager.create_task()
            elif choice == '3':
                self.task_manager.update_task()
            elif choice == '4':
                self.task_manager.delete_task()
            elif choice == '5':
                self.task_manager.get_task_analytics()
            elif choice == '6':
                break
            else:
                print("❌ Invalid option. Please choose 1-6.")
            
            input("\nPress Enter to continue...")

    def show_time_tracking_menu(self):
        """Show the time tracking menu."""
        if not self.time_tracker:
            print("❌ Time tracker not initialized!")
            return
        
        while True:
            print("\n" + "="*50)
            print("⏱️  TIME TRACKING")
            print("="*50)
            
            # Show active timer if any
            active_timer = self.time_tracker.check_active_timer()
            if active_timer:
                elapsed = datetime.now() - active_timer['start_time']
                hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"🔄 ACTIVE TIMER: {hours:02d}:{minutes:02d}:{seconds:02d} - {active_timer['task_name']}")
                print("-"*50)
            
            print("1. 🚀 Start Timer")
            print("2. ⏹️  Stop Timer")
            print("3. 📋 View Available Tasks")
            print("4. 📊 View Timer History")
            print("5. 📈 Timer Analytics")
            print("6. 🔙 Back to Main Menu")
            print("-"*50)
            
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                self.time_tracker.start_timer()
            elif choice == '2':
                if active_timer:
                    self.time_tracker.stop_timer()
                else:
                    print("⚠️ No active timer to stop.")
            elif choice == '3':
                tasks = self.time_tracker.get_user_tasks()
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
                self.time_tracker.view_timer_history()
            elif choice == '5':
                self.time_tracker.get_timer_analytics()
            elif choice == '6':
                break
            else:
                print("❌ Invalid option. Please choose 1-6.")
            
            input("\nPress Enter to continue...")

    def show_analytics_menu(self):
        """Show the analytics menu."""
        if not self.analytics:
            print("❌ Analytics not initialized!")
            return
        
        while True:
            print("\n" + "="*50)
            print("📊 ANALYTICS & REPORTS")
            print("="*50)
            print("1. 📈 Time Reports")
            print("2. 💡 Smart Suggestions")
            print("3. 🧠 Productivity Insights")
            print("4. 🏷️  Category Analytics")
            print("5. ⏰ Break Suggestions")
            print("6. 🔙 Back to Main Menu")
            print("-"*50)
            
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                self.show_time_reports_menu()
            elif choice == '2':
                self.show_smart_suggestions()
            elif choice == '3':
                self.show_productivity_insights()
            elif choice == '4':
                self.show_category_analytics()
            elif choice == '5':
                self.show_break_suggestions()
            elif choice == '6':
                break
            else:
                print("❌ Invalid option. Please choose 1-6.")
            
            input("\nPress Enter to continue...")

    def show_time_reports_menu(self):
        """Show the time reports menu."""
        if not self.analytics:
            print("❌ Analytics not initialized!")
            return
        
        while True:
            print("\n" + "="*50)
            print("📈 TIME REPORTS")
            print("="*50)
            print("1. 📅 Daily Report")
            print("2. 📊 Weekly Report")
            print("3. 📈 Monthly Report")
            print("4. 📊 All Time Report")
            print("5. 🔙 Back to Analytics")
            print("-"*50)
            
            choice = input("Choose an option (1-5): ").strip()
            
            user_id = self.auth.get_current_user()['user_id']
            
            if choice == '1':
                self.analytics.display_time_report(user_id, "daily")
            elif choice == '2':
                self.analytics.display_time_report(user_id, "weekly")
            elif choice == '3':
                self.analytics.display_time_report(user_id, "monthly")
            elif choice == '4':
                self.analytics.display_time_report(user_id, "all")
            elif choice == '5':
                break
            else:
                print("❌ Invalid option. Please choose 1-5.")
            
            input("\nPress Enter to continue...")

    def show_smart_suggestions(self):
        """Show smart scheduling suggestions."""
        if not self.analytics:
            print("❌ Analytics not initialized!")
            return
        
        print("\n=== Smart Scheduling Suggestions ===")
        user_id = self.auth.get_current_user()['user_id']
        
        task_name = input("Enter task name for suggestions: ").strip()
        if not task_name:
            print("❌ Task name is required!")
            return
        
        category_id = input("Enter category ID (optional): ").strip() or None
        
        suggestion = self.analytics.get_smart_scheduling_suggestion(user_id, task_name, category_id)
        
        print(f"\n💡 Smart Suggestion for '{task_name}':")
        print(f"   Estimated duration: {suggestion['estimated_duration']} minutes")
        print(f"   Confidence level: {suggestion['confidence_level']}")
        if suggestion['recommended_breaks']:
            print(f"   Recommended breaks: {len(suggestion['recommended_breaks'])} break(s)")

    def show_productivity_insights(self):
        """Show productivity insights."""
        if not self.analytics:
            print("❌ Analytics not initialized!")
            return
        
        print("\n=== Productivity Insights ===")
        user_id = self.auth.get_current_user()['user_id']
        
        insights = self.analytics.get_productivity_insights(user_id)
        
        print(f"📊 Productivity Insights:")
        print(f"   Most productive time: {insights['most_productive_time'] or 'Not enough data'}")
        print(f"   Average session length: {insights['average_session_length']} minutes")
        print(f"   Completion rate: {insights['completion_rate']}%")
        
        if insights.get('top_categories'):
            print(f"\n🏷️  Top Categories:")
            for category in insights['top_categories']:
                print(f"   {category['category_name']}: {category['task_count']} tasks")

    def show_category_analytics(self):
        """Show category analytics."""
        if not self.analytics:
            print("❌ Analytics not initialized!")
            return
        
        print("\n=== Category Analytics ===")
        user_id = self.auth.get_current_user()['user_id']
        
        category_analytics = self.analytics.get_category_analytics(user_id)
        
        if category_analytics['categories']:
            print(f"📈 Category Breakdown:")
            for category in category_analytics['categories']:
                print(f"   {category['category_name']}: {category['total_tasks']} tasks, {category['total_time'] or 0} min")
        else:
            print("📝 No category data available.")

    def show_break_suggestions(self):
        """Show break suggestions."""
        if not self.analytics:
            print("❌ Analytics not initialized!")
            return
        
        print("\n=== Break Suggestions ===")
        user_id = self.auth.get_current_user()['user_id']
        
        break_suggestion = self.analytics.suggest_break(user_id)
        
        if break_suggestion['should_take_break']:
            print(f"💡 Break Recommendation:")
            print(f"   {break_suggestion['reason']}")
            if break_suggestion['recommended_duration']:
                print(f"   Recommended break duration: {break_suggestion['recommended_duration']} minutes")
        else:
            print("✅ No break needed at this time.")

    def show_smart_scheduling_menu(self):
        """Show the smart scheduling menu."""
        if not self.scheduler:
            print("❌ Smart scheduler not initialized!")
            return
        
        while True:
            print("\n" + "="*50)
            print("🤖 SMART SCHEDULING")
            print("="*50)
            print("1. 📅 Create Smart Schedule")
            print("2. 🔔 Start Reminder System")
            print("3. 🔕 Stop Reminder System")
            print("4. 📊 Schedule Recommendations")
            print("5. ⏰ Predict Task Duration")
            print("6. 🔙 Back to Main Menu")
            print("-"*50)
            
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                self.create_smart_schedule()
            elif choice == '2':
                self.scheduler.start_reminder_system()
            elif choice == '3':
                self.scheduler.stop_reminder_system()
            elif choice == '4':
                self.show_schedule_recommendations()
            elif choice == '5':
                self.predict_task_duration()
            elif choice == '6':
                break
            else:
                print("❌ Invalid option. Please choose 1-6.")
            
            input("\nPress Enter to continue...")

    def create_smart_schedule(self):
        """Create a smart schedule for multiple tasks."""
        print("\n=== Create Smart Schedule ===")
        
        tasks = []
        while True:
            print(f"\nTask {len(tasks) + 1}:")
            task_name = input("Task name (or 'done' to finish): ").strip()
            
            if task_name.lower() == 'done':
                break
            
            if not task_name:
                print("❌ Task name is required!")
                continue
            
            description = input("Description (optional): ").strip() or None
            
            # Get categories
            categories = self.task_manager.get_categories()
            category_id = None
            if categories:
                print("\nAvailable categories:")
                for cat in categories:
                    print(f"  {cat['category_id']}. {cat['category_name']}")
                cat_input = input("Category ID (optional): ").strip()
                category_id = int(cat_input) if cat_input.isdigit() else None
            
            tasks.append({
                'name': task_name,
                'description': description,
                'category_id': category_id
            })
        
        if not tasks:
            print("❌ No tasks to schedule!")
            return
        
        print(f"\n🤖 Creating smart schedule for {len(tasks)} tasks...")
        scheduled_tasks = self.scheduler.create_smart_schedule(tasks)
        
        if scheduled_tasks:
            print("\n📅 Smart Schedule Created:")
            print("-" * 60)
            for i, task in enumerate(scheduled_tasks, 1):
                print(f"{i}. {task['task_name']}")
                print(f"   📅 Start: {task['start_time'].strftime('%Y-%m-%d %H:%M')}")
                print(f"   ⏱️  Duration: {task['duration']} minutes")
                print(f"   🎯 Category: {task['category']}")
                print(f"   📊 Confidence: {task['confidence']}%")
                print()
        else:
            print("❌ Failed to create schedule!")

    def show_schedule_recommendations(self):
        """Show personalized schedule recommendations."""
        print("\n=== Schedule Recommendations ===")
        
        recommendations = self.scheduler.get_schedule_recommendations()
        
        if recommendations:
            print(f"⏰ Optimal Work Hours: {', '.join(map(str, recommendations['optimal_work_hours']))}")
            print(f"📊 Recommended Session Length: {recommendations['recommended_session_length']} minutes")
            print(f"☕ Break Frequency: {recommendations['break_frequency']}")
            print(f"📅 Best Days: {', '.join(recommendations['best_days'])}")
            
            if recommendations['focus_tips']:
                print(f"\n💡 Focus Tips:")
                for tip in recommendations['focus_tips']:
                    print(f"   • {tip}")
        else:
            print("❌ No recommendations available!")

    def predict_task_duration(self):
        """Predict duration for a specific task."""
        print("\n=== Task Duration Prediction ===")
        
        task_name = input("Task name: ").strip()
        if not task_name:
            print("❌ Task name is required!")
            return
        
        description = input("Description (optional): ").strip() or None
        
        # Get categories
        categories = self.task_manager.get_categories()
        category_id = None
        if categories:
            print("\nAvailable categories:")
            for cat in categories:
                print(f"  {cat['category_id']}. {cat['category_name']}")
            cat_input = input("Category ID (optional): ").strip()
            category_id = int(cat_input) if cat_input.isdigit() else None
        
        prediction = self.scheduler.predict_task_duration(
            task_name, description, category_id
        )
        
        print(f"\n🤖 Duration Prediction:")
        print(f"   Task: {task_name}")
        print(f"   Estimated Duration: {prediction['predicted_duration']} minutes")
        print(f"   Confidence: {prediction['confidence']}%")
        print(f"   Method: {prediction['method']}")
        
        if prediction.get('features_used'):
            print(f"   Features Used: {', '.join(prediction['features_used'])}")

    def show_user_profile_menu(self):
        """Show the user profile menu."""
        user = self.auth.get_current_user()
        
        while True:
            print("\n" + "="*50)
            print("👤 USER PROFILE")
            print("="*50)
            print(f"Name: {user['name']}")
            print(f"Email: {user['email']}")
            print(f"User ID: {user['user_id']}")
            print("-"*50)
            print("1. 🔙 Back to Main Menu")
            print("-"*50)
            
            choice = input("Choose an option (1): ").strip()
            
            if choice == '1':
                break
            else:
                print("❌ Invalid option. Please choose 1.")

    def run(self):
        """Run the main application."""
        try:
            # Show welcome screen and handle authentication
            if not self.show_welcome_screen():
                return
            
            # Show main menu
            self.show_main_menu()
            
        except KeyboardInterrupt:
            print("\n\n👋 Application interrupted. Goodbye!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            print("\n👋 Thank you for using Smart Time-Tracking and Task Scheduler!")

def main():
    """Main function to run the application."""
    print("🚀 Starting Smart Time-Tracking and Task Scheduler...")
    
    app = SmartTimeTrackerCLI()
    app.run()

if __name__ == "__main__":
    main()

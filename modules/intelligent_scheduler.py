"""
Intelligent Scheduler Module
Handles smart scheduling, reminders, and automated task planning.
"""

import sys
import os
from datetime import datetime, timedelta
import threading
import time
import schedule
from typing import Dict, List, Optional, Tuple

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connector import DatabaseConnector
from modules.analytics import Analytics

class IntelligentScheduler:
    def __init__(self, user_id: int):
        """
        Initialize the Intelligent Scheduler.
        
        Args:
            user_id: ID of the logged-in user
        """
        self.user_id = user_id
        self.db_connector = DatabaseConnector()
        self.analytics = None
        self.reminder_thread = None
        self.is_running = False
        
        # Connect to database
        if self.db_connector.connect():
            self.analytics = Analytics(self.db_connector.get_connection())
            print("✅ Intelligent Scheduler initialized successfully")
        else:
            print("❌ Failed to connect to database")

    def predict_task_duration(self, task_name: str, description: str = None, 
                            category_id: int = None, project_id: int = None) -> Dict:
        """
        Estimate task duration based on category and historical data.
        
        Returns:
            Dictionary with estimated duration and method
        """
        try:
            # Get category name
            category_name = "other"
            if category_id:
                cat_query = "SELECT category_name FROM task_categories WHERE category_id = %s"
                cat_result = self.db_connector.execute_query(cat_query, (category_id,))
                if cat_result:
                    category_name = cat_result[0]['category_name']
            
            # Get average duration for this category
            query = """
                SELECT AVG(tl.duration_minutes) as avg_duration
                FROM tasks t
                JOIN time_logs tl ON t.task_id = tl.task_id
                WHERE t.category_id = %s AND t.user_id = %s
                AND tl.duration_minutes IS NOT NULL
            """
            result = self.db_connector.execute_query(query, (category_id, self.user_id))
            
            # Default durations by category (in minutes)
            default_durations = {
                'coding': 120,
                'design': 90,
                'planning': 60,
                'testing': 45,
                'documentation': 60,
                'meeting': 30,
                'other': 60
            }
            
            # Use average if available, otherwise use default
            if result and result[0]['avg_duration']:
                duration = result[0]['avg_duration']
            else:
                duration = default_durations.get(category_name.lower(), 60)
            
            return {
                'duration': round(duration / 60, 1),  # Convert to hours
                'confidence': 70.0,
                'method': 'Historical Average'
            }
            
        except Exception as e:
            print(f"❌ Error in duration estimation: {e}")
            # Fallback to default
            return {
                'duration': 1.0,
                'confidence': 50.0,
                'method': 'Default Estimate'
            }

    def create_smart_schedule(self, tasks: List[Dict]) -> List[Dict]:
        """
        Create an intelligent schedule for multiple tasks.
        
        Args:
            tasks: List of task dictionaries with name, description, category_id, etc.
            
        Returns:
            List of scheduled tasks with start times and durations
        """
        try:
            scheduled_tasks = []
            current_time = datetime.now()
            
            # Get user's productivity insights
            insights = self.analytics.get_productivity_insights(self.user_id)
            productive_hours = insights.get('most_productive_hours', [9, 10, 11, 14, 15, 16])
            
            for i, task in enumerate(tasks):
                # Predict duration
                prediction = self.predict_task_duration(
                    task['name'], 
                    task.get('description'), 
                    task.get('category_id')
                )
                
                duration = prediction['predicted_duration']
                
                # Find optimal start time
                start_time = self._find_optimal_start_time(
                    current_time, duration, productive_hours, scheduled_tasks
                )
                
                # Add breaks between tasks
                if i > 0:
                    break_duration = self._calculate_break_duration(duration)
                    start_time += timedelta(minutes=break_duration)
                
                scheduled_task = {
                    'task_name': task['name'],
                    'start_time': start_time,
                    'duration': duration,
                    'confidence': prediction['confidence'],
                    'category': task.get('category_name', 'Unknown'),
                    'project': task.get('project_name', 'No Project')
                }
                
                scheduled_tasks.append(scheduled_task)
                current_time = start_time + timedelta(minutes=duration)
            
            return scheduled_tasks
            
        except Exception as e:
            print(f"❌ Error creating smart schedule: {e}")
            return []

    def _find_optimal_start_time(self, current_time: datetime, duration: int, 
                                productive_hours: List[int], existing_tasks: List[Dict]) -> datetime:
        """Find the optimal start time for a task."""
        # Start from current time
        start_time = current_time
        
        # If current time is outside productive hours, move to next productive hour
        if start_time.hour not in productive_hours:
            for hour in productive_hours:
                if hour > start_time.hour:
                    start_time = start_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                    break
            else:
                # If no productive hours today, move to tomorrow
                start_time = (start_time + timedelta(days=1)).replace(
                    hour=productive_hours[0], minute=0, second=0, microsecond=0
                )
        
        # Check for conflicts with existing tasks
        for task in existing_tasks:
            task_end = task['start_time'] + timedelta(minutes=task['duration'])
            if start_time < task_end:
                start_time = task_end + timedelta(minutes=15)  # 15 min buffer
        
        return start_time

    def _calculate_break_duration(self, task_duration: int) -> int:
        """Calculate appropriate break duration based on task length."""
        if task_duration <= 30:
            return 5
        elif task_duration <= 60:
            return 10
        elif task_duration <= 120:
            return 15
        else:
            return 20

    def start_reminder_system(self):
        """Start the intelligent reminder system."""
        if self.is_running:
            print("⚠️ Reminder system is already running")
            return
        
        self.is_running = True
        self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()
        print("🔔 Intelligent reminder system started")

    def stop_reminder_system(self):
        """Stop the reminder system."""
        self.is_running = False
        if self.reminder_thread:
            self.reminder_thread.join(timeout=1)
        print("🔕 Reminder system stopped")

    def _reminder_loop(self):
        """Main loop for sending intelligent reminders."""
        while self.is_running:
            try:
                # Check for overdue tasks
                self._check_overdue_tasks()
                
                # Check for upcoming deadlines
                self._check_upcoming_deadlines()
                
                # Suggest breaks
                self._suggest_breaks()
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                print(f"❌ Error in reminder loop: {e}")
                time.sleep(60)

    def _check_overdue_tasks(self):
        """Check and remind about overdue tasks."""
        try:
            query = """
                SELECT t.task_name, t.due_date, DATEDIFF(CURDATE(), t.due_date) as days_overdue
                FROM tasks t
                WHERE t.user_id = %s AND t.due_date < CURDATE() 
                AND t.status_id != (SELECT status_id FROM task_status WHERE status_name = 'completed')
            """
            
            overdue_tasks = self.db_connector.execute_query(query, (self.user_id,))
            
            for task in overdue_tasks:
                days_overdue = task['days_overdue']
                if days_overdue == 1:
                    self._send_notification(
                        f"⚠️ Task overdue: {task['task_name']}",
                        f"This task was due yesterday. Consider updating the deadline or status."
                    )
                elif days_overdue % 3 == 0:  # Remind every 3 days
                    self._send_notification(
                        f"🚨 Task severely overdue: {task['task_name']}",
                        f"This task is {days_overdue} days overdue. Please review and update."
                    )
                    
        except Exception as e:
            print(f"❌ Error checking overdue tasks: {e}")

    def _check_upcoming_deadlines(self):
        """Check and remind about upcoming deadlines."""
        try:
            query = """
                SELECT t.task_name, t.due_date, DATEDIFF(t.due_date, CURDATE()) as days_until_due
                FROM tasks t
                WHERE t.user_id = %s AND t.due_date >= CURDATE()
                AND t.status_id != (SELECT status_id FROM task_status WHERE status_name = 'completed')
                AND DATEDIFF(t.due_date, CURDATE()) <= 3
            """
            
            upcoming_tasks = self.db_connector.execute_query(query, (self.user_id,))
            
            for task in upcoming_tasks:
                days_until_due = task['days_until_due']
                if days_until_due == 0:
                    self._send_notification(
                        f"📅 Due today: {task['task_name']}",
                        f"This task is due today! Make sure to complete it."
                    )
                elif days_until_due == 1:
                    self._send_notification(
                        f"⏰ Due tomorrow: {task['task_name']}",
                        f"This task is due tomorrow. Plan your time accordingly."
                    )
                elif days_until_due == 3:
                    self._send_notification(
                        f"📋 Due in 3 days: {task['task_name']}",
                        f"This task is due in 3 days. Consider starting it soon."
                    )
                    
        except Exception as e:
            print(f"❌ Error checking upcoming deadlines: {e}")

    def _suggest_breaks(self):
        """Suggest breaks based on user activity."""
        try:
            # Check if user has been working for too long
            query = """
                SELECT SUM(tl.duration_minutes) as total_work_time
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                WHERE t.user_id = %s 
                AND tl.start_time >= DATE_SUB(NOW(), INTERVAL 4 HOUR)
                AND tl.end_time IS NOT NULL
            """
            
            result = self.db_connector.execute_query(query, (self.user_id,))
            if result and result[0]['total_work_time']:
                total_work_time = result[0]['total_work_time']
                
                if total_work_time > 240:  # More than 4 hours
                    self._send_notification(
                        "☕ Time for a break!",
                        f"You've been working for {total_work_time//60} hours. Consider taking a 15-30 minute break."
                    )
                elif total_work_time > 120:  # More than 2 hours
                    self._send_notification(
                        "💧 Stay hydrated!",
                        "You've been working for a while. Take a short break and drink some water."
                    )
                    
        except Exception as e:
            print(f"❌ Error suggesting breaks: {e}")

    def _send_notification(self, title: str, message: str):
        """Send a notification to the user."""
        try:
            # For now, print to console. In a real app, this would use system notifications
            print(f"\n🔔 {title}")
            print(f"   {message}")
            print("-" * 50)
        except Exception as e:
            print(f"❌ Error sending notification: {e}")

    def get_schedule_recommendations(self) -> Dict:
        """Get personalized schedule recommendations."""
        try:
            insights = self.analytics.get_productivity_insights(self.user_id)
            
            recommendations = {
                'optimal_work_hours': insights.get('most_productive_hours', [9, 10, 11, 14, 15, 16]),
                'recommended_session_length': insights.get('optimal_session_length', 45),
                'break_frequency': insights.get('break_frequency', 'every_90_minutes'),
                'best_days': insights.get('most_productive_days', ['Monday', 'Tuesday', 'Wednesday']),
                'focus_tips': []
            }
            
            # Add personalized tips
            if insights.get('completion_rate', 0) < 0.7:
                recommendations['focus_tips'].append("Consider breaking down larger tasks into smaller chunks")
            
            if insights.get('average_session_length', 0) > 120:
                recommendations['focus_tips'].append("Try shorter, more focused work sessions")
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error getting schedule recommendations: {e}")
            return {}

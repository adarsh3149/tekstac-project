"""
Analytics Module - Team Member 5
Handles the "smart" part of the project - analytics, reporting, and intelligent suggestions.
Updated to work with the new comprehensive database schema.
"""

import mysql.connector
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics
from tabulate import tabulate


class Analytics:
    def __init__(self, db_connection):
        """
        Initialize Analytics with database connection.
        
        Args:
            db_connection: MySQL database connection object
        """
        self.db_connection = db_connection
        self.cursor = db_connection.cursor(dictionary=True)

    def generate_time_report(self, user_id: int, report_type: str = "all") -> Dict:
        """
        Generate a comprehensive time report for a user.
        
        Args:
            user_id: ID of the user
            report_type: Type of report ("all", "daily", "weekly", "monthly")
            
        Returns:
            Dictionary containing report data
        """
        try:
            report_data = {
                "total_time": 0,
                "tasks_completed": 0,
                "average_duration": 0,
                "task_breakdown": [],
                "period": report_type
            }

            # Base query for time logs with joins to get status and category names
            base_query = """
                SELECT t.task_name, ts.status_name, tc.category_name, p.project_name,
                       tl.duration_minutes, tl.start_time, tl.end_time
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN projects p ON t.project_id = p.project_id
                WHERE t.user_id = %s
            """

            # Add time filter based on report type
            if report_type == "daily":
                base_query += " AND DATE(tl.start_time) = CURDATE()"
            elif report_type == "weekly":
                base_query += " AND tl.start_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
            elif report_type == "monthly":
                base_query += " AND tl.start_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)"

            self.cursor.execute(base_query, (user_id,))
            time_logs = self.cursor.fetchall()

            if not time_logs:
                return report_data

            # Calculate totals
            total_duration = sum(log['duration_minutes'] for log in time_logs if log['duration_minutes'])
            completed_tasks = len([log for log in time_logs if log['status_name'] == 'completed'])

            # Group by task
            task_breakdown = {}
            for log in time_logs:
                task_name = log['task_name']
                duration = log['duration_minutes'] or 0
                
                if task_name not in task_breakdown:
                    task_breakdown[task_name] = {
                        'total_time': 0,
                        'sessions': 0,
                        'status': log['status_name'],
                        'category': log['category_name'] or 'Uncategorized',
                        'project': log['project_name'] or 'No Project'
                    }
                
                task_breakdown[task_name]['total_time'] += duration
                task_breakdown[task_name]['sessions'] += 1

            # Convert to list format for display
            task_breakdown_list = [
                {
                    'task_name': task,
                    'total_time': data['total_time'],
                    'sessions': data['sessions'],
                    'status': data['status'],
                    'category': data['category'],
                    'project': data['project']
                }
                for task, data in task_breakdown.items()
            ]

            report_data.update({
                "total_time": total_duration,
                "tasks_completed": completed_tasks,
                "average_duration": total_duration / len(time_logs) if time_logs else 0,
                "task_breakdown": task_breakdown_list
            })

            return report_data

        except mysql.connector.Error as e:
            print(f"Database error in generate_time_report: {e}")
            return {}

    def calculate_average_time(self, user_id: int, task_type: str = None, category_id: int = None) -> float:
        """
        Calculate average time it takes a user to complete tasks.
        
        Args:
            user_id: ID of the user
            task_type: Optional filter for specific task types (deprecated, use category_id)
            category_id: Optional filter for specific category
            
        Returns:
            Average duration in minutes
        """
        try:
            query = """
                SELECT AVG(tl.duration_minutes) as avg_duration
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                JOIN task_status ts ON t.status_id = ts.status_id
                WHERE t.user_id = %s AND ts.status_name = 'completed' AND tl.duration_minutes IS NOT NULL
            """
            
            params = [user_id]
            
            if category_id:
                query += " AND t.category_id = %s"
                params.append(category_id)
            elif task_type:
                # Legacy support - search in task name or category name
                query += " AND (t.task_name LIKE %s OR EXISTS (SELECT 1 FROM task_categories tc WHERE tc.category_id = t.category_id AND tc.category_name LIKE %s))"
                search_term = f"%{task_type}%"
                params.extend([search_term, search_term])

            self.cursor.execute(query, params)
            result = self.cursor.fetchone()
            
            return result['avg_duration'] if result['avg_duration'] else 0

        except mysql.connector.Error as e:
            print(f"Database error in calculate_average_time: {e}")
            return 0

    def get_smart_scheduling_suggestion(self, user_id: int, task_name: str, category_id: int = None) -> Dict:
        """
        Provide intelligent scheduling suggestions based on past performance.
        
        Args:
            user_id: ID of the user
            task_name: Name of the new task
            category_id: Optional category ID for more specific suggestions
            
        Returns:
            Dictionary containing scheduling suggestions
        """
        try:
            suggestions = {
                "estimated_duration": 0,
                "confidence_level": "low",
                "recommended_breaks": [],
                "similar_tasks": []
            }

            # Find similar tasks based on task name and category
            similar_tasks_query = """
                SELECT t.task_name, tc.category_name, AVG(tl.duration_minutes) as avg_duration, 
                       COUNT(*) as completion_count, p.project_name
                FROM tasks t
                JOIN time_logs tl ON t.task_id = tl.task_id
                JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN projects p ON t.project_id = p.project_id
                WHERE t.user_id = %s AND ts.status_name = 'completed' 
                AND (t.task_name LIKE %s OR t.description LIKE %s)
                AND tl.duration_minutes IS NOT NULL
            """
            
            params = [user_id, f"%{task_name}%", f"%{task_name}%"]
            
            if category_id:
                similar_tasks_query += " AND t.category_id = %s"
                params.append(category_id)
            
            similar_tasks_query += """
                GROUP BY t.task_id, t.task_name, tc.category_name, p.project_name
                ORDER BY completion_count DESC
                LIMIT 5
            """
            
            self.cursor.execute(similar_tasks_query, params)
            similar_tasks = self.cursor.fetchall()

            if similar_tasks:
                # Calculate weighted average based on completion count
                total_weight = sum(task['completion_count'] for task in similar_tasks)
                weighted_avg = sum(
                    task['avg_duration'] * task['completion_count'] 
                    for task in similar_tasks
                ) / total_weight if total_weight > 0 else 0

                suggestions.update({
                    "estimated_duration": round(weighted_avg, 2),
                    "confidence_level": "high" if len(similar_tasks) >= 3 else "medium",
                    "similar_tasks": similar_tasks
                })
            else:
                # Fallback to general average for the category or overall
                if category_id:
                    general_avg = self.calculate_average_time(user_id, category_id=category_id)
                else:
                    general_avg = self.calculate_average_time(user_id)
                    
                suggestions.update({
                    "estimated_duration": round(general_avg, 2),
                    "confidence_level": "low"
                })

            # Suggest breaks based on estimated duration
            estimated_duration = suggestions["estimated_duration"]
            if estimated_duration > 120:  # More than 2 hours
                suggestions["recommended_breaks"] = [
                    {"time": estimated_duration // 2, "duration": 15, "type": "mid-session break"},
                    {"time": estimated_duration, "duration": 30, "type": "completion break"}
                ]
            elif estimated_duration > 60:  # More than 1 hour
                suggestions["recommended_breaks"] = [
                    {"time": estimated_duration, "duration": 15, "type": "completion break"}
                ]

            return suggestions

        except mysql.connector.Error as e:
            print(f"Database error in get_smart_scheduling_suggestion: {e}")
            return {"estimated_duration": 0, "confidence_level": "low", "recommended_breaks": [], "similar_tasks": []}

    def display_time_report(self, user_id: int, report_type: str = "all") -> None:
        """
        Display a formatted time report in the CLI.
        
        Args:
            user_id: ID of the user
            report_type: Type of report to display
        """
        report = self.generate_time_report(user_id, report_type)
        
        if not report:
            print("No data available for the selected report type.")
            return

        print(f"\n=== TIME REPORT ({report_type.upper()}) ===")
        print(f"Total Time Spent: {report['total_time']} minutes ({report['total_time']/60:.1f} hours)")
        print(f"Tasks Completed: {report['tasks_completed']}")
        print(f"Average Duration per Session: {report['average_duration']:.1f} minutes")
        
        if report['task_breakdown']:
            print("\nTask Breakdown:")
            headers = ["Task Name", "Total Time (min)", "Sessions", "Status", "Category", "Project"]
            table_data = [
                [task['task_name'], task['total_time'], task['sessions'], task['status'], task['category'], task['project']]
                for task in report['task_breakdown']
            ]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def suggest_break(self, user_id: int) -> Optional[Dict]:
        """
        Suggest a break based on user's recent activity.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Break suggestion or None
        """
        try:
            # Check recent activity (last 4 hours)
            recent_activity_query = """
                SELECT SUM(tl.duration_minutes) as recent_time
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                WHERE t.user_id = %s 
                AND tl.start_time >= DATE_SUB(NOW(), INTERVAL 4 HOUR)
                AND tl.duration_minutes IS NOT NULL
            """
            
            self.cursor.execute(recent_activity_query, (user_id,))
            result = self.cursor.fetchone()
            
            recent_time = result['recent_time'] if result['recent_time'] else 0
            
            if recent_time > 240:  # More than 4 hours
                return {
                    "type": "extended_break",
                    "duration": 30,
                    "message": "You've been working for over 4 hours. Consider taking a 30-minute break."
                }
            elif recent_time > 120:  # More than 2 hours
                return {
                    "type": "short_break",
                    "duration": 15,
                    "message": "You've been working for over 2 hours. Consider taking a 15-minute break."
                }
            elif recent_time > 60:  # More than 1 hour
                return {
                    "type": "micro_break",
                    "duration": 5,
                    "message": "You've been working for over 1 hour. Consider taking a 5-minute micro-break."
                }
            
            return None

        except mysql.connector.Error as e:
            print(f"Database error in suggest_break: {e}")
            return None

    def get_productivity_insights(self, user_id: int) -> Dict:
        """
        Generate productivity insights for the user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary containing productivity insights
        """
        try:
            insights = {
                "most_productive_time": None,
                "average_session_length": 0,
                "completion_rate": 0,
                "improvement_suggestions": [],
                "top_categories": [],
                "project_breakdown": []
            }

            # Find most productive time of day
            time_analysis_query = """
                SELECT HOUR(tl.start_time) as hour, 
                       AVG(tl.duration_minutes) as avg_duration,
                       COUNT(*) as session_count
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                WHERE t.user_id = %s AND tl.duration_minutes IS NOT NULL
                GROUP BY HOUR(tl.start_time)
                ORDER BY avg_duration DESC
                LIMIT 1
            """
            
            self.cursor.execute(time_analysis_query, (user_id,))
            result = self.cursor.fetchone()
            
            if result:
                insights["most_productive_time"] = f"{result['hour']:02d}:00"

            # Calculate average session length
            avg_session_query = """
                SELECT AVG(tl.duration_minutes) as avg_session
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                WHERE t.user_id = %s AND tl.duration_minutes IS NOT NULL
            """
            
            self.cursor.execute(avg_session_query, (user_id,))
            result = self.cursor.fetchone()
            
            if result and result['avg_session']:
                insights["average_session_length"] = round(result['avg_session'], 1)

            # Calculate completion rate
            completion_query = """
                SELECT 
                    COUNT(CASE WHEN ts.status_name = 'completed' THEN 1 END) as completed,
                    COUNT(*) as total
                FROM tasks t
                JOIN task_status ts ON t.status_id = ts.status_id
                WHERE t.user_id = %s
            """
            
            self.cursor.execute(completion_query, (user_id,))
            result = self.cursor.fetchone()
            
            if result and result['total'] > 0:
                insights["completion_rate"] = round((result['completed'] / result['total']) * 100, 1)

            # Get top categories
            top_categories_query = """
                SELECT tc.category_name, COUNT(*) as task_count, 
                       AVG(tl.duration_minutes) as avg_duration
                FROM tasks t
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN time_logs tl ON t.task_id = tl.task_id
                WHERE t.user_id = %s
                GROUP BY tc.category_id, tc.category_name
                ORDER BY task_count DESC
                LIMIT 5
            """
            
            self.cursor.execute(top_categories_query, (user_id,))
            insights["top_categories"] = self.cursor.fetchall()

            # Get project breakdown
            project_breakdown_query = """
                SELECT p.project_name, COUNT(t.task_id) as task_count,
                       SUM(tl.duration_minutes) as total_time
                FROM tasks t
                LEFT JOIN projects p ON t.project_id = p.project_id
                LEFT JOIN time_logs tl ON t.task_id = tl.task_id
                WHERE t.user_id = %s
                GROUP BY p.project_id, p.project_name
                ORDER BY total_time DESC
                LIMIT 5
            """
            
            self.cursor.execute(project_breakdown_query, (user_id,))
            insights["project_breakdown"] = self.cursor.fetchall()

            # Generate improvement suggestions
            suggestions = []
            if insights["average_session_length"] > 120:
                suggestions.append("Consider breaking longer sessions into smaller chunks for better focus.")
            if insights["completion_rate"] < 70:
                suggestions.append("Try setting more realistic deadlines to improve completion rates.")
            if not insights["most_productive_time"]:
                suggestions.append("Track your productivity patterns to identify your most productive hours.")

            insights["improvement_suggestions"] = suggestions

            return insights

        except mysql.connector.Error as e:
            print(f"Database error in get_productivity_insights: {e}")
            return insights

    def get_category_analytics(self, user_id: int) -> Dict:
        """
        Get analytics broken down by task categories.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary containing category analytics
        """
        try:
            category_query = """
                SELECT tc.category_name, 
                       COUNT(t.task_id) as total_tasks,
                       COUNT(CASE WHEN ts.status_name = 'completed' THEN 1 END) as completed_tasks,
                       AVG(tl.duration_minutes) as avg_duration,
                       SUM(tl.duration_minutes) as total_time
                FROM tasks t
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN time_logs tl ON t.task_id = tl.task_id
                WHERE t.user_id = %s
                GROUP BY tc.category_id, tc.category_name
                ORDER BY total_time DESC
            """
            
            self.cursor.execute(category_query, (user_id,))
            categories = self.cursor.fetchall()
            
            return {
                "categories": categories,
                "total_categories": len(categories)
            }
            
        except mysql.connector.Error as e:
            print(f"Database error in get_category_analytics: {e}")
            return {"categories": [], "total_categories": 0}

    def get_category_analytics(self, user_id=None):
        """Get category analytics for a specific user or for Streamlit."""
        try:
            # Use provided user_id or get from session state if available
            if user_id is None:
                # Try to get user_id from session state, fallback to 1 if not available
                import streamlit as st
                user_id = st.session_state.get('current_user', {}).get('user_id', 1)
                
            category_query = """
                SELECT COALESCE(tc.category_name, 'Uncategorized') as category_name, 
                       COUNT(t.task_id) as total_tasks,
                       COUNT(CASE WHEN ts.status_name = 'completed' THEN 1 END) as completed_tasks,
                       AVG(COALESCE(tl.duration_minutes, 0)) as avg_duration,
                       SUM(COALESCE(tl.duration_minutes, 0)) as total_time
                FROM tasks t
                LEFT JOIN task_categories tc ON t.category_id = tc.category_id
                LEFT JOIN task_status ts ON t.status_id = ts.status_id
                LEFT JOIN time_logs tl ON t.task_id = tl.task_id
                WHERE t.user_id = %s
                GROUP BY tc.category_id, tc.category_name
                HAVING total_time > 0
                ORDER BY total_time DESC
            """
            
            self.cursor.execute(category_query, (user_id,))
            categories = self.cursor.fetchall()
            
            if not categories:
                # Return dummy data for empty result
                return [{'category_name': 'No Data', 'total_time': 0}]
                
            return categories
            
        except Exception as e:
            print(f"Error in get_category_analytics: {e}")
            # Return dummy data for error case
            return [{'category_name': 'Error', 'total_time': 0}]

    def get_daily_time_analytics(self, days=7, user_id=None):
        """Get daily time analytics for the specified number of days."""
        try:
            # Use provided user_id or get from session state if available
            if user_id is None:
                # Try to get user_id from session state, fallback to 1 if not available
                import streamlit as st
                user_id = st.session_state.get('current_user', {}).get('user_id', 1)
                
            daily_query = """
                SELECT DATE(tl.start_time) as date,
                       SUM(COALESCE(tl.duration_minutes, 0)) / 60.0 as total_time
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                WHERE t.user_id = %s
                  AND tl.start_time >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY DATE(tl.start_time)
                ORDER BY date DESC
            """
            
            self.cursor.execute(daily_query, (user_id, days))
            results = self.cursor.fetchall()
            
            if not results:
                # Return dummy data for empty result
                today = datetime.now().date()
                return [{'date': today, 'total_time': 0}]
                
            return results
            
        except Exception as e:
            print(f"Error in get_daily_time_analytics: {e}")
            # Return dummy data for error case
            today = datetime.now().date()
            return [{'date': today, 'total_time': 0}]

    def get_task_completion_rate(self, user_id=None):
        """Get task completion rate for a specific user or for Streamlit."""
        try:
            # Use provided user_id or get from session state if available
            if user_id is None:
                # Try to get user_id from session state, fallback to 1 if not available
                import streamlit as st
                user_id = st.session_state.get('current_user', {}).get('user_id', 1)
                
            completion_query = """
                SELECT 
                    COUNT(CASE WHEN ts.status_name = 'completed' THEN 1 END) as completed,
                    COUNT(*) as total
                FROM tasks t
                JOIN task_status ts ON t.status_id = ts.status_id
                WHERE t.user_id = %s
            """
            
            self.cursor.execute(completion_query, (user_id,))
            result = self.cursor.fetchone()
            
            if result and result['total'] > 0:
                # Calculate percentage and ensure it's between 0-100%
                return min(100.0, (result['completed'] / result['total']) * 100)
            return 0
            
        except Exception as e:
            print(f"Error in get_task_completion_rate: {e}")
            return 0

    def get_productivity_insights_streamlit(self, user_id=None):
        """Get productivity insights for Streamlit."""
        try:
            # Use provided user_id or get from session state if available
            if user_id is None:
                # Try to get user_id from session state, fallback to 1 if not available
                import streamlit as st
                user_id = st.session_state.get('current_user', {}).get('user_id', 1)
                
            insights = []
            
            # Get most productive time
            productive_time_query = """
                SELECT HOUR(tl.start_time) as hour, AVG(COALESCE(tl.duration_minutes, 0)) as avg_duration
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                WHERE t.user_id = %s
                GROUP BY HOUR(tl.start_time)
                ORDER BY avg_duration DESC
                LIMIT 1
            """
            
            self.cursor.execute(productive_time_query, (user_id,))
            result = self.cursor.fetchone()
            
            if result:
                insights.append(f"Your most productive hour is {result['hour']}:00")
            
            # Get average session length
            session_query = """
                SELECT AVG(COALESCE(tl.duration_minutes, 0)) as avg_session
                FROM time_logs tl
                JOIN tasks t ON tl.task_id = t.task_id
                WHERE t.user_id = %s
            """
            
            self.cursor.execute(session_query, (user_id,))
            result = self.cursor.fetchone()
            
            if result and result['avg_session']:
                insights.append(f"Average session length: {result['avg_session']:.1f} minutes")
            
            # Get completion rate
            completion_rate = self.get_task_completion_rate(user_id)
            insights.append(f"Task completion rate: {completion_rate:.1f}%")
            
            return insights
            
        except Exception as e:
            print(f"Error in get_productivity_insights_streamlit: {e}")
            return ["No productivity data available yet"] 
            
            return insights
            
        except mysql.connector.Error as e:
            print(f"Database error in get_productivity_insights: {e}")
            return []
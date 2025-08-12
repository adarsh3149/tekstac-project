"""
Smart Time-Tracking and Task Scheduler - Streamlit Web Interface
A beautiful, modern web application for intelligent time tracking and task management.
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import time
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.auth import Auth
from modules.task_manager import TaskManager
from modules.time_tracker import TimeTracker
from modules.analytics import Analytics
from modules.intelligent_scheduler import IntelligentScheduler

# Page configuration
st.set_page_config(
    page_title="Smart Time Tracker",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    
    .task-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
    }
    
    .task-card.overdue {
        border-left-color: #f44336;
    }
    
    .task-card.due-soon {
        border-left-color: #ff9800;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

class SmartTimeTrackerApp:
    def __init__(self):
        """Initialize the Streamlit application."""
        self.auth = Auth()
        self.task_manager = None
        self.time_tracker = None
        self.analytics = None
        self.scheduler = None
        
        # Initialize session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        if 'task_created' not in st.session_state:
            st.session_state.task_created = False
        if 'last_task_info' not in st.session_state:
            st.session_state.last_task_info = None

    def initialize_modules(self):
        """Initialize modules for the current user."""
        if not st.session_state.authenticated:
            return False
        
        try:
            user_id = st.session_state.current_user['user_id']
            self.task_manager = TaskManager(user_id)
            self.time_tracker = TimeTracker(user_id)
            self.analytics = Analytics(self.auth.db_connector.get_connection())
            self.scheduler = IntelligentScheduler(user_id)
            return True
        except Exception as e:
            st.error(f"Error initializing modules: {e}")
            return False

    def show_login_page(self):
        """Display the login/signup page."""
        st.markdown("""
        <div class="main-header">
            <h1>⏰ Smart Time-Tracking & Task Scheduler</h1>
            <p>Intelligent time management with AI-powered insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
            
            with tab1:
                st.markdown("### Welcome Back!")
                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="Enter your email")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")
                    submit_login = st.form_submit_button("Login", use_container_width=True)
                    
                    if submit_login:
                        if self.auth.log_in(email, password):
                            st.session_state.authenticated = True
                            st.session_state.current_user = self.auth.get_current_user()
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please try again.")
            
            with tab2:
                st.markdown("### Create New Account")
                with st.form("signup_form"):
                    new_name = st.text_input("Full Name", placeholder="Enter your full name")
                    new_email = st.text_input("Email", placeholder="Enter your email")
                    new_password = st.text_input("Password", type="password", placeholder="Create a password")
                    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                    submit_signup = st.form_submit_button("Sign Up", use_container_width=True)
                    
                    if submit_signup:
                        if new_password != confirm_password:
                            st.error("Passwords do not match!")
                        elif self.auth.sign_up(new_email, new_password, new_name):
                            st.success("Account created successfully! Please log in.")
                        else:
                            st.error("Registration failed. Please try again.")

    def show_dashboard(self):
        """Display the main dashboard."""
        if not self.initialize_modules():
            return
        
        # Header
        user = st.session_state.current_user
        st.markdown(f"""
        <div class="main-header">
            <h1>Welcome back, {user['name']}! 👋</h1>
            <p>Let's make today productive with intelligent insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tasks = self.task_manager.get_total_tasks()
            st.markdown(f"""
            <div class="metric-card">
                <h3>📋 Total Tasks</h3>
                <h2>{total_tasks}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            completed_tasks = self.task_manager.get_completed_tasks()
            st.markdown(f"""
            <div class="metric-card">
                <h3>✅ Completed</h3>
                <h2>{completed_tasks}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pending_tasks = self.task_manager.get_pending_tasks()
            st.markdown(f"""
            <div class="metric-card">
                <h3>⏳ Pending</h3>
                <h2>{pending_tasks}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_time = self.time_tracker.get_total_time_today()
            st.markdown(f"""
            <div class="metric-card">
                <h3>⏰ Today's Time</h3>
                <h2>{total_time} min</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Recent Activity")
            self.show_recent_activity()
            
            st.markdown("### 🎯 Today's Tasks")
            self.show_todays_tasks()
        
        with col2:
            st.markdown("### 🚀 Quick Actions")
            self.show_quick_actions()
            
            st.markdown("### 💡 Smart Insights")
            self.show_smart_insights()

    def show_recent_activity(self):
        """Display recent activity chart."""
        try:
            # Get recent time logs (durations returned in minutes)
            time_logs = self.time_tracker.get_recent_time_logs(7)  # Last 7 days
            
            if time_logs:
                df = pd.DataFrame(time_logs)
                df['date'] = pd.to_datetime(df['start_time']).dt.date
                daily_time = df.groupby('date')['duration'].sum().reset_index()
                daily_time['hours'] = daily_time['duration'].fillna(0) / 60.0
                
                fig = px.line(daily_time, x='date', y='hours', 
                            title="Daily Time Tracking (Last 7 Days)",
                            labels={'hours': 'Hours', 'date': 'Date'})
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No recent activity to display.")
        except Exception as e:
            st.error(f"Error loading recent activity: {e}")

    def show_todays_tasks(self):
        """Display today's tasks."""
        try:
            tasks = self.task_manager.get_todays_tasks()
            
            if tasks:
                for task in tasks:
                    # Map status to emoji
                    status_color = {
                        'completed': '✅',
                        'in_progress': '🔄',
                        'pending': '⏳',
                        'overdue': '❌'
                    }.get(task['status'].lower(), '📋')
                    
                    # Map status to CSS class
                    css_class = "task-card"
                    if task['status'].lower() == 'overdue':
                        css_class += " overdue"
                    elif task['status'].lower() == 'pending':
                        css_class += " due-soon"
                    
                    # Format due date
                    due_date = task.get('due_date', 'No due date')
                    if due_date != 'No due date':
                        due_date = due_date.strftime('%Y-%m-%d %H:%M')
                    
                    # Display task card with all information
                    st.markdown(f"""
                    <div class="{css_class}">
                        <h4>{status_color} {task['task_name']}</h4>
                        <p><strong>Category:</strong> {task.get('category_name', 'Uncategorized')}</p>
                        <p><strong>Project:</strong> {task.get('project_name', 'No Project')}</p>
                        <p><strong>Due:</strong> {due_date}</p>
                        <p><strong>Status:</strong> {task['status'].replace('_', ' ').title()}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No tasks scheduled for today.")
        except Exception as e:
            st.error(f"Error loading tasks: {e}")

    def show_quick_actions(self):
        """Display quick action buttons."""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ New Task", use_container_width=True, key="quick_new_task"):
                st.session_state.current_page = 'new_task'
                st.rerun()
            
            if st.button("⏰ Start Timer", use_container_width=True, key="quick_start_timer"):
                st.session_state.current_page = 'time_tracker'
                st.rerun()
        
        with col2:
            if st.button("📅 Task Scheduler", use_container_width=True, key="quick_smart_schedule"):
                st.session_state.current_page = 'smart_schedule'
                st.rerun()
            
            if st.button("📊 Analytics", use_container_width=True, key="quick_analytics"):
                st.session_state.current_page = 'analytics'
                st.rerun()

    def show_smart_insights(self):
        """Display smart insights and recommendations."""
        try:
            insights = self.scheduler.get_schedule_recommendations()
            
            if insights:
                for insight in insights[:3]:  # Show top 3 insights
                    st.info(f"💡 {insight}")
            else:
                st.info("Complete more tasks to get personalized insights!")
        except Exception as e:
            st.error(f"Error loading insights: {e}")

    def show_new_task_page(self):
        """Display the new task creation page."""
        if not self.initialize_modules():
            return
            
        st.markdown("""
        <div class="main-header">
            <h1>➕ Create New Task</h1>
            <p>Add a new task with duration estimation</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get categories and projects (handle empty results gracefully)
        categories = self.task_manager.get_categories() or []

        category_options = (
            {cat['category_name']: cat['category_id'] for cat in categories}
            if categories else {"Uncategorized": None}
        )
        
        # Project selection section (outside form)
        st.markdown("### 📁 Project Selection")
        
        # Project input with autocomplete
        project_input = st.text_input("Project Name", placeholder="Type project name")
        
        with st.form("new_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                task_name = st.text_input("Task Name", placeholder="Enter task name")
                description = st.text_area("Description", placeholder="Enter task description")
                category_name = st.selectbox("Category", options=list(category_options.keys()))
            
            with col2:
                priority = st.selectbox("Priority", ["Low", "Medium", "High"])
                due_date = st.date_input("Due Date")
                due_time = st.time_input("Due Time")
                
                # Combine date and time (store date for DB)
                due_datetime = datetime.combine(due_date, due_time)
            
            submitted = st.form_submit_button("Create Task", use_container_width=True)
            
            if submitted and task_name:
                try:
                    # Get IDs (may be None when no options available)
                    category_id = category_options.get(category_name)
                    
                    # Handle project creation/selection
                    project_id = None
                    if project_input:
                        # Create new project
                        project_id = self.task_manager.create_project(project_input)
                    
                    # Create task
                    task_id = self.task_manager.create_task(
                        task_name=task_name,
                        description=description,
                        category_id=category_id,
                        project_id=project_id,
                        priority=priority,
                        due_date=due_datetime.date()
                    )
                    
                    if task_id:
                        st.success("Task created successfully!")
                        
                        # Store task info in session state for auto-scheduling
                        st.session_state.task_created = True
                        st.session_state.last_task_info = {
                            'task_name': task_name,
                            'description': description,
                            'category_id': category_id,
                            'project_id': project_id
                        }
                        
                        # Show duration estimate
                        prediction = self.scheduler.predict_task_duration(
                            task_name, description, category_id, project_id
                        )
                        
                        if prediction:
                            st.info(f"""
                            ⏱️ **Duration Estimate:**
                            - Estimated Duration: {prediction['duration']:.1f} hours
                            - Based on: {prediction['method']}
                            """)
                    else:
                        st.error("Failed to create task.")
                except Exception as e:
                    st.error(f"Error creating task: {e}")
        
        # Auto-schedule option (outside the form)
        if 'task_created' in st.session_state and st.session_state.task_created:
            if st.button("📅 Auto-Schedule This Task", key="auto_schedule_task"):
                try:
                    # Get the last created task info from session state
                    task_info = st.session_state.last_task_info
                    schedule = self.scheduler.create_smart_schedule([task_info])
                    
                    if schedule:
                        st.success("Task scheduled successfully!")
                        for scheduled_task in schedule:
                            st.info(f"📅 Scheduled: {scheduled_task['task_name']} at {scheduled_task['start_time']}")
                except Exception as e:
                    st.error(f"Error scheduling task: {e}")

    def show_time_tracker_page(self):
        """Display the time tracking page."""
        if not self.initialize_modules():
            return
            
        st.markdown("""
        <div class="main-header">
            <h1>⏰ Time Tracker</h1>
            <p>Track your time with intelligent insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🎯 Active Tasks")
            
            # Get active tasks
            active_tasks = self.task_manager.get_active_tasks()
            
            if active_tasks:
                task_names = [t['task_name'] for t in active_tasks]
                idx_map = {t['task_name']: i for i, t in enumerate(active_tasks)}
                selected_name = st.selectbox("Select Task to Track", options=task_names)
                selected_task = active_tasks[idx_map[selected_name]] if selected_name else None
                
                if selected_task:
                    col_start, col_stop = st.columns(2)
                    
                    with col_start:
                        if st.button("▶️ Start Timer", use_container_width=True, key="start_timer"):
                            try:
                                self.time_tracker.start_timer(selected_task['task_id'])
                                st.success("Timer started!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error starting timer: {e}")
                    
                    with col_stop:
                        if st.button("⏹️ Stop Timer", use_container_width=True, key="stop_timer"):
                            try:
                                if self.time_tracker.stop_timer():
                                    st.success("Timer stopped!")
                                    st.rerun()
                                else:
                                    st.error("Failed to stop timer")
                            except Exception as e:
                                st.error(f"Error stopping timer: {e}")

                    # Add some spacing
                    st.write("")
                    st.write("")
                    st.write("Select a task and use the buttons above to start or stop the timer.")
        
        with col2:
            st.markdown("### ⏱️ Live Timer")
            active = self.time_tracker.check_active_timer()
            
            # Add refresh button
            if st.button("🔄 Refresh Timer", key="refresh_timer"):
                st.rerun()
                
            if active:
                start_time = active['start_time']
                task_name = active['task_name']
                
                # Create a placeholder for the timer
                timer_placeholder = st.empty()
                
                # Calculate current elapsed time
                elapsed = (datetime.now() - start_time).total_seconds()
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)
                
                # Display current time in the placeholder with JavaScript for live updates
                timer_placeholder.markdown(f"""
                <div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px;'>
                <div id="timer-display" style='font-size: 2rem; font-weight: bold;'>{hours:02d}:{minutes:02d}:{seconds:02d}</div>
                <div style='font-style: italic;'>Task: {task_name}</div>
                </div>
                
                <script>
                    // Store the start time in JavaScript
                    const startTime = new Date('{start_time.isoformat()}');
                    
                    // Function to update the timer
                    function updateTimer() {{
                        const now = new Date();
                        const elapsedSeconds = Math.floor((now - startTime) / 1000);
                        
                        const hours = Math.floor(elapsedSeconds / 3600);
                        const minutes = Math.floor((elapsedSeconds % 3600) / 60);
                        const seconds = elapsedSeconds % 60;
                        
                        // Format with leading zeros
                        const formattedTime = 
                            String(hours).padStart(2, '0') + ':' + 
                            String(minutes).padStart(2, '0') + ':' + 
                            String(seconds).padStart(2, '0');
                        
                        // Update the timer display
                        document.getElementById('timer-display').textContent = formattedTime;
                    }}
                    
                    // Update immediately and then every second
                    updateTimer();
                    setInterval(updateTimer, 1000);
                </script>
                """, unsafe_allow_html=True)
            else:
                st.info("No timer running")

            st.markdown("### 📊 Today's Summary")
            
            # Get today's time logs (durations returned in minutes, may contain NULLs)
            today_logs = self.time_tracker.get_todays_time_logs()
            
            if today_logs:
                total_minutes = sum((log['duration'] or 0) for log in today_logs)
                st.metric("Total Time Today", f"{total_minutes} minutes")
                
                # Show recent sessions
                st.markdown("#### Recent Sessions")
                for log in today_logs[-5:]:  # Last 5 sessions
                    minutes = (log['duration'] or 0)
                    st.write(f"🕐 {log['task_name']}: {minutes} min")
            else:
                st.info("No time logged today.")

    def show_smart_schedule_page(self):
        """Display the smart scheduling page."""
        if not self.initialize_modules():
            return
            
        st.markdown("""
        <div class="main-header">
            <h1>📅 Smart Scheduler</h1>
            <p>Intelligent task scheduling and optimization</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📅 Create Schedule", "⏱️ Duration Predictor", "💡 Recommendations"])
        
        with tab1:
            st.markdown("### Create Smart Schedule")
            
            # Get pending tasks
            pending_tasks = self.task_manager.get_pending_tasks_list()
            
            if pending_tasks:
                selected_tasks = st.multiselect(
                    "Select Tasks to Schedule",
                    options=pending_tasks,
                    format_func=lambda x: x['task_name']
                )
                
                if selected_tasks and st.button("🤖 Generate Smart Schedule", use_container_width=True, key="generate_smart_schedule"):
                    try:
                        schedule = self.scheduler.create_smart_schedule(selected_tasks)
                        
                        if schedule:
                            st.success("Smart schedule generated!")
                            
                            for i, scheduled_task in enumerate(schedule, 1):
                                st.markdown(f"""
                                <div class="task-card">
                                    <h4>📅 {i}. {scheduled_task['task_name']}</h4>
                                    <p><strong>Start Time:</strong> {scheduled_task['start_time']}</p>
                                    <p><strong>Duration:</strong> {scheduled_task['duration']:.1f} hours</p>
                                    <p><strong>Break After:</strong> {scheduled_task.get('break_duration', 0)} minutes</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.error("Failed to generate schedule.")
                    except Exception as e:
                        st.error(f"Error generating schedule: {e}")
            else:
                st.info("No pending tasks to schedule.")
        
        with tab2:
            st.markdown("### Estimate Task Duration")
            
            with st.form("duration_estimator"):
                task_name = st.text_input("Task Name", placeholder="Enter task name")
                description = st.text_area("Description", placeholder="Enter task description")
                
                categories = self.task_manager.get_categories()
                projects = self.task_manager.get_projects()
                
                category_options = {cat['category_name']: cat['category_id'] for cat in categories}
                project_options = {proj['project_name']: proj['project_id'] for proj in projects}
                
                category_name = st.selectbox("Category", options=list(category_options.keys()))
                project_name = st.selectbox("Project", options=list(project_options.keys()))
                
                submitted = st.form_submit_button("Estimate Duration", use_container_width=True)
                
                if submitted and task_name:
                    try:
                        category_id = category_options[category_name]
                        project_id = project_options[project_name]
                        
                        prediction = self.scheduler.predict_task_duration(
                            task_name, description, category_id, project_id
                        )
                        
                        if prediction:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Estimated Duration", f"{prediction['duration']:.1f} hours")
                            
                            with col2:
                                st.metric("Based On", prediction['method'])
                        else:
                            st.error("Unable to estimate duration.")
                    except Exception as e:
                        st.error(f"Error estimating duration: {e}")
        
        with tab3:
            st.markdown("### Smart Recommendations")
            
            try:
                recommendations = self.scheduler.get_schedule_recommendations()
                
                if recommendations:
                    for i, rec in enumerate(recommendations, 1):
                        st.info(f"💡 **Recommendation {i}:** {rec}")
                else:
                    st.info("Complete more tasks to get personalized recommendations!")
            except Exception as e:
                st.error(f"Error loading recommendations: {e}")

    def show_tasks_page(self):
        """Display tasks by status with simple tabs."""
        if not self.initialize_modules():
            return
        st.markdown("""
        <div class="main-header">
            <h1>📋 Tasks</h1>
            <p>Browse tasks by status</p>
        </div>
        """, unsafe_allow_html=True)

        tabs = st.tabs(["⏳ Pending", "🔄 In Progress", "✅ Completed", "❌ Cancelled"])
        statuses = ["pending", "in-progress", "completed", "cancelled"]
        for tab, status in zip(tabs, statuses):
            with tab:
                tasks = self.task_manager.get_tasks_by_status(status)
                if not tasks:
                    st.info("No tasks here yet.")
                for task in tasks:
                    due = task.get('due_date')
                    due_text = due.strftime('%Y-%m-%d') if due else 'No due date'
                    st.markdown(f"""
                    <div class="task-card">
                        <h4>{task['task_name']}</h4>
                        <p><strong>Project:</strong> {task.get('project_name') or 'No Project'}</p>
                        <p><strong>Category:</strong> {task.get('category_name') or 'Uncategorized'}</p>
                        <p><strong>Due:</strong> {due_text}</p>
                        <p><strong>Status:</strong> {task.get('status_name','').title()}</p>
                    </div>
                    """, unsafe_allow_html=True)

    def show_analytics_page(self):
        """Display the analytics page."""
        if not self.initialize_modules():
            return
            
        st.markdown("""
        <div class="main-header">
            <h1>📊 Analytics Dashboard</h1>
            <p>Data-driven insights and productivity analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📈 Time Analytics", "🎯 Task Analytics", "🚀 Productivity Insights"])
        
        with tab1:
            st.markdown("### Time Tracking Analytics")
            
            # Time distribution by category
            try:
                category_time = self.analytics.get_category_analytics()
                
                if category_time and len(category_time) > 0:
                    # Convert to DataFrame and ensure column names match
                    df = pd.DataFrame(category_time)
                    
                    if 'total_time' in df.columns and 'category_name' in df.columns:
                        fig = px.pie(df, values='total_time', names='category_name', 
                                   title="Time Distribution by Category")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Missing required columns in category data.")
                else:
                    st.info("No time data available for analysis.")
            except Exception as e:
                st.error(f"Error loading category analytics: {e}")
            
            # Daily time tracking
            try:
                daily_time = self.analytics.get_daily_time_analytics(7)  # Last 7 days
                
                if daily_time and len(daily_time) > 0:
                    # Convert to DataFrame and ensure column names match
                    df = pd.DataFrame(daily_time)
                    
                    if 'date' in df.columns and 'total_time' in df.columns:
                        fig = px.bar(df, x='date', y='total_time', 
                                   title="Daily Time Tracking (Last 7 Days)",
                                   labels={'total_time': 'Hours', 'date': 'Date'})
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Missing required columns in daily time data.")
                else:
                    st.info("No daily time data available for analysis.")
            except Exception as e:
                st.error(f"Error loading daily analytics: {e}")
        
        with tab2:
            st.markdown("### Task Completion Analytics")
            
            # Task completion rate
            try:
                completion_rate = self.analytics.get_task_completion_rate()
                # Format as percentage but ensure it's between 0-100%
                formatted_rate = min(100.0, completion_rate)
                st.metric("Task Completion Rate", f"{formatted_rate:.1f}%")
                
                # Tasks by status
                status_counts = self.task_manager.get_task_status_counts()
                
                if status_counts and len(status_counts) > 0:
                    # Convert to DataFrame and ensure column names match
                    df = pd.DataFrame(status_counts)
                    
                    if 'status' in df.columns and 'count' in df.columns:
                        fig = px.bar(df, x='status', y='count', 
                                   title="Tasks by Status",
                                   labels={'count': 'Number of Tasks', 'status': 'Status'})
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Missing required columns in status counts data.")
                else:
                    st.info("No task status data available for analysis.")
            except Exception as e:
                st.error(f"Error loading task analytics: {e}")
        
        with tab3:
            st.markdown("### Productivity Insights")
            
            try:
                # Productivity insights
                insights = self.analytics.get_productivity_insights_streamlit()
                
                if insights:
                    for insight in insights:
                        st.info(f"💡 {insight}")
                
                # Break suggestions
                # Get current user ID from session state
                user_id = st.session_state.get('current_user', {}).get('user_id', 1)
                break_suggestion = self.analytics.suggest_break(user_id)
                if break_suggestion and 'message' in break_suggestion:
                    st.warning(f"🛑 {break_suggestion['message']}")
                
                # Smart scheduling suggestions
                scheduling_suggestion = self.analytics.get_smart_scheduling_suggestion(user_id, "general")
                if scheduling_suggestion:
                    est_duration = scheduling_suggestion.get('estimated_duration', 0)
                    confidence = scheduling_suggestion.get('confidence_level', 'low')
                    st.success(f"📅 Estimated task duration: {est_duration:.1f} minutes with {confidence} confidence")
            except Exception as e:
                st.error(f"Error loading productivity insights: {e}")

    def show_tasks_page(self):
        """Display tasks by status with simple tabs and editing."""
        if not self.initialize_modules():
            return
        st.markdown("""
        <div class="main-header">
            <h1>📋 Tasks</h1>
            <p>Browse and edit tasks by status</p>
        </div>
        """, unsafe_allow_html=True)

        tabs = st.tabs(["⏳ Pending", "🔄 In Progress", "✅ Completed", "❌ Cancelled"])
        statuses = ["pending", "in-progress", "completed", "cancelled"]
        for tab, status in zip(tabs, statuses):
            with tab:
                tasks = self.task_manager.get_tasks_by_status(status)
                if not tasks:
                    st.info("No tasks here yet.")
                    continue
                for task in tasks:
                    due = task.get('due_date')
                    due_text = due.strftime('%Y-%m-%d') if due else 'No due date'
                    with st.container(border=True):
                        cols = st.columns([3, 2, 2, 2, 2])
                        with cols[0]:
                            name_key = f"name_{status}_{task['task_id']}"
                            desc_key = f"desc_{status}_{task['task_id']}"
                            new_name = st.text_input("Task", value=task['task_name'], key=name_key)
                            new_desc = st.text_area("Desc", value=task.get('description') or "", key=desc_key, height=80)
                        with cols[1]:
                            st.write(f"Project: {task.get('project_name') or 'No Project'}")
                            st.write(f"Due: {due_text}")
                        with cols[2]:
                            # Quick category edit
                            categories = self.task_manager.get_categories() or []
                            opts = {c['category_name']: c['category_id'] for c in categories} or {"Uncategorized": None}
                            current = task.get('category_name') or 'Uncategorized'
                            cat_key = f"cat_{status}_{task['task_id']}"
                            new_cat = st.selectbox("Category", options=list(opts.keys()), index=list(opts.keys()).index(current) if current in opts else 0, key=cat_key)
                        with cols[3]:
                            # Status changer via button
                            next_status_cycle = {
                                'pending': 'in-progress',
                                'in-progress': 'completed',
                                'completed': 'pending',
                                'cancelled': 'pending',
                            }
                            current_status = task.get('status_name') or status
                            next_status = next_status_cycle.get(current_status, 'pending')
                            if st.button(f"Set {next_status.title()}", key=f"set_status_{status}_{task['task_id']}"):
                                if self.task_manager.update_task_status(task['task_id'], next_status):
                                    st.success("Status updated")
                                    st.rerun()
                                else:
                                    st.error("Update failed")
                        with cols[4]:
                            if st.button("Save", key=f"save_{status}_{task['task_id']}"):
                                ok = self.task_manager.update_task_details(
                                    task_id=task['task_id'],
                                    task_name=new_name,
                                    description=new_desc,
                                    category_id=opts.get(new_cat),
                                )
                                if ok:
                                    st.success("Saved")
                                    st.rerun()
                                else:
                                    st.error("Failed to save")

    def show_sidebar(self):
        """Display the sidebar navigation."""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h2>⏰ Smart Tracker</h2>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.authenticated:
                user = st.session_state.current_user
                st.markdown(f"**Welcome, {user['name']}**")
                
                st.markdown("---")
                
                # Navigation
                pages = {
                    "🏠 Dashboard": "dashboard",
                    "➕ New Task": "new_task",
                    "⏰ Time Tracker": "time_tracker",
                    "🤖 Smart Schedule": "smart_schedule",
                    "📋 Tasks": "tasks",
                    "📊 Analytics": "analytics"
                }
                
                for page_name, page_id in pages.items():
                    if st.button(page_name, use_container_width=True, key=f"sidebar_{page_id}"):
                        st.session_state.current_page = page_id
                        st.rerun()
                
                st.markdown("---")
                
                if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
                    st.session_state.authenticated = False
                    st.session_state.current_user = None
                    st.session_state.current_page = 'dashboard'
                    self.auth.log_out()
                    st.rerun()

    def run(self):
        """Main application runner."""
        # Show sidebar
        self.show_sidebar()
        
        # Route to appropriate page
        if not st.session_state.authenticated:
            self.show_login_page()
        else:
            if st.session_state.current_page == 'dashboard':
                self.show_dashboard()
            elif st.session_state.current_page == 'new_task':
                self.show_new_task_page()
            elif st.session_state.current_page == 'time_tracker':
                self.show_time_tracker_page()
            elif st.session_state.current_page == 'smart_schedule':
                self.show_smart_schedule_page()
            elif st.session_state.current_page == 'tasks':
                self.show_tasks_page()
            elif st.session_state.current_page == 'analytics':
                self.show_analytics_page()

# Run the application
if __name__ == "__main__":
    app = SmartTimeTrackerApp()
    app.run()

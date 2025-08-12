-- Smart Time-Tracking and Task Scheduler Database Schema
-- Team Member 1: Database & Data Modeling

-- Create database
CREATE DATABASE IF NOT EXISTS smart_scheduler_db;
USE smart_scheduler_db;

-- Users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Projects table
CREATE TABLE projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    project_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Task status table
CREATE TABLE task_status (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL UNIQUE  -- e.g., 'pending', 'in-progress', 'completed'
);

-- Task categories table
CREATE TABLE task_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE -- e.g., 'coding', 'design', 'review'
);

-- Tasks table
CREATE TABLE tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    project_id INT,
    task_name VARCHAR(200) NOT NULL,
    description TEXT,
    status_id INT NOT NULL,
    category_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE SET NULL,
    FOREIGN KEY (status_id) REFERENCES task_status(status_id),
    FOREIGN KEY (category_id) REFERENCES task_categories(category_id)
);

-- Time logs table
CREATE TABLE time_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_minutes INT,  -- This can be calculated dynamically as well
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
);

-- Insert default task statuses
INSERT INTO task_status (status_name) VALUES 
('pending'),
('in-progress'), 
('completed'),
('cancelled');

-- Insert default task categories
INSERT INTO task_categories (category_name) VALUES 
('coding'),
('design'),
('review'),
('planning'),
('testing'),
('documentation'),
('meeting'),
('other');

-- Indexes for better performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status_id ON tasks(status_id);
CREATE INDEX idx_tasks_category_id ON tasks(category_id);
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_time_logs_task_id ON time_logs(task_id);
CREATE INDEX idx_time_logs_start_time ON time_logs(start_time);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_projects_user_id ON projects(user_id); 
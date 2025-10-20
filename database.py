

# import pyodbc
# import streamlit as st
# import pandas as pd
# from datetime import datetime, date, timedelta
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import smtplib
# import os
# import hashlib
# import secrets
# from typing import Optional, Dict, List
# import json


# # =============================================
# # Database Configuration & Connection
# # =============================================

# @st.cache_resource
# def get_db_connection():
#     """
#     Creates a MSSQL connection using Streamlit secrets or local config.
#     Connection is cached to avoid multiple connections.
#     """
#     try:
#         drivers = pyodbc.drivers()
#         print("Available drivers:", drivers)
        
#         # Try each driver until one works
        
#         for driver in drivers:
#             try:
#                 print(f"Testing driver: {driver}")
#                 conn = pyodbc.connect(
#                     f"DRIVER={{{driver}}};"
#                     "SERVER=localhost,1433;"
#                     "DATABASE=Task_flo_Database;"
#                     "UID=sa;"
#                     "PWD=Yashal309;"
#                     "Encrypt=yes;"
#                     "TrustServerCertificate=yes;"
#                 )
#                 print(f"✅ SUCCESS with driver: {driver}")
#                 return conn
#             except Exception as driver_error:
#                 print(f"❌ Failed with {driver}: {driver_error}")
#                 continue
        
#         st.error("❌ All ODBC drivers failed to connect")
#         return None
        
#     except Exception as e:
#         st.error(f"Failed to connect to SQL Server: {str(e)}")
#         return None

# # =============================================
# # Security & Password Hashing
# # =============================================

# class PasswordHasher:
#     """Handles password hashing and verification using SHA-256 with salt"""
    
#     @staticmethod
#     def hash_password(password: str) -> str:
#         """Hash a password with a random salt"""
#         salt = secrets.token_hex(16)
#         return f"{salt}${hashlib.sha256((salt + password).encode()).hexdigest()}"
    
#     @staticmethod
#     def verify_password(password: str, hashed_password: str) -> bool:
#         """Verify a password against its hash"""
#         try:
#             salt, hash_value = hashed_password.split('$')
#             return hashlib.sha256((salt + password).encode()).hexdigest() == hash_value
#         except:
#             return False

# # =============================================
# # Database Initialization
# # =============================================

# def init_database():
#     """Initialize database schema with proper enterprise structure"""
#     conn = get_db_connection()
#     if conn is None:
#         st.error("❌ Cannot initialize database - no connection")
#         return
    
#     cursor = None
#     try:
#         cursor = conn.cursor()
        
#         # Create users table with proper security
#         cursor.execute("""
#             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
#             CREATE TABLE users (
#                 user_id INT PRIMARY KEY IDENTITY(1,1),
#                 username NVARCHAR(50) UNIQUE NOT NULL,
#                 email NVARCHAR(100) UNIQUE NOT NULL,
#                 password_hash NVARCHAR(255) NOT NULL,
#                 role NVARCHAR(20) NOT NULL CHECK (role IN ('admin', 'user')),
#                 is_active BIT DEFAULT 1,
#                 created_at DATETIME2 DEFAULT GETDATE(),
#                 updated_at DATETIME2 DEFAULT GETDATE(),
#                 last_login DATETIME2 NULL
#             )
#         """)
        
#         # Create domains table
#         cursor.execute("""
#             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='domains' AND xtype='U')
#             CREATE TABLE domains (
#                 domain_id INT PRIMARY KEY IDENTITY(1,1),
#                 domain_name NVARCHAR(100) UNIQUE NOT NULL,
#                 mancom_member_name NVARCHAR(100) NOT NULL,
#                 mancom_member_email NVARCHAR(100) NOT NULL,
#                 is_active BIT DEFAULT 1,
#                 created_at DATETIME2 DEFAULT GETDATE()
#             )
#         """)
        
#         # Create tasks table with proper enums and JSON comments
#         cursor.execute("""
#             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
#             CREATE TABLE tasks (
#                 task_id INT PRIMARY KEY IDENTITY(1,1),
#                 title NVARCHAR(255) NOT NULL,
#                 description NVARCHAR(MAX),
#                 domain NVARCHAR(100),
#                 assigned_to INT,
#                 attachment NVARCHAR(MAX),
#                 status NVARCHAR(20) NOT NULL DEFAULT 'open' 
#                     CHECK (status IN ('open', 'in_progress', 'closed')),
#                 priority NVARCHAR(20) NOT NULL DEFAULT 'medium'
#                     CHECK (priority IN ('high', 'medium', 'low')),
#                 due_date DATETIME2,
#                 frequency NVARCHAR(50),
#                 comments NVARCHAR(MAX), -- JSON string for comments array
#                 created_by INT NOT NULL,
#                 created_at DATETIME2 DEFAULT GETDATE(),
#                 updated_at DATETIME2 DEFAULT GETDATE(),
#                 FOREIGN KEY (assigned_to) REFERENCES users(user_id),
#                 FOREIGN KEY (created_by) REFERENCES users(user_id)
#             )
#         """)
        
#         # Create task_history table for audit trail
#         cursor.execute("""
#             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='task_history' AND xtype='U')
#             CREATE TABLE task_history (
#                 history_id INT PRIMARY KEY IDENTITY(1,1),
#                 task_id INT NOT NULL,
#                 field_name NVARCHAR(100),
#                 old_value NVARCHAR(MAX),
#                 new_value NVARCHAR(MAX),
#                 changed_by INT,
#                 changed_at DATETIME2 DEFAULT GETDATE(),
#                 FOREIGN KEY (task_id) REFERENCES tasks(task_id),
#                 FOREIGN KEY (changed_by) REFERENCES users(user_id)
#             )
#         """)
        
#         # Create indexes for performance
#         indexes = [
#             "CREATE INDEX idx_users_email ON users(email)",
#             "CREATE INDEX idx_users_username ON users(username)",
#             "CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to)",
#             "CREATE INDEX idx_tasks_status ON tasks(status)",
#             "CREATE INDEX idx_tasks_priority ON tasks(priority)",
#             "CREATE INDEX idx_tasks_due_date ON tasks(due_date)",
#             "CREATE INDEX idx_tasks_created_by ON tasks(created_by)"
#         ]
        
#         for index_sql in indexes:
#             try:
#                 cursor.execute(f"""
#                     IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='{index_sql.split()[-1]}')
#                     {index_sql}
#                 """)
#             except Exception as e:
#                 print(f"Index creation warning: {e}")
        
#         conn.commit()
#         print("✅ Database schema created successfully!")
        
#         # Insert default admin user
#         default_password = "admin123"
#         hashed_password = PasswordHasher.hash_password(default_password)
        
#         default_users = [
#             ('admin', 'admin@nfoods.com', hashed_password, 'admin'),
#             ('yashal.ali', 'yashal.ali@nfoods.com', hashed_password, 'admin'),
#         ]
        
#         for username, email, password, role in default_users:
#             try:
#                 cursor.execute("""
#                     IF NOT EXISTS (SELECT 1 FROM users WHERE email = ?)
#                     INSERT INTO users (username, email, password_hash, role)
#                     VALUES (?, ?, ?, ?)
#                 """, (email, username, email, password, role))
#                 print(f"✅ Added user: {username}")
#             except Exception as e:
#                 print(f"⚠️ User {username} already exists: {e}")
        
#         # Insert default domains
#         default_domains = [
#             ('SAP', 'Robert Wilson', 'robert.wilson@nfoods.com'),
#             ('Network', 'Jennifer Lee', 'jennifer.lee@nfoods.com'),
#             ('EC', 'David Brown', 'david.brown@nfoods.com'),
#             ('SalesFlo', 'Maria Garcia', 'maria.garcia@nfoods.com'),
#             ('NFlo', 'James Miller', 'james.miller@nfoods.com'),
#             ('Help Desk', 'Patricia Davis', 'patricia.davis@nfoods.com'),
#             ('IT-Governance', 'Michael Taylor', 'michael.taylor@nfoods.com')
#         ]
        
#         for domain_name, mancom_name, mancom_email in default_domains:
#             try:
#                 cursor.execute("""
#                     IF NOT EXISTS (SELECT 1 FROM domains WHERE domain_name = ?)
#                     INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
#                     VALUES (?, ?, ?)
#                 """, (domain_name, domain_name, mancom_name, mancom_email))
#                 print(f"✅ Added domain: {domain_name}")
#             except Exception as e:
#                 print(f"⚠️ Domain {domain_name} already exists: {e}")
        
#         conn.commit()
#         print("✅ Database initialized successfully!")
        
#     except Exception as e:
#         st.error(f"Error initializing database: {str(e)}")
#         print(f"Database initialization error: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if cursor:
#             cursor.close()

# # =============================================
# # User Management Functions
# # =============================================

# def authenticate_user(email: str, password: str) -> Optional[Dict]:
#     """Authenticate user by email and return user data if successful"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         query = """
#             SELECT user_id, username, email, password_hash, role, is_active 
#             FROM users 
#             WHERE email = ? AND is_active = 1
#         """
#         df = pd.read_sql(query, conn, params=(email,))
        
#         if df.empty:
#             return None
            
#         user = df.iloc[0].to_dict()
        
#         if PasswordHasher.verify_password(password, user['password_hash']):
#             # Update last login
#             cursor = conn.cursor()
#             cursor.execute(
#                 "UPDATE users SET last_login = GETDATE() WHERE user_id = ?", 
#                 (user['user_id'],)
#             )
#             conn.commit()
#             cursor.close()
            
#             # Remove password hash from returned user data
#             del user['password_hash']
#             return user
#         return None
        
#     except Exception as e:
#         st.error(f"Authentication error: {str(e)}")
#         return None


# def get_user_by_email(email: str) -> Optional[Dict]:
#     """Get user by email (for Microsoft auth)"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         query = """
#             SELECT user_id, username, email, password_hash, role, is_active 
#             FROM users 
#             WHERE email = ? AND is_active = 1
#         """
#         df = pd.read_sql(query, conn, params=(email,))
        
#         if df.empty:
#             return None
            
#         user = df.iloc[0].to_dict()
#         # Remove password hash from returned user data
#         del user['password_hash']
#         return user
        
#     except Exception as e:
#         print(f"Error fetching user by email: {str(e)}")
#         return None
#     finally:
#         if conn:
#             conn.close()

# def change_user_password(user_id: int, current_password: str, new_password: str) -> bool:
#     """Change user password with verification"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Verify current password
#         cursor.execute(
#             "SELECT password_hash FROM users WHERE user_id = ?", 
#             (user_id,)
#         )
#         result = cursor.fetchone()
        
#         if not result or not PasswordHasher.verify_password(current_password, result[0]):
#             st.error("Current password is incorrect")
#             return False
        
#         # Update to new password
#         new_hashed_password = PasswordHasher.hash_password(new_password)
#         cursor.execute(
#             "UPDATE users SET password_hash = ?, updated_at = GETDATE() WHERE user_id = ?",
#             (new_hashed_password, user_id)
#         )
#         conn.commit()
#         return True
        
#     except Exception as e:
#         st.error(f"Error changing password: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()
# def create_user(username: str, email: str, password: str, role: str = 'user') -> bool:
#     """Create a new user with hashed password"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         hashed_password = PasswordHasher.hash_password(password)
#         cursor.execute("""
#             INSERT INTO users (username, email, password_hash, role)
#             VALUES (?, ?, ?, ?)
#         """, (username, email, hashed_password, role))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error creating user: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()
# def get_all_users() -> pd.DataFrame:
#     """Get all users (without password hashes)"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#             SELECT user_id, username, email, role, is_active, created_at, last_login
#             FROM users 
#             ORDER BY username
#         """
#         return pd.read_sql(query, conn)
#     except Exception as e:
#         st.error(f"Error fetching users: {str(e)}")
#         return pd.DataFrame()

# def get_all_users_with_names():
#     """Get all users with proper name field"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#             SELECT user_id, username, email, role, is_active, created_at, last_login,
#                    COALESCE(name, username) as display_name
#             FROM users 
#             ORDER BY username
#         """
#         df = pd.read_sql(query, conn)
#         return df
#     except Exception as e:
#         st.error(f"Error fetching users: {str(e)}")
#         return pd.DataFrame()
# def update_user(user_id: int, username: str, email: str, role: str, is_active: bool) -> bool:
#     """Update user details"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             UPDATE users 
#             SET username = ?, email = ?, role = ?, is_active = ?, updated_at = GETDATE()
#             WHERE user_id = ?
#         """, (username, email, role, is_active, user_id))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error updating user: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def delete_user(user_id: int) -> bool:
#     """Delete a user - simple version only handling users table"""
#     conn = get_db_connection()
#     if conn is None:
#         st.error("❌ No database connection")
#         return False
    
#     cursor = None
#     try:
#         cursor = conn.cursor()
        
#         # First, check if the user exists
#         cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
#         user = cursor.fetchone()
        
#         if not user:
#             st.error(f"❌ User with ID {user_id} not found")
#             return False
        
#         username = user[0]
        
#         # Prevent users from deleting themselves
#         if user_id == st.session_state.user_id:
#             st.error("❌ You cannot delete your own account")
#             return False
        
#         # Check if user has assigned tasks
#         cursor.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to = ?", (user_id,))
#         task_count = cursor.fetchone()[0]
        
#         if task_count > 0:
#             st.warning(f"⚠️ User '{username}' has {task_count} assigned tasks")
#             st.info("Please reassign the tasks to another user or set assigned_to to NULL first")
#             return False
        
#         # Simply delete the user (let database handle foreign key constraints)
#         cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
#         conn.commit()
        
#         if cursor.rowcount > 0:
#             st.success(f"✅ User '{username}' deleted successfully!")
#             return True
#         else:
#             st.error("❌ Failed to delete user")
#             return False
            
#     except pyodbc.IntegrityError as e:
#         st.error(f"❌ Cannot delete user: There are related records in other tables")
#         st.info("Please reassign or delete the user's tasks and comments first")
#         return False
#     except Exception as e:
#         st.error(f"❌ Error deleting user: {str(e)}")
#         if conn:
#             conn.rollback()
#         return False
#     finally:
#         if cursor:
#             cursor.close()

# #delete with proper checks and reassignment prompts to N/A or other users
# # def delete_user(user_id: int) -> bool:
# #     """Delete a user and set their assigned tasks to NULL"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         st.error("❌ No database connection")
# #         return False
    
# #     cursor = None
# #     try:
# #         cursor = conn.cursor()
        
# #         # First, check if the user exists
# #         cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
# #         user = cursor.fetchone()
        
# #         if not user:
# #             st.error(f"❌ User with ID {user_id} not found")
# #             return False
        
# #         username = user[0]
        
# #         # Prevent users from deleting themselves
# #         if user_id == st.session_state.user_id:
# #             st.error("❌ You cannot delete your own account")
# #             return False
        
# #         # Count tasks assigned to this user
# #         cursor.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to = ?", (user_id,))
# #         task_count = cursor.fetchone()[0]
        
# #         # Set assigned_to to NULL for all tasks assigned to this user
# #         if task_count > 0:
# #             cursor.execute("UPDATE tasks SET assigned_to = NULL WHERE assigned_to = ?", (user_id,))
# #             st.info(f"✅ Unassigned {task_count} tasks from user '{username}'")
        
# #         # Delete the user
# #         cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
# #         conn.commit()
        
# #         if cursor.rowcount > 0:
# #             st.success(f"✅ User '{username}' deleted successfully!")
# #             if task_count > 0:
# #                 st.info(f"📝 {task_count} tasks were unassigned and need to be reassigned")
# #             return True
# #         else:
# #             st.error("❌ Failed to delete user")
# #             return False
            
# #     except Exception as e:
# #         st.error(f"❌ Error deleting user: {str(e)}")
# #         if conn:
# #             conn.rollback()
# #         return False
# #     finally:
# #         if cursor:
# #             cursor.close()

# # =============================================
# # Task Management Functions
# # =============================================

# def create_task(
#     title: str, 
#     description: str, 
#     domain: str, 
#     assigned_to: int, 
#     priority: str, 
#     due_date: datetime,
#     frequency: str = 'One-time',
#     attachment: str = '',
#     created_by: int = None
# ) -> bool:
#     """Create a new task with empty comments array"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Initialize comments as empty JSON array
#         initial_comments = json.dumps([])
        
#         cursor.execute("""
#             INSERT INTO tasks (
#                 title, description, domain, assigned_to, priority, 
#                 due_date, frequency, attachment, comments, created_by
#             )
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """, (title, description, domain, assigned_to, priority, 
#               due_date, frequency, attachment, initial_comments, created_by))
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error creating task: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def get_tasks(
#     user_id: int = None, 
#     role: str = 'user', 
#     include_closed: bool = True  # Changed default to True
# ) -> pd.DataFrame:
#     """Get tasks based on user role and filters - NOW INCLUDES CLOSED TASKS BY DEFAULT"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         base_query = """
#             SELECT 
#                 t.task_id, t.title, t.description, t.domain, 
#                 t.assigned_to, t.attachment, t.status, t.priority,
#                 t.due_date, t.frequency, t.comments, t.created_at, t.updated_at,
#                 u.username AS assigned_username, u.email AS assigned_email,
#                 creator.username AS created_by_username
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             LEFT JOIN users creator ON t.created_by = creator.user_id
#         """
        
#         if role == 'admin':
#             if not include_closed:
#                 query = f"{base_query} WHERE t.status != 'closed' ORDER BY t.priority DESC, t.due_date ASC"
#             else:
#                 query = f"{base_query} ORDER BY t.priority DESC, t.due_date ASC"
#             df = pd.read_sql(query, conn)
#         else:
#             if not include_closed:
#                 query = f"{base_query} WHERE t.assigned_to = ? AND t.status != 'closed' ORDER BY t.priority DESC, t.due_date ASC"
#             else:
#                 query = f"{base_query} WHERE t.assigned_to = ? ORDER BY t.priority DESC, t.due_date ASC"
#             df = pd.read_sql(query, conn, params=(user_id,))
        
#         # Parse JSON comments
#         if not df.empty and 'comments' in df.columns:
#             df['comments'] = df['comments'].apply(lambda x: json.loads(x) if x else [])
        
#         return df
#     except Exception as e:
#         st.error(f"Error fetching tasks: {str(e)}")
#         return pd.DataFrame()
    
# def get_overdue_tasks():
#     """Get tasks that are overdue"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#         SELECT t.*, u.username AS assigned_username, u.email AS assigned_email
#         FROM tasks t
#         LEFT JOIN users u ON t.assigned_to = u.user_id
#         WHERE t.due_date < GETDATE() AND t.status IN ('open', 'in_progress')
#         ORDER BY t.due_date ASC
#         """
#         df = pd.read_sql(query, conn)
        
#         # Ensure status column exists
#         if 'status' not in df.columns:
#             df['status'] = 'open'
            
#         return df
#     except Exception as e:
#         st.error(f"Error fetching overdue tasks: {str(e)}")
#         return pd.DataFrame()

# def get_tasks_due_soon(days=7):
#     """Get tasks due within specified days"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#         SELECT t.*, u.username AS assigned_username, u.email AS assigned_email
#         FROM tasks t
#         LEFT JOIN users u ON t.assigned_to = u.user_id
#         WHERE t.due_date BETWEEN GETDATE() AND DATEADD(day, ?, GETDATE()) 
#           AND t.status IN ('open', 'in_progress')
#         ORDER BY t.due_date ASC
#         """
#         df = pd.read_sql(query, conn, params=(days,))
        
#         # Ensure status column exists
#         if 'status' not in df.columns:
#             df['status'] = 'open'
            
#         return df
#     except Exception as e:
#         st.error(f"Error fetching tasks due soon: {str(e)}")
#         return pd.DataFrame()


# def get_overdue_tasks():
#     """Get tasks that are overdue (fallback implementation)"""
#     try:
#         tasks_df = get_tasks(role='admin')
#         if tasks_df.empty:
#             return pd.DataFrame()
        
#         # Filter overdue tasks
#         overdue_tasks = tasks_df[
#             (tasks_df['due_date'] < datetime.now()) & 
#             (tasks_df['status'].isin(['open', 'in_progress']))
#         ]
        
#         return overdue_tasks
#     except Exception as e:
#         st.error(f"Error fetching overdue tasks: {str(e)}")
#         return pd.DataFrame()

# def get_tasks_due_soon(days=7):
#     """Get tasks due within specified days (fallback implementation)"""
#     try:
#         tasks_df = get_tasks(role='admin')
#         if tasks_df.empty:
#             return pd.DataFrame()
        
#         # Calculate date range
#         start_date = datetime.now()
#         end_date = start_date + timedelta(days=days)
        
#         # Filter tasks due soon
#         due_soon_tasks = tasks_df[
#             (tasks_df['due_date'] >= start_date) & 
#             (tasks_df['due_date'] <= end_date) & 
#             (tasks_df['status'].isin(['open', 'in_progress']))
#         ]
        
#         return due_soon_tasks
#     except Exception as e:
#         st.error(f"Error fetching tasks due soon: {str(e)}")
#         return pd.DataFrame()

# def get_task_history(task_id):
#     """Get history of changes for a task"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#         SELECT th.field_name, th.old_value, th.new_value, th.changed_at, u.username as changed_by_name
#         FROM task_history th
#         LEFT JOIN users u ON th.changed_by = u.user_id
#         WHERE th.task_id = ?
#         ORDER BY th.changed_at DESC
#         """
#         df = pd.read_sql(query, conn, params=(task_id,))
#         return df
#     except Exception as e:
#         st.error(f"Error fetching task history: {str(e)}")
#         return pd.DataFrame()
    
# def get_task_by_id(task_id: int) -> Optional[Dict]:
#     """Get a specific task by ID"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         query = """
#             SELECT 
#                 t.*,
#                 u.username AS assigned_username, u.email AS assigned_email,
#                 creator.username AS created_by_username
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             LEFT JOIN users creator ON t.created_by = creator.user_id
#             WHERE t.task_id = ?
#         """
#         df = pd.read_sql(query, conn, params=(task_id,))
        
#         if df.empty:
#             return None
        
#         task = df.iloc[0].to_dict()
        
#         # Parse comments JSON
#         if task.get('comments'):
#             task['comments'] = json.loads(task['comments'])
#         else:
#             task['comments'] = []
            
#         return task
#     except Exception as e:
#         st.error(f"Error fetching task: {str(e)}")
#         return None

# def add_task_comment(task_id: int, user_id: int, comment_text: str) -> bool:
#     """Add a comment to a task"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Get current comments
#         cursor.execute("SELECT comments FROM tasks WHERE task_id = ?", (task_id,))
#         result = cursor.fetchone()
        
#         current_comments = []
#         if result and result[0]:
#             current_comments = json.loads(result[0])
        
#         # Add new comment
#         new_comment = {
#             'id': len(current_comments) + 1,
#             'user_id': user_id,
#             'username': st.session_state.user_name,  # From session state
#             'comment': comment_text,
#             'timestamp': datetime.now().isoformat()
#         }
        
#         current_comments.append(new_comment)
        
#         # Update task with new comments
#         cursor.execute(
#             "UPDATE tasks SET comments = ?, updated_at = GETDATE() WHERE task_id = ?",
#             (json.dumps(current_comments), task_id)
#         )
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error adding comment: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def update_task_status(task_id: int, new_status: str, changed_by: int) -> bool:
#     """Update task status with history tracking"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Get old status
#         cursor.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,))
#         old_status = cursor.fetchone()[0]
        
#         # Update task
#         cursor.execute(
#             "UPDATE tasks SET status = ?, updated_at = GETDATE() WHERE task_id = ?",
#             (new_status, task_id)
#         )
        
#         # Add to history
#         cursor.execute("""
#             INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
#             VALUES (?, 'status', ?, ?, ?)
#         """, (task_id, old_status, new_status, changed_by))
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error updating task status: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def update_task_priority(task_id: int, new_priority: str, changed_by: int) -> bool:
#     """Update task priority with history tracking"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Get old priority
#         cursor.execute("SELECT priority FROM tasks WHERE task_id = ?", (task_id,))
#         old_priority = cursor.fetchone()[0]
        
#         # Update task
#         cursor.execute(
#             "UPDATE tasks SET priority = ?, updated_at = GETDATE() WHERE task_id = ?",
#             (new_priority, task_id)
#         )
        
#         # Add to history
#         cursor.execute("""
#             INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
#             VALUES (?, 'priority', ?, ?, ?)
#         """, (task_id, old_priority, new_priority, changed_by))
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error updating task priority: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def update_task(task_id: int, title: str, description: str, domain: str, assigned_to: int, 
#                 attachment: str, status: str, due_date: date, frequency: str, 
#                 priority: str, updated_by: int) -> bool:
#     """Update entire task with history tracking"""
#     conn = get_db_connection()
#     if conn is None:
#         st.error("❌ No database connection")
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Get old values for history
#         cursor.execute("""
#             SELECT title, description, domain, assigned_to, attachment, status, due_date, frequency, priority 
#             FROM tasks WHERE task_id = ?
#         """, (task_id,))
#         old_values = cursor.fetchone()
        
#         if old_values:
#             old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = old_values
#         else:
#             # If no old values found, set defaults
#             old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = '', '', '', None, '', 'open', None, '', 'medium'

#         # Convert due_date to datetime if it's a date object
#         if isinstance(due_date, date) and not isinstance(due_date, datetime):
#             due_date = datetime.combine(due_date, datetime.min.time())

#         # Update task
#         cursor.execute("""
#             UPDATE tasks
#             SET title = ?, description = ?, domain = ?, assigned_to = ?, 
#                 attachment = ?, status = ?, due_date = ?, frequency = ?, priority = ?, updated_at = GETDATE()
#             WHERE task_id = ?
#         """, (title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, task_id))
        
#         # Add changes to history
#         fields_to_check = [
#             ('title', old_title, title),
#             ('description', old_description, description),
#             ('domain', old_domain, domain),
#             ('assigned_to', old_assigned_to, assigned_to),
#             ('attachment', old_attachment, attachment),
#             ('status', old_status, status),
#             ('due_date', old_due_date, due_date),
#             ('frequency', old_frequency, frequency),
#             ('priority', old_priority, priority)
#         ]
        
#         for field_name, old_val, new_val in fields_to_check:
#             if str(old_val) != str(new_val):
#                 cursor.execute("""
#                     INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
#                     VALUES (?, ?, ?, ?, ?)
#                 """, (task_id, field_name, str(old_val), str(new_val), updated_by))
        
#         conn.commit()
#         st.success("✅ Task updated successfully!")
#         return True
#     except Exception as e:
#         st.error(f"❌ Error updating task: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def delete_task(task_id: int) -> bool:
#     """Delete task and its related data"""
#     conn = get_db_connection()
#     if conn is None:
#         st.error("❌ No database connection")
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # First, check if task exists and get its title for confirmation
#         cursor.execute("SELECT title FROM tasks WHERE task_id = ?", (task_id,))
#         task = cursor.fetchone()
#         if not task:
#             st.error(f"❌ Task with ID {task_id} not found")
#             return False
        
#         task_title = task[0]
        
#         # Check which tables exist
#         cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
#         existing_tables = [table[0].lower() for table in cursor.fetchall()]
        
#         # Delete from task_history if table exists
#         if 'task_history' in existing_tables:
#             cursor.execute("DELETE FROM task_history WHERE task_id = ?", (task_id,))
        
#         # Delete from comments if table exists
#         if 'comments' in existing_tables:
#             cursor.execute("DELETE FROM comments WHERE task_id = ?", (task_id,))
        
#         # Delete the task
#         cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        
#         conn.commit()
#         st.success(f"✅ Task '{task_title}' deleted successfully!")
#         return True
#     except Exception as e:
#         st.error(f"❌ Error deleting task: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def send_escalation_email(task: dict, sender_email: str, sender_password: str) -> bool:
#     """Send escalation email to mancom member for overdue tasks"""
#     try:
#         mancom_member = get_mancom_member_by_domain(task.get('domain', ''))
#         if not mancom_member:
#             st.error(f"No mancom member found for domain: {task.get('domain', 'Unknown')}")
#             return False
        
#         msg = MIMEMultipart('alternative')
#         msg['Subject'] = f'🚨 ESCALATION: Overdue Task - {task.get("title", "Untitled Task")}'
#         msg['From'] = sender_email
#         msg['To'] = mancom_member.get('mancom_member_email', '')
        
#         # Safe data access
#         title = task.get('title', 'Untitled Task')
#         description = task.get('description', 'No description')
#         assigned_name = task.get('assigned_username', 'Unassigned')
#         domain = task.get('domain', 'Unknown')
#         status = task.get('status', 'open')
#         priority = task.get('priority', 'medium')
        
#         # Safe date handling
#         due_date_str = "Not specified"
#         overdue_days = 0
#         if pd.notna(task.get('due_date')):
#             try:
#                 due_date_str = task['due_date'].strftime("%Y-%m-%d")
#                 if isinstance(task['due_date'], (pd.Timestamp, datetime)):
#                     overdue_days = (datetime.now().date() - task['due_date'].date()).days
#                 else:
#                     due_date_str = str(task['due_date'])
#             except:
#                 due_date_str = "Invalid date"
        
#         html = f"""
#         <html>
#           <head>
#             <style>
#               body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
#               .container {{ max-width: 700px; margin: 0 auto; padding: 25px; }}
#               .header {{ border-bottom: 3px solid #dc2626; padding-bottom: 20px; margin-bottom: 30px; }}
#               .alert-box {{ background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 20px; margin-bottom: 25px; }}
#               .info-box {{ background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 16px; margin-bottom: 25px; }}
#               .task-details {{ width: 100%; border-collapse: collapse; }}
#               .task-details td {{ padding: 8px 0; }}
#             </style>
#           </head>
#           <body>
#             <div class="container">
#               <div class="header">
#                 <h1 style="color: #dc2626; margin: 0 0 10px 0; font-size: 26px; font-weight: 700;">🚨 Task Escalation Required</h1>
#                 <p style="color: #64748b; margin: 0; font-size: 16px;">A task requires your immediate attention as Mancom Member.</p>
#               </div>
              
#               <div class="alert-box">
#                 <h2 style="color: #dc2626; margin: 0 0 15px 0; font-size: 20px; font-weight: 600;">Task Details</h2>
                
#                 <table class="task-details">
#                   <tr>
#                     <td style="color: #475569; font-weight: 600; width: 120px;">Task Title:</td>
#                     <td style="color: #1e293b;">{title}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Description:</td>
#                     <td style="color: #1e293b;">{description}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Assigned To:</td>
#                     <td style="color: #1e293b;">{assigned_name}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Domain:</td>
#                     <td style="color: #1e293b;">{domain}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Due Date:</td>
#                     <td style="color: #1e293b;">{due_date_str}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Current Status:</td>
#                     <td style="color: #dc2626; font-weight: 600;">{status}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Overdue By:</td>
#                     <td style="color: #dc2626; font-weight: 600;">{overdue_days} days</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Priority:</td>
#                     <td style="color: #dc2626; font-weight: 600;">{priority}</td>
#                   </tr>
#                 </table>
#               </div>
              
#               <div class="info-box">
#                 <p style="margin: 0; color: #1e40af; font-size: 14px; font-weight: 500;">
#                   <strong>Action Required:</strong> This task is overdue and requires your attention as the Mancom member for the {domain} domain. 
#                   Please follow up with the assigned team member and ensure completion.
#                 </p>
#               </div>
              
#               <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
#                 <p style="color: #64748b; margin: 0 0 10px 0; font-size: 14px;">
#                   This is an automated escalation email from TaskFlow Pro System
#                 </p>
#                 <p style="color: #94a3b8; margin: 0; font-size: 12px;">
#                   Please do not reply to this email
#                 </p>
#               </div>
#             </div>
#           </body>
#         </html>
#         """
        
#         part = MIMEText(html, 'html')
#         msg.attach(part)
        
#         with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
#             server.starttls()  # Enable TLS
#             server.login(sender_email, sender_password)
#             server.send_message(msg)
        
#         st.success(f"✅ Escalation email sent to {mancom_member.get('mancom_member_name')}")
#         return True
        
#     except Exception as e:
#         st.error(f"❌ Error sending escalation email: {str(e)}")
#         return False

# def get_admin_users():
#     """Get all admin users - FIXED: Proper DataFrame structure"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#             SELECT user_id, username, email, role 
#             FROM users 
#             WHERE role = 'admin' AND is_active = 1
#         """
#         df = pd.read_sql(query, conn)
        
#         # Ensure the DataFrame has the correct structure
#         if not df.empty:
#             # Make sure we have all required columns
#             required_columns = ['user_id', 'username', 'email', 'role']
#             for col in required_columns:
#                 if col not in df.columns:
#                     df[col] = None
            
#             return df[required_columns]  # Return only the required columns in correct order
#         else:
#             return pd.DataFrame(columns=required_columns)
            
#     except Exception as e:
#         st.error(f"Error fetching admin users: {str(e)}")
#         print(f"Detailed error: {e}")
#         return pd.DataFrame(columns=['user_id', 'username', 'email', 'role'])

# def get_mancom_member_by_domain(domain_name: str):
#     """Get mancom member for a specific domain"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     cursor = None
#     try:
#         cursor = conn.cursor()
#         cursor.execute("""
#             SELECT mancom_member_name, mancom_member_email 
#             FROM domains 
#             WHERE domain_name = ? AND (is_active = 1 OR is_active IS NULL)
#         """, (domain_name,))
        
#         result = cursor.fetchone()
#         if result:
#             return {
#                 'mancom_member_name': result[0],
#                 'mancom_member_email': result[1]
#             }
#         return None
        
#     except Exception as e:
#         st.error(f"Error fetching mancom member: {str(e)}")
#         return None
#     finally:
#         if cursor:
#             cursor.close()

# def send_task_completion_notification(task, user_name, sender_email, sender_password):
#     """Send notification to admins when a task is completed - FIXED: Better error handling"""
#     try:
#         admin_users = get_admin_users()
        
#         if admin_users.empty:
#             print("No admin users found to send completion notification")
#             return False
        
#         success_count = 0
#         total_admins = len(admin_users)
        
#         for _, admin in admin_users.iterrows():
#             try:
#                 msg = MIMEMultipart('alternative')
#                 msg['Subject'] = f'✅ Task Completed: {task.get("title", "Untitled Task")}'
#                 msg['From'] = sender_email
#                 msg['To'] = admin.get('email', '')
                
#                 # Safe data access
#                 title = task.get('title', 'Untitled Task')
#                 description = task.get('description', 'No description')
#                 domain = task.get('domain', 'Unknown')
#                 frequency = task.get('frequency', 'One-time')
#                 priority = task.get('priority', 'Medium')
                
#                 # Safe date handling
#                 due_date_str = "Not specified"
#                 if pd.notna(task.get('due_date')):
#                     try:
#                         due_date_str = task['due_date'].strftime("%Y-%m-%d")
#                     except:
#                         due_date_str = "Invalid date"
                
#                 completion_time = datetime.now().strftime("%Y-%m-%d at %I:%M %p")
                
#                 html = f"""
#                 <html>
#                   <head>
#                     <style>
#                       body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
#                       .container {{ max-width: 700px; margin: 0 auto; padding: 25px; }}
#                       .header {{ border-bottom: 3px solid #10b981; padding-bottom: 20px; margin-bottom: 30px; }}
#                       .success-box {{ background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 25px; }}
#                       .info-box {{ background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 16px; margin-bottom: 25px; }}
#                       .task-details {{ width: 100%; border-collapse: collapse; }}
#                       .task-details td {{ padding: 8px 0; }}
#                     </style>
#                   </head>
#                   <body>
#                     <div class="container">
#                       <div class="header">
#                         <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 26px; font-weight: 700;">✅ Task Completed Successfully</h1>
#                         <p style="color: #64748b; margin: 0; font-size: 16px;">Great news! A task has been marked as completed.</p>
#                       </div>
                      
#                       <div class="success-box">
#                         <h2 style="color: #15803d; margin: 0 0 15px 0; font-size: 20px; font-weight: 600;">Task Details</h2>
                        
#                         <table class="task-details">
#                           <tr>
#                             <td style="color: #475569; font-weight: 600; width: 120px;">Task Title:</td>
#                             <td style="color: #1e293b;">{title}</td>
#                           </tr>
#                           <tr>
#                             <td style="color: #475569; font-weight: 600;">Description:</td>
#                             <td style="color: #1e293b;">{description}</td>
#                           </tr>
#                           <tr>
#                             <td style="color: #475569; font-weight: 600;">Completed By:</td>
#                             <td style="color: #1e293b;">{user_name}</td>
#                           </tr>
#                           <tr>
#                             <td style="color: #475569; font-weight: 600;">Domain:</td>
#                             <td style="color: #1e293b;">{domain}</td>
#                           </tr>
#                           <tr>
#                             <td style="color: #475569; font-weight: 600;">Due Date:</td>
#                             <td style="color: #1e293b;">{due_date_str}</td>
#                           </tr>
#                           <tr>
#                             <td style="color: #475569; font-weight: 600;">Frequency:</td>
#                             <td style="color: #1e293b;">{frequency}</td>
#                           </tr>
#                           <tr>
#                             <td style="color: #475569; font-weight: 600;">Priority:</td>
#                             <td style="color: #1e293b;">{priority}</td>
#                           </tr>
#                           <tr>
#                             <td style="color: #475569; font-weight: 600;">Completed On:</td>
#                             <td style="color: #15803d; font-weight: 600;">{completion_time}</td>
#                           </tr>
#                         </table>
#                       </div>
                      
#                       <div class="info-box">
#                         <p style="margin: 0; color: #1e40af; font-size: 14px;">
#                           <strong>Note:</strong> This task has been successfully completed and is now ready for your review.
#                         </p>
#                       </div>
                      
#                       <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
#                         <p style="color: #64748b; margin: 0 0 10px 0; font-size: 14px;">
#                           This is an automated notification from TaskFlow Pro System
#                         </p>
#                         <p style="color: #94a3b8; margin: 0; font-size: 12px;">
#                           Please do not reply to this email
#                         </p>
#                       </div>
#                     </div>
#                   </body>
#                 </html>
#                 """
                
#                 part = MIMEText(html, 'html')
#                 msg.attach(part)
                
#                 # Send email
#                 with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
#                     server.starttls()  # Enable TLS
#                     server.login(sender_email, sender_password)
#                     server.send_message(msg)
                
#                 success_count += 1
#                 print(f"✅ Completion notification sent to {admin.get('email')}")
                
#             except Exception as e:
#                 print(f"❌ Failed to send completion notification to {admin.get('email', 'Unknown')}: {str(e)}")
        
#         print(f"📧 Completion notifications: {success_count}/{total_admins} successful")
#         return success_count > 0
        
#     except Exception as e:
#         print(f"❌ Error in send_task_completion_notification: {str(e)}")
#         return False
# # =============================================
# # Domain Management Functions
# # =============================================

# def get_domains() -> pd.DataFrame:
#     """Get all active domains"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#             SELECT domain_id, domain_name, mancom_member_name, mancom_member_email
#             FROM domains 
#             WHERE is_active = 1
#             ORDER BY domain_name
#         """
#         return pd.read_sql(query, conn)
#     except Exception as e:
#         st.error(f"Error fetching domains: {str(e)}")
#         return pd.DataFrame()

# def get_mancom_member_by_domain(domain_name: str) -> Optional[Dict]:
#     """Get mancom member for a specific domain"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         query = """
#             SELECT mancom_member_name, mancom_member_email 
#             FROM domains 
#             WHERE domain_name = ? AND is_active = 1
#         """
#         df = pd.read_sql(query, conn, params=(domain_name,))
#         return df.iloc[0].to_dict() if not df.empty else None
#     except Exception as e:
#         st.error(f"Error fetching mancom member: {str(e)}")
#         return None

# # =============================================
# # Email Notification Functions
# # =============================================

# def send_task_notification(task: Dict, notification_type: str, sender_email: str, sender_password: str) -> bool:
#     """Send email notifications for task events"""
#     try:
#         if notification_type == 'completion':
#             return send_completion_notification(task, sender_email, sender_password)
#         elif notification_type == 'escalation':
#             return send_escalation_notification(task, sender_email, sender_password)
#         elif notification_type == 'assignment':
#             return send_assignment_notification(task, sender_email, sender_password)
#         else:
#             return False
#     except Exception as e:
#         st.error(f"Error sending notification: {str(e)}")
#         return False

# def send_completion_notification(task: Dict, sender_email: str, sender_password: str) -> bool:
#     """Send notification when task is completed"""
#     try:
#         admin_users = get_all_users()
#         admin_users = admin_users[admin_users['role'] == 'admin']
        
#         success_count = 0
#         for _, admin in admin_users.iterrows():
#             msg = MIMEMultipart('alternative')
#             msg['Subject'] = f'✅ Task Completed: {task["title"]}'
#             msg['From'] = sender_email
#             msg['To'] = admin['email']
            
#             html = create_completion_email_html(task, admin['username'])
#             part = MIMEText(html, 'html')
#             msg.attach(part)
            
#             try:
#                 with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#                     server.login(sender_email, sender_password)
#                     server.send_message(msg)
#                 success_count += 1
#             except Exception as e:
#                 print(f"Failed to send to {admin['email']}: {e}")
        
#         return success_count > 0
#     except Exception as e:
#         st.error(f"Error sending completion notification: {str(e)}")
#         return False

# def send_escalation_notification(task: Dict, sender_email: str, sender_password: str) -> bool:
#     """Send escalation notification for overdue tasks"""
#     try:
#         mancom_member = get_mancom_member_by_domain(task.get('domain', ''))
#         if not mancom_member:
#             return False
        
#         msg = MIMEMultipart('alternative')
#         msg['Subject'] = f'🚨 ESCALATION: Overdue Task - {task["title"]}'
#         msg['From'] = sender_email
#         msg['To'] = mancom_member['mancom_member_email']
        
#         html = create_escalation_email_html(task, mancom_member)
#         part = MIMEText(html, 'html')
#         msg.attach(part)
        
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#             server.login(sender_email, sender_password)
#             server.send_message(msg)
        
#         return True
#     except Exception as e:
#         st.error(f"Error sending escalation notification: {str(e)}")
#         return False

# def send_assignment_notification(task: Dict, sender_email: str, sender_password: str) -> bool:
#     """Send notification when task is assigned"""
#     # Implementation similar to above
#     pass

# def create_completion_email_html(task: Dict, admin_name: str) -> str:
#     """Create HTML email for task completion"""
#     due_date = task.get('due_date', 'Not specified')
#     if isinstance(due_date, (datetime, pd.Timestamp)):
#         due_date = due_date.strftime("%Y-%m-%d")
    
#     return f"""
#     <html>
#       <body>
#         <h2>Task Completed Successfully</h2>
#         <p>Hello {admin_name},</p>
#         <p>The following task has been marked as completed:</p>
#         <div style="background: #f0f8ff; padding: 15px; border-radius: 5px;">
#           <h3>{task['title']}</h3>
#           <p><strong>Description:</strong> {task.get('description', 'N/A')}</p>
#           <p><strong>Domain:</strong> {task.get('domain', 'N/A')}</p>
#           <p><strong>Due Date:</strong> {due_date}</p>
#           <p><strong>Priority:</strong> {task.get('priority', 'Medium')}</p>
#           <p><strong>Completed by:</strong> {st.session_state.user_name}</p>
#         </div>
#         <p>Best regards,<br>TaskFlow Pro System</p>
#       </body>
#     </html>
#     """

# def create_escalation_email_html(task: Dict, mancom_member: Dict) -> str:
#     """Create HTML email for task escalation"""
#     due_date = task.get('due_date', 'Not specified')
#     if isinstance(due_date, (datetime, pd.Timestamp)):
#         due_date = due_date.strftime("%Y-%m-%d")
    
#     return f"""
#     <html>
#       <body>
#         <h2 style="color: #dc3545;">🚨 Task Escalation Required</h2>
#         <p>Hello {mancom_member['mancom_member_name']},</p>
#         <p>The following task requires your immediate attention as it is overdue:</p>
#         <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
#           <h3>{task['title']}</h3>
#           <p><strong>Description:</strong> {task.get('description', 'N/A')}</p>
#           <p><strong>Domain:</strong> {task.get('domain', 'N/A')}</p>
#           <p><strong>Due Date:</strong> {due_date}</p>
#           <p><strong>Assigned To:</strong> {task.get('assigned_username', 'Unassigned')}</p>
#           <p><strong>Current Status:</strong> {task.get('status', 'Open')}</p>
#         </div>
#         <p>Please follow up with the assigned team member to ensure timely completion.</p>
#         <p>Best regards,<br>TaskFlow Pro System</p>
#       </body>
#     </html>
#     """


# def update_domain(domain_id, domain_name, mancom_member_name, mancom_member_email):
#     """Update domain details"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             UPDATE domains
#             SET domain_name = ?, mancom_member_name = ?, mancom_member_email = ?
#             WHERE domain_id = ?
#         """, (domain_name, mancom_member_name, mancom_member_email, domain_id))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error updating domain: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close() 

# def add_domain(domain_name: str, mancom_member_name: str, mancom_member_email: str) -> bool:
#     """Add a new domain to the database"""
#     conn = get_db_connection()
#     if conn is None:
#         st.error("❌ No database connection")
#         return False
    
#     cursor = None
#     try:
#         cursor = conn.cursor()
        
#         # Check if domain already exists
#         cursor.execute("SELECT domain_id FROM domains WHERE domain_name = ?", (domain_name,))
#         if cursor.fetchone():
#             st.error(f"❌ Domain '{domain_name}' already exists")
#             return False
        
#         # Check if is_active column exists
#         cursor.execute("""
#             SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
#             WHERE TABLE_NAME = 'domains' AND COLUMN_NAME = 'is_active'
#         """)
#         has_is_active = cursor.fetchone()[0] > 0
        
#         # Insert new domain
#         if has_is_active:
#             cursor.execute("""
#                 INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email, is_active)
#                 VALUES (?, ?, ?, 1)
#             """, (domain_name, mancom_member_name, mancom_member_email))
#         else:
#             cursor.execute("""
#                 INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
#                 VALUES (?, ?, ?)
#             """, (domain_name, mancom_member_name, mancom_member_email))
        
#         conn.commit()
#         st.success(f"✅ Domain '{domain_name}' added successfully!")
#         return True
        
#     except Exception as e:
#         st.error(f"❌ Error adding domain: {str(e)}")
#         if conn:
#             conn.rollback()
#         return False
#     finally:
#         if cursor:
#             cursor.close()

# def delete_domain(domain_id: int) -> bool:
#     """Delete a domain from the database"""
#     conn = get_db_connection()
#     if conn is None:
#         st.error("❌ No database connection")
#         return False
    
#     cursor = None
#     try:
#         cursor = conn.cursor()
        
#         # First, check if the domain exists
#         cursor.execute("SELECT domain_name FROM domains WHERE domain_id = ?", (domain_id,))
#         domain = cursor.fetchone()
        
#         if not domain:
#             st.error(f"❌ Domain with ID {domain_id} not found")
#             return False
        
#         domain_name = domain[0]
        
#         # Check if there are tasks associated with this domain
#         cursor.execute("SELECT COUNT(*) FROM tasks WHERE domain = ?", (domain_name,))
#         task_count = cursor.fetchone()[0]
        
#         if task_count > 0:
#             st.warning(f"⚠️ Cannot delete domain '{domain_name}' - it has {task_count} associated tasks")
#             st.info("Please reassign or delete the tasks first, or update the domain name instead of deleting")
#             return False
        
#         # Perform the deletion
#         cursor.execute("DELETE FROM domains WHERE domain_id = ?", (domain_id,))
#         conn.commit()
        
#         if cursor.rowcount > 0:
#             st.success(f"✅ Domain '{domain_name}' deleted successfully!")
#             return True
#         else:
#             st.error("❌ Failed to delete domain")
#             return False
            
#     except Exception as e:
#         st.error(f"❌ Error deleting domain: {str(e)}")
#         if conn:
#             conn.rollback()
#         return False
#     finally:
#         if cursor:
#             cursor.close()
# # =============================================
# # Streamlit UI Components
# # =============================================

# def render_login_form():
#     """Render user login form"""
#     st.title("🔐 TaskFlow Pro - Login")
    
#     with st.form("login_form"):
#         username = st.text_input("Username", placeholder="Enter your username")
#         password = st.text_input("Password", type="password", placeholder="Enter your password")
#         submit = st.form_submit_button("Login")
        
#         if submit:
#             if not username or not password:
#                 st.error("Please enter both username and password")
#                 return
            
#             user = authenticate_user(username, password)
#             if user:
#                 st.session_state.authenticated = True
#                 st.session_state.user_id = user['user_id']
#                 st.session_state.user_name = user['username']
#                 st.session_state.user_role = user['role']
#                 st.session_state.user_email = user['email']
#                 st.success(f"Welcome back, {user['username']}!")
#                 st.rerun()
#             else:
#                 st.error("Invalid username or password")

# def render_change_password_form():
#     """Render change password form"""
#     with st.expander("🔐 Change Password"):
#         with st.form("change_password_form"):
#             current_password = st.text_input("Current Password", type="password")
#             new_password = st.text_input("New Password", type="password")
#             confirm_password = st.text_input("Confirm New Password", type="password")
            
#             if st.form_submit_button("Change Password"):
#                 if not current_password or not new_password:
#                     st.error("Please fill all fields")
#                 elif new_password != confirm_password:
#                     st.error("New passwords don't match")
#                 elif len(new_password) < 6:
#                     st.error("Password must be at least 6 characters")
#                 else:
#                     if change_user_password(
#                         st.session_state.user_id, 
#                         current_password, 
#                         new_password
#                     ):
#                         st.success("Password changed successfully!")
#                     else:
#                         st.error("Failed to change password")

# def render_task_form(mode='create', task=None):
#     """Render task creation/editing form"""
#     users_df = get_all_users()
#     domains_df = get_domains()
    
#     with st.form(key=f"task_form_{mode}"):
#         col1, col2 = st.columns(2)
        
#         with col1:
#             title = st.text_input("Task Title", value=task.get('title', '') if task else '')
#             description = st.text_area("Description", value=task.get('description', '') if task else '')
#             domain = st.selectbox(
#                 "Domain", 
#                 options=domains_df['domain_name'].tolist(),
#                 index=domains_df[domains_df['domain_name'] == task.get('domain', '')].index[0] if task and task.get('domain') else 0
#             )
#             assigned_to = st.selectbox(
#                 "Assign To",
#                 options=users_df[users_df['is_active'] == True]['username'].tolist(),
#                 index=users_df[users_df['username'] == task.get('assigned_username', '')].index[0] if task and task.get('assigned_username') else 0
#             )
        
#         with col2:
#             priority = st.selectbox(
#                 "Priority",
#                 options=['high', 'medium', 'low'],
#                 index=['high', 'medium', 'low'].index(task.get('priority', 'medium')) if task else 1
#             )
#             due_date = st.date_input("Due Date", value=task.get('due_date', date.today()) if task else date.today())
#             frequency = st.selectbox(
#                 "Frequency",
#                 options=['One-time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'],
#                 index=['One-time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'].index(task.get('frequency', 'One-time')) if task else 0
#             )
#             attachment = st.text_input("Attachment URL", value=task.get('attachment', '') if task else '')
        
#         submitted = st.form_submit_button("Create Task" if mode == 'create' else "Update Task")
        
#         if submitted:
#             if not title:
#                 st.error("Task title is required")
#                 return False
            
#             # Get user_id from username
#             assigned_user_id = users_df[users_df['username'] == assigned_to]['user_id'].iloc[0]
            
#             if mode == 'create':
#                 success = create_task(
#                     title=title,
#                     description=description,
#                     domain=domain,
#                     assigned_to=assigned_user_id,
#                     priority=priority,
#                     due_date=due_date,
#                     frequency=frequency,
#                     attachment=attachment,
#                     created_by=st.session_state.user_id
#                 )
#                 if success:
#                     st.success("Task created successfully!")
#                     return True
#                 else:
#                     st.error("Failed to create task")
#                     return False
#             else:
#                 # Update task logic would go here
#                 pass
    
#     return False


# # =============================================
# # Main Application
# # =============================================

# def main():
#     """Main application entry point"""
    
#     # Initialize database
#     init_database()
    
#     # Initialize session state
#     if 'authenticated' not in st.session_state:
#         st.session_state.authenticated = False
    
#     # Check authentication
#     if not st.session_state.authenticated:
#         render_login_form()
#         return
    
#     # Main application after login
#     st.sidebar.title(f"👋 Welcome, {st.session_state.user_name}!")
#     st.sidebar.write(f"Role: {st.session_state.user_role}")
    
#     # Navigation
#     menu_options = ["📋 My Tasks", "➕ Create Task", "👥 User Management", "🏷️ Domain Management"]
#     if st.session_state.user_role == 'admin':
#         menu_options.extend(["📊 Admin Dashboard", "📧 Email Reports"])
    
#     selected_menu = st.sidebar.selectbox("Navigation", menu_options)
    
#     # Change password form in sidebar
#     render_change_password_form()
    
#     # Logout button
#     if st.sidebar.button("🚪 Logout"):
#         for key in list(st.session_state.keys()):
#             del st.session_state[key]
#         st.rerun()
    
#     # Main content area
#     if selected_menu == "📋 My Tasks":
#         st.title("My Tasks")
#         tasks_df = get_tasks(
#             user_id=st.session_state.user_id,
#             role=st.session_state.user_role,
#             include_closed=False
#         )
        
#         if tasks_df.empty:
#             st.info("No tasks assigned to you.")
#         else:
#             st.dataframe(tasks_df, use_container_width=True)
    
#     elif selected_menu == "➕ Create Task":
#         st.title("Create New Task")
#         render_task_form(mode='create')
    
#     elif selected_menu == "👥 User Management" and st.session_state.user_role == 'admin':
#         st.title("User Management")
#         users_df = get_all_users()
#         st.dataframe(users_df, use_container_width=True)
    
#     elif selected_menu == "🏷️ Domain Management" and st.session_state.user_role == 'admin':
#         st.title("Domain Management")
#         domains_df = get_domains()
#         st.dataframe(domains_df, use_container_width=True)
    
#     elif selected_menu == "📊 Admin Dashboard" and st.session_state.user_role == 'admin':
#         st.title("Admin Dashboard")
#         # Dashboard implementation would go here
    
#     elif selected_menu == "📧 Email Reports" and st.session_state.user_role == 'admin':
#         st.title("Email Reports")
#         # Email reporting implementation would go here

# if __name__ == "__main__":
#     st.set_page_config(
#         page_title="TaskFlow Pro",
#         page_icon="✅",
#         layout="wide",
#         initial_sidebar_state="expanded"
#     )
#     main()


import pyodbc
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
import hashlib
import secrets
from typing import Optional, Dict, List
import json
import msal
import requests
from urllib.parse import urlencode


# =============================================
# Microsoft Authentication Class
# =============================================

class MicrosoftAuth:
    def __init__(self):
        self.client_id = "client_id"
        self.tenant_id = "tenant_id"
        self.client_secret = "secert"
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["User.Read"]
        self.graph_endpoint = "https://graph.microsoft.com/v1.0/me"
        
    def get_redirect_uri(self):
        """Get the redirect URI dynamically"""
        if 'localhost' in st.get_option('browser.serverAddress') or st.get_option('browser.serverAddress') == '0.0.0.0':
            return "http://localhost:8501"
        return "https://your-app-domain.streamlit.app"
    
    def get_auth_url(self):
        """Generate Microsoft OAuth authorization URL"""
        try:
            redirect_uri = self.get_redirect_uri()
            
            params = {
                'client_id': self.client_id,
                'response_type': 'code',
                'redirect_uri': redirect_uri,
                'response_mode': 'query',
                'scope': 'openid profile email User.Read',
                'state': 'taskflow_auth'
            }
            
            auth_url = f"{self.authority}/oauth2/v2.0/authorize?{urlencode(params)}"
            return auth_url
            
        except Exception as e:
            print(f"Error generating auth URL: {e}")
            return None
    
    def get_token_from_code(self, code):
        """Exchange authorization code for access token"""
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_by_authorization_code(
                code,
                scopes=self.scope,
                redirect_uri=self.get_redirect_uri()
            )
            
            if "error" in result:
                print(f"Token acquisition error: {result.get('error')}")
                return None
            
            return result
            
        except Exception as e:
            print(f"Error acquiring token: {e}")
            return None
    
    def get_user_info(self, access_token):
        """Fetch user information from Microsoft Graph API"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(self.graph_endpoint, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'email': user_data.get('mail') or user_data.get('userPrincipalName'),
                    'displayName': user_data.get('displayName'),
                    'givenName': user_data.get('givenName'),
                    'surname': user_data.get('surname'),
                    'id': user_data.get('id')
                }
            else:
                print(f"Graph API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching user info: {e}")
            return None

# Create global instance
ms_auth = MicrosoftAuth()

# =============================================
# Database Configuration & Connection
# =============================================


@st.cache_resource
def get_db_connection():
    """Creates a MSSQL connection using Streamlit secrets or local config."""
    try:
        drivers = pyodbc.drivers()
        print("Available drivers:", drivers)
        
        for driver in drivers:
            try:
                print(f"Testing driver: {driver}")
                conn = pyodbc.connect(
                    f"DRIVER={{{driver}}};"
                    "SERVER=localhost,1433;"
                    "DATABASE=Task_flo_Database;"
                    "UID=sa;"
                    "PWD=Yashal309;"
                    "Encrypt=yes;"
                    "TrustServerCertificate=yes;"
                )
                print(f"✅ SUCCESS with driver: {driver}")
                return conn
            except Exception as driver_error:
                print(f"❌ Failed with {driver}: {driver_error}")
                continue
        
        st.error("❌ All ODBC drivers failed to connect")
        return None
        
    except Exception as e:
        st.error(f"Failed to connect to SQL Server: {str(e)}")
        return None

# =============================================
# Security & Password Hashing
# =============================================

class PasswordHasher:
    """Handles password hashing and verification using SHA-256 with salt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password with a random salt"""
        salt = secrets.token_hex(16)
        return f"{salt}${hashlib.sha256((salt + password).encode()).hexdigest()}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, hash_value = hashed_password.split('$')
            return hashlib.sha256((salt + password).encode()).hexdigest() == hash_value
        except:
            return False

# =============================================
# Enhanced Authentication Functions
# =============================================

def handle_microsoft_auth(email: str, name: str = None) -> Optional[Dict]:
    """
    Handle Microsoft authentication - automatically create user if doesn't exist
    """
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = None
    try:
        # Check if user exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, username, email, role, is_active 
            FROM users 
            WHERE email = ? AND is_active = 1
        """, (email,))
        
        result = cursor.fetchone()
        
        if result:
            # Existing user - update last login
            user = {
                'user_id': result[0],
                'username': result[1],
                'email': result[2],
                'role': result[3],
                'is_active': result[4]
            }
            
            cursor.execute(
                "UPDATE users SET last_login = GETDATE() WHERE user_id = ?", 
                (user['user_id'],)
            )
            conn.commit()
            
        else:
            # New user - auto-create with default role
            username = generate_username_from_email(email, name)
            role = 'user'  # Default role for new Microsoft users
            
            # Insert new user with microsoft_auth flag
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, auth_method)
                VALUES (?, ?, ?, ?, 'microsoft')
            """, (username, email, 'microsoft_auth', role))
            
            conn.commit()
            
            # Get the newly created user
            cursor.execute("""
                SELECT user_id, username, email, role, is_active 
                FROM users 
                WHERE email = ?
            """, (email,))
            
            result = cursor.fetchone()
            user = {
                'user_id': result[0],
                'username': result[1],
                'email': result[2],
                'role': result[3],
                'is_active': result[4]
            }
            
            st.success(f"✅ Welcome {name or username}! Your account has been created.")
        
        return user
        
    except Exception as e:
        st.error(f"Microsoft authentication error: {str(e)}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()

def generate_username_from_email(email: str, name: str = None) -> str:
    """Generate username from email or name"""
    if name:
        # Convert "John Doe" to "john.doe"
        username = name.lower().replace(' ', '.')
        
        # Check if username exists and make unique
        base_username = username
        counter = 1
        conn = get_db_connection()
        cursor = conn.cursor()
        
        while True:
            cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                break
            username = f"{base_username}{counter}"
            counter += 1
        
        cursor.close()
        return username
    else:
        # Use email prefix
        return email.split('@')[0]

def get_or_create_microsoft_user(email: str, name: str = None, department: str = None) -> Optional[Dict]:
    """
    Get existing user or create new one for Microsoft authentication
    with enhanced user information
    """
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("""
            SELECT user_id, username, email, role, is_active 
            FROM users 
            WHERE email = ?
        """, (email,))
        
        result = cursor.fetchone()
        
        if result:
            user = {
                'user_id': result[0],
                'username': result[1],
                'email': result[2],
                'role': result[3],
                'is_active': result[4]
            }
            
            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = GETDATE() WHERE user_id = ?", 
                (user['user_id'],)
            )
            
        else:
            # Create new user with Microsoft info
            username = generate_username_from_email(email, name)
            role = assign_role_based_on_department(department)
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, auth_method, created_at, last_login)
                VALUES (?, ?, ?, ?, 'microsoft', GETDATE(), GETDATE())
            """, (username, email, 'microsoft_auth', role))
            
            conn.commit()
            
            # Get the new user
            cursor.execute("SELECT user_id, username, email, role FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            user = {
                'user_id': result[0],
                'username': result[1],
                'email': result[2],
                'role': result[3]
            }
        
        conn.commit()
        return user
        
    except Exception as e:
        st.error(f"Error in Microsoft user management: {str(e)}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()

def assign_role_based_on_department(department: str) -> str:
    """Assign role based on department (customize this logic)"""
    if not department:
        return 'user'
    
    department = department.lower()
    
    # Custom logic based on your organization
    if any(term in department for term in ['it', 'admin', 'management']):
        return 'admin'
    elif any(term in department for term in ['lead', 'supervisor', 'manager']):
        return 'team_lead'
    else:
        return 'user'

# =============================================
# Database Initialization (Enhanced)
# =============================================

def init_database():
    """Initialize database schema with proper enterprise structure"""
    conn = get_db_connection()
    if conn is None:
        st.error("❌ Cannot initialize database - no connection")
        return
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Create users table with auth_method column
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                user_id INT PRIMARY KEY IDENTITY(1,1),
                username NVARCHAR(50) UNIQUE NOT NULL,
                email NVARCHAR(100) UNIQUE NOT NULL,
                password_hash NVARCHAR(255) NOT NULL,
                role NVARCHAR(20) NOT NULL CHECK (role IN ('admin', 'user')),
                auth_method NVARCHAR(20) DEFAULT 'traditional',
                is_active BIT DEFAULT 1,
                created_at DATETIME2 DEFAULT GETDATE(),
                updated_at DATETIME2 DEFAULT GETDATE(),
                last_login DATETIME2 NULL
            )
        """)
        
        # Create domains table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='domains' AND xtype='U')
            CREATE TABLE domains (
                domain_id INT PRIMARY KEY IDENTITY(1,1),
                domain_name NVARCHAR(100) UNIQUE NOT NULL,
                mancom_member_name NVARCHAR(100) NOT NULL,
                mancom_member_email NVARCHAR(100) NOT NULL,
                is_active BIT DEFAULT 1,
                created_at DATETIME2 DEFAULT GETDATE()
            )
        """)
        
        # Create tasks table with proper enums and JSON comments
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
            CREATE TABLE tasks (
                task_id INT PRIMARY KEY IDENTITY(1,1),
                title NVARCHAR(255) NOT NULL,
                description NVARCHAR(MAX),
                domain NVARCHAR(100),
                assigned_to INT,
                attachment NVARCHAR(MAX),
                status NVARCHAR(20) NOT NULL DEFAULT 'open' 
                    CHECK (status IN ('open', 'in_progress', 'closed')),
                priority NVARCHAR(20) NOT NULL DEFAULT 'medium'
                    CHECK (priority IN ('high', 'medium', 'low')),
                due_date DATETIME2,
                frequency NVARCHAR(50),
                comments NVARCHAR(MAX),
                created_by INT NOT NULL,
                created_at DATETIME2 DEFAULT GETDATE(),
                updated_at DATETIME2 DEFAULT GETDATE(),
                FOREIGN KEY (assigned_to) REFERENCES users(user_id),
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        """)
        
        # Create task_history table for audit trail
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='task_history' AND xtype='U')
            CREATE TABLE task_history (
                history_id INT PRIMARY KEY IDENTITY(1,1),
                task_id INT NOT NULL,
                field_name NVARCHAR(100),
                old_value NVARCHAR(MAX),
                new_value NVARCHAR(MAX),
                changed_by INT,
                changed_at DATETIME2 DEFAULT GETDATE(),
                FOREIGN KEY (task_id) REFERENCES tasks(task_id),
                FOREIGN KEY (changed_by) REFERENCES users(user_id)
            )
        """)
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX idx_users_email ON users(email)",
            "CREATE INDEX idx_users_username ON users(username)",
            "CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to)",
            "CREATE INDEX idx_tasks_status ON tasks(status)",
            "CREATE INDEX idx_tasks_priority ON tasks(priority)",
            "CREATE INDEX idx_tasks_due_date ON tasks(due_date)",
            "CREATE INDEX idx_tasks_created_by ON tasks(created_by)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(f"""
                    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='{index_sql.split()[-1]}')
                    {index_sql}
                """)
            except Exception as e:
                print(f"Index creation warning: {e}")
        
        conn.commit()
        print("✅ Database schema created successfully!")
        
        # Insert default admin user
        default_password = "admin123"
        hashed_password = PasswordHasher.hash_password(default_password)
        
        default_users = [
            ('admin', 'admin@nfoods.com', hashed_password, 'admin', 'traditional'),
            ('yashal.ali', 'yashal.ali@nfoods.com', hashed_password, 'admin', 'traditional'),
        ]
        
        for username, email, password, role, auth_method in default_users:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM users WHERE email = ?)
                    INSERT INTO users (username, email, password_hash, role, auth_method)
                    VALUES (?, ?, ?, ?, ?)
                """, (email, username, email, password, role, auth_method))
                print(f"✅ Added user: {username}")
            except Exception as e:
                print(f"⚠️ User {username} already exists: {e}")
        
        # Insert default domains
        default_domains = [
            ('SAP', 'Robert Wilson', 'robert.wilson@nfoods.com'),
            ('Network', 'Jennifer Lee', 'jennifer.lee@nfoods.com'),
            ('EC', 'David Brown', 'david.brown@nfoods.com'),
            ('SalesFlo', 'Maria Garcia', 'maria.garcia@nfoods.com'),
            ('NFlo', 'James Miller', 'james.miller@nfoods.com'),
            ('Help Desk', 'Patricia Davis', 'patricia.davis@nfoods.com'),
            ('IT-Governance', 'Michael Taylor', 'michael.taylor@nfoods.com')
        ]
        
        for domain_name, mancom_name, mancom_email in default_domains:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM domains WHERE domain_name = ?)
                    INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
                    VALUES (?, ?, ?)
                """, (domain_name, domain_name, mancom_name, mancom_email))
                print(f"✅ Added domain: {domain_name}")
            except Exception as e:
                print(f"⚠️ Domain {domain_name} already exists: {e}")
        
        conn.commit()
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")
        print(f"Database initialization error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
    
# =============================================
# Enhanced User Management Functions
# =============================================

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user by email and return user data if successful"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        # First, check if auth_method column exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'auth_method'
        """)
        auth_method_exists = cursor.fetchone()[0] > 0
        
        if auth_method_exists:
            query = """
                SELECT user_id, username, email, password_hash, role, is_active, auth_method
                FROM users 
                WHERE email = ? AND is_active = 1
            """
        else:
            query = """
                SELECT user_id, username, email, password_hash, role, is_active, 'traditional' as auth_method
                FROM users 
                WHERE email = ? AND is_active = 1
            """
        
        df = pd.read_sql(query, conn, params=(email,))
        
        if df.empty:
            return None
            
        user = df.iloc[0].to_dict()
        
        if PasswordHasher.verify_password(password, user['password_hash']):
            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = GETDATE() WHERE user_id = ?", 
                (user['user_id'],)
            )
            conn.commit()
            cursor.close()
            
            # Remove password hash from returned user data
            del user['password_hash']
            return user
        return None
        
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return None
def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email (for Microsoft auth)"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        query = """
            SELECT user_id, username, email, password_hash, role, is_active, auth_method
            FROM users 
            WHERE email = ? AND is_active = 1
        """
        df = pd.read_sql(query, conn, params=(email,))
        
        if df.empty:
            return None
            
        user = df.iloc[0].to_dict()
        # Remove password hash from returned user data
        del user['password_hash']
        return user
        
    except Exception as e:
        print(f"Error fetching user by email: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def create_user(username: str, email: str, password: str, role: str = 'user', auth_method: str = 'traditional') -> bool:
    """Create a new user with hashed password"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        hashed_password = PasswordHasher.hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, auth_method)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, hashed_password, role, auth_method))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def get_all_users() -> pd.DataFrame:
    """Get all users (without password hashes)"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
            SELECT user_id, username, email, role, auth_method, is_active, created_at, last_login
            FROM users 
            ORDER BY username
        """
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error fetching users: {str(e)}")
        return pd.DataFrame()

def update_user(user_id: int, username: str, email: str, role: str, is_active: bool) -> bool:
    """Update user details"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users 
            SET username = ?, email = ?, role = ?, is_active = ?, updated_at = GETDATE()
            WHERE user_id = ?
        """, (username, email, role, is_active, user_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating user: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def delete_user(user_id: int) -> bool:
    """Delete a user - simple version only handling users table"""
    conn = get_db_connection()
    if conn is None:
        st.error("❌ No database connection")
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # First, check if the user exists
        cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            st.error(f"❌ User with ID {user_id} not found")
            return False
        
        username = user[0]
        
        # Prevent users from deleting themselves
        if user_id == st.session_state.user_id:
            st.error("❌ You cannot delete your own account")
            return False
        
        # Check if user has assigned tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to = ?", (user_id,))
        task_count = cursor.fetchone()[0]
        
        if task_count > 0:
            st.warning(f"⚠️ User '{username}' has {task_count} assigned tasks")
            st.info("Please reassign the tasks to another user or set assigned_to to NULL first")
            return False
        
        # Simply delete the user
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            st.success(f"✅ User '{username}' deleted successfully!")
            return True
        else:
            st.error("❌ Failed to delete user")
            return False
            
    except pyodbc.IntegrityError as e:
        st.error(f"❌ Cannot delete user: There are related records in other tables")
        st.info("Please reassign or delete the user's tasks and comments first")
        return False
    except Exception as e:
        st.error(f"❌ Error deleting user: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()

def get_admin_users():
    """Get all admin users - FIXED: Proper DataFrame structure"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
            SELECT user_id, username, email, role 
            FROM users 
            WHERE role = 'admin' AND is_active = 1
        """
        df = pd.read_sql(query, conn)
        
        # Ensure the DataFrame has the correct structure
        if not df.empty:
            # Make sure we have all required columns
            required_columns = ['user_id', 'username', 'email', 'role']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            return df[required_columns]  # Return only the required columns in correct order
        else:
            return pd.DataFrame(columns=required_columns)
            
    except Exception as e:
        st.error(f"Error fetching admin users: {str(e)}")
        print(f"Detailed error: {e}")
        return pd.DataFrame(columns=['user_id', 'username', 'email', 'role'])

# =============================================
# Enhanced Task Management Functions
# =============================================

def create_task(
    title: str, 
    description: str, 
    domain: str, 
    assigned_to: int, 
    priority: str, 
    due_date: datetime,
    frequency: str = 'One-time',
    attachment: str = '',
    created_by: int = None
) -> bool:
    """Create a new task with empty comments array"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        # Initialize comments as empty JSON array
        initial_comments = json.dumps([])
        
        cursor.execute("""
            INSERT INTO tasks (
                title, description, domain, assigned_to, priority, 
                due_date, frequency, attachment, comments, created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, description, domain, assigned_to, priority, 
              due_date, frequency, attachment, initial_comments, created_by))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error creating task: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def get_tasks(
    user_id: int = None, 
    role: str = 'user', 
    include_closed: bool = True
) -> pd.DataFrame:
    """Get tasks based on user role and filters"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        base_query = """
            SELECT 
                t.task_id, t.title, t.description, t.domain, 
                t.assigned_to, t.attachment, t.status, t.priority,
                t.due_date, t.frequency, t.comments, t.created_at, t.updated_at,
                u.username AS assigned_username, u.email AS assigned_email,
                creator.username AS created_by_username
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.user_id
            LEFT JOIN users creator ON t.created_by = creator.user_id
        """
        
        if role == 'admin':
            if not include_closed:
                query = f"{base_query} WHERE t.status != 'closed' ORDER BY t.priority DESC, t.due_date ASC"
            else:
                query = f"{base_query} ORDER BY t.priority DESC, t.due_date ASC"
            df = pd.read_sql(query, conn)
        else:
            if not include_closed:
                query = f"{base_query} WHERE t.assigned_to = ? AND t.status != 'closed' ORDER BY t.priority DESC, t.due_date ASC"
            else:
                query = f"{base_query} WHERE t.assigned_to = ? ORDER BY t.priority DESC, t.due_date ASC"
            df = pd.read_sql(query, conn, params=(user_id,))
        
        # Parse JSON comments
        if not df.empty and 'comments' in df.columns:
            df['comments'] = df['comments'].apply(lambda x: json.loads(x) if x else [])
        
        return df
    except Exception as e:
        st.error(f"Error fetching tasks: {str(e)}")
        return pd.DataFrame()

def get_tasks_for_microsoft_user(user_email: str, include_closed: bool = True) -> pd.DataFrame:
    """Get tasks assigned to a Microsoft-authenticated user"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
            SELECT 
                t.task_id, t.title, t.description, t.domain, 
                t.assigned_to, t.attachment, t.status, t.priority,
                t.due_date, t.frequency, t.comments, t.created_at, t.updated_at,
                u.username AS assigned_username, u.email AS assigned_email,
                creator.username AS created_by_username
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.user_id
            LEFT JOIN users creator ON t.created_by = creator.user_id
            WHERE u.email = ? 
        """
        
        if not include_closed:
            query += " AND t.status != 'closed'"
        
        query += " ORDER BY t.priority DESC, t.due_date ASC"
        
        df = pd.read_sql(query, conn, params=(user_email,))
        
        # Parse JSON comments
        if not df.empty and 'comments' in df.columns:
            df['comments'] = df['comments'].apply(lambda x: json.loads(x) if x else [])
        
        return df
    except Exception as e:
        st.error(f"Error fetching tasks for Microsoft user: {str(e)}")
        return pd.DataFrame()

def assign_task_to_microsoft_user(task_id: int, assignee_email: str, assigned_by: int) -> bool:
    """Assign task to user by email (for Microsoft users)"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        # Get user_id from email
        cursor.execute("SELECT user_id FROM users WHERE email = ?", (assignee_email,))
        result = cursor.fetchone()
        
        if not result:
            st.error(f"User with email {assignee_email} not found")
            return False
        
        assignee_user_id = result[0]
        
        # Update task assignment
        cursor.execute(
            "UPDATE tasks SET assigned_to = ?, updated_at = GETDATE() WHERE task_id = ?",
            (assignee_user_id, task_id)
        )
        
        # Log in history
        cursor.execute("""
            INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
            VALUES (?, 'assigned_to', ?, ?, ?)
        """, (task_id, 'Previous assignee', assignee_email, assigned_by))
        
        conn.commit()
        st.success(f"Task assigned to {assignee_email}")
        return True
        
    except Exception as e:
        st.error(f"Error assigning task: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def get_task_by_id(task_id: int) -> Optional[Dict]:
    """Get a specific task by ID"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        query = """
            SELECT 
                t.*,
                u.username AS assigned_username, u.email AS assigned_email,
                creator.username AS created_by_username
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.user_id
            LEFT JOIN users creator ON t.created_by = creator.user_id
            WHERE t.task_id = ?
        """
        df = pd.read_sql(query, conn, params=(task_id,))
        
        if df.empty:
            return None
        
        task = df.iloc[0].to_dict()
        
        # Parse comments JSON
        if task.get('comments'):
            task['comments'] = json.loads(task['comments'])
        else:
            task['comments'] = []
            
        return task
    except Exception as e:
        st.error(f"Error fetching task: {str(e)}")
        return None

def update_task_priority(task_id: int, new_priority: str, changed_by: int) -> bool:
    """Update task priority with history tracking"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        # Get old priority
        cursor.execute("SELECT priority FROM tasks WHERE task_id = ?", (task_id,))
        old_priority = cursor.fetchone()[0]
        
        # Update task
        cursor.execute(
            "UPDATE tasks SET priority = ?, updated_at = GETDATE() WHERE task_id = ?",
            (new_priority, task_id)
        )
        
        # Add to history
        cursor.execute("""
            INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
            VALUES (?, 'priority', ?, ?, ?)
        """, (task_id, old_priority, new_priority, changed_by))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating task priority: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def update_task(task_id: int, title: str, description: str, domain: str, assigned_to: int, 
                attachment: str, status: str, due_date: date, frequency: str, 
                priority: str, updated_by: int) -> bool:
    """Update entire task with history tracking"""
    conn = get_db_connection()
    if conn is None:
        st.error("❌ No database connection")
        return False
    
    cursor = conn.cursor()
    try:
        # Get old values for history
        cursor.execute("""
            SELECT title, description, domain, assigned_to, attachment, status, due_date, frequency, priority 
            FROM tasks WHERE task_id = ?
        """, (task_id,))
        old_values = cursor.fetchone()
        
        if old_values:
            old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = old_values
        else:
            # If no old values found, set defaults
            old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = '', '', '', None, '', 'open', None, '', 'medium'

        # Convert due_date to datetime if it's a date object
        if isinstance(due_date, date) and not isinstance(due_date, datetime):
            due_date = datetime.combine(due_date, datetime.min.time())

        # Update task
        cursor.execute("""
            UPDATE tasks
            SET title = ?, description = ?, domain = ?, assigned_to = ?, 
                attachment = ?, status = ?, due_date = ?, frequency = ?, priority = ?, updated_at = GETDATE()
            WHERE task_id = ?
        """, (title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, task_id))
        
        # Add changes to history
        fields_to_check = [
            ('title', old_title, title),
            ('description', old_description, description),
            ('domain', old_domain, domain),
            ('assigned_to', old_assigned_to, assigned_to),
            ('attachment', old_attachment, attachment),
            ('status', old_status, status),
            ('due_date', old_due_date, due_date),
            ('frequency', old_frequency, frequency),
            ('priority', old_priority, priority)
        ]
        
        for field_name, old_val, new_val in fields_to_check:
            if str(old_val) != str(new_val):
                cursor.execute("""
                    INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
                    VALUES (?, ?, ?, ?, ?)
                """, (task_id, field_name, str(old_val), str(new_val), updated_by))
        
        conn.commit()
        st.success("✅ Task updated successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Error updating task: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def delete_task(task_id: int) -> bool:
    """Delete task and its related data"""
    conn = get_db_connection()
    if conn is None:
        st.error("❌ No database connection")
        return False
    
    cursor = conn.cursor()
    try:
        # First, check if task exists and get its title for confirmation
        cursor.execute("SELECT title FROM tasks WHERE task_id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            st.error(f"❌ Task with ID {task_id} not found")
            return False
        
        task_title = task[0]
        
        # Check which tables exist
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        existing_tables = [table[0].lower() for table in cursor.fetchall()]
        
        # Delete from task_history if table exists
        if 'task_history' in existing_tables:
            cursor.execute("DELETE FROM task_history WHERE task_id = ?", (task_id,))
        
        # Delete from comments if table exists
        if 'comments' in existing_tables:
            cursor.execute("DELETE FROM comments WHERE task_id = ?", (task_id,))
        
        # Delete the task
        cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        
        conn.commit()
        st.success(f"✅ Task '{task_title}' deleted successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Error deleting task: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()



# =============================================
# Enhanced Login System
# =============================================

def show_login():
    """Show professional login page with both email/password and Microsoft login"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>🚀</div>
            <h1 style='color: #1a202c; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 800;'>TaskFlow Pro</h1>
            <p style='color: #64748b; font-size: 1.125rem; font-weight: 500; margin-bottom: 3rem;'>Task Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login Tabs
        tab1, tab2 = st.tabs(["🔐 Email/Password", "🏢 Microsoft Login"])
        
        with tab1:
            show_email_password_login()
        
        with tab2:
            show_microsoft_login()

def show_email_password_login():
    """Show traditional email/password login"""
    st.markdown("<h3 style='text-align: center; color: #1a202c; margin-bottom: 0.5rem;'>Email Login</h3>", unsafe_allow_html=True)
    
    email = st.text_input("Email", placeholder="Enter your email address", key="login_email")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Sign In with Email", use_container_width=True, key="email_login_btn"):
            if email and password:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.user_id = user['user_id']
                    st.session_state.user_name = user['username']
                    st.session_state.user_email = user['email']
                    st.session_state.user_role = user['role']
                    st.session_state.auth_method = user.get('auth_method', 'traditional')
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")
            else:
                st.warning("Please enter both email and password")

def show_microsoft_login():
    """Enhanced Microsoft login with better error handling"""
    st.markdown("<h3 style='text-align: center; color: #1a202c; margin-bottom: 0.5rem;'>Microsoft Login</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
    '>
        <div style='font-size: 2rem; margin-bottom: 1rem;'>🏢</div>
        <p style='color: #495057; margin-bottom: 1rem;'>
            Sign in with your Microsoft corporate account for seamless access.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for OAuth callback
    query_params = st.query_params
    
    # Check if we have an authorization code
    if "code" in query_params:
        code = query_params["code"]
        handle_microsoft_callback(code)
        return
    
    # Check for error in callback
    if "error" in query_params:
        error = query_params.get("error", "Unknown error")
        error_description = query_params.get("error_description", "")
        st.error(f"❌ Authentication failed: {error}")
        if error_description:
            st.warning(f"Details: {error_description}")
        
        # Clear error parameters
        if st.button("Try Again"):
            st.query_params.clear()
            st.rerun()
        return
    
    # Show Microsoft login button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            auth_url = ms_auth.get_auth_url()
            
            if auth_url:
                st.markdown(f"""
                <a href="{auth_url}" target="_self" style='
                    display: inline-block;
                    background: linear-gradient(135deg, #2F80ED 0%, #1a5dc7 100%);
                    color: white;
                    padding: 0.875rem 1.75rem;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    text-align: center;
                    width: 100%;
                    border: none;
                    cursor: pointer;
                    box-shadow: 0 4px 6px rgba(47, 128, 237, 0.3);
                    transition: all 0.3s ease;
                '>
                    <span style='font-size: 1.1rem;'>Sign in with Microsoft</span>
                </a>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style='text-align: center; margin-top: 1rem;'>
                    <small style='color: #6c757d;'>
                        You'll be redirected to Microsoft's secure login page
                    </small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ Failed to generate authentication URL")
                st.info("Please use email/password login instead")
                
        except Exception as e:
            st.error(f"❌ Microsoft authentication error: {str(e)}")
            st.info("Please use email/password login instead")

def handle_microsoft_callback(code):
    """Handle Microsoft OAuth callback with improved error handling"""
    try:
        with st.spinner("🔐 Authenticating with Microsoft..."):
            # Exchange code for token
            token_result = ms_auth.get_token_from_code(code)
            
            if not token_result or "access_token" not in token_result:
                st.error("❌ Failed to obtain access token from Microsoft")
                if token_result:
                    error_msg = token_result.get('error_description', 'Unknown error')
                    st.warning(f"Error details: {error_msg}")
                
                # Clear parameters and allow retry
                if st.button("Try Again"):
                    st.query_params.clear()
                    st.rerun()
                return
            
            # Get user information
            user_info = ms_auth.get_user_info(token_result["access_token"])
            
            if not user_info or not user_info.get('email'):
                st.error("❌ Could not retrieve user information from Microsoft")
                if st.button("Try Again"):
                    st.query_params.clear()
                    st.rerun()
                return
            
            microsoft_email = user_info['email']
            microsoft_name = user_info.get('displayName', 'Microsoft User')
            
            # Check if user exists in database
            user = get_user_by_email(microsoft_email)
            
            if user:
                # User exists - log them in
                st.session_state.user_id = user['user_id']
                st.session_state.user_name = user['username']
                st.session_state.user_email = user['email']
                st.session_state.user_role = user['role']
                st.session_state.auth_method = 'microsoft'
                st.session_state.logged_in = True
                
                st.success(f"✅ Welcome back, {user['username']}!")
                
                # Clear URL parameters
                st.query_params.clear()
                st.rerun()
            else:
                # New user - show registration
                st.info(f"👋 Welcome {microsoft_name}! This is your first time signing in.")
                handle_new_microsoft_user(microsoft_email, microsoft_name)
                
    except Exception as e:
        st.error(f"❌ Authentication error: {str(e)}")
        st.info("Please try again or use email/password login")
        
        if st.button("Return to Login"):
            st.query_params.clear()
            st.rerun()

def handle_new_microsoft_user(email, name):
    """Handle new Microsoft user registration"""
    st.write("📝 **Complete Your Registration**")
    
    with st.form("microsoft_user_registration"):
        # Pre-fill username from email
        default_username = email.split('@')[0]
        username = st.text_input(
            "Username *", 
            value=default_username,
            help="Choose a username for the system"
        )
        
        role = st.selectbox(
            "Role *", 
            ["user", "admin"],
            format_func=lambda x: "👑 Administrator" if x == "admin" else "👤 Team Member",
            help="Select your role (contact admin if you need admin access)"
        )
        
        st.markdown("""
        <div style='background: #eff6ff; padding: 0.75rem; border-radius: 6px; margin: 1rem 0;'>
            <small style='color: #1e40af;'>
                ℹ️ Your Microsoft account will be linked to this TaskFlow Pro account.
                You can use Microsoft login for all future sessions.
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("✅ Complete Registration", use_container_width=True)
        
        if submitted:
            if not username:
                st.error("❌ Please enter a username")
                return
            
            # Create user with random password (will use Microsoft login)
            import secrets
            random_password = secrets.token_urlsafe(32)
            
            if create_user(username, email, random_password, role, 'microsoft'):
                st.success("🎉 Registration completed! Logging you in...")
                
                # Get newly created user and log them in
                user = get_user_by_email(email)
                if user:
                    st.session_state.user_id = user['user_id']
                    st.session_state.user_name = user['username']
                    st.session_state.user_email = user['email']
                    st.session_state.user_role = user['role']
                    st.session_state.auth_method = 'microsoft'
                    st.session_state.logged_in = True
                    
                    # Clear URL parameters
                    st.query_params.clear()
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Registration succeeded but login failed. Please try logging in manually.")
            else:
                st.error("❌ Failed to create user account. The username or email might already exist.")
    
    # Cancel button
    if st.button("❌ Cancel Registration", type="secondary"):
        st.query_params.clear()
        st.rerun()

# =============================================
# Enhanced User Dashboard for Microsoft Users
# =============================================

def show_microsoft_user_dashboard():
    """Render dashboard for Microsoft-authenticated users"""
    st.title(f"🎯 Welcome, {st.session_state.user_name}!")
    
    # Show user info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Login Method", "Microsoft")
    with col2:
        st.metric("Role", st.session_state.user_role.title())
    with col3:
        st.metric("Email", st.session_state.user_email)
    
    # Get tasks for this user using email-based lookup
    tasks_df = get_tasks_for_microsoft_user(st.session_state.user_email)
    
    if tasks_df.empty:
        st.info("No tasks assigned to you.")
    else:
        st.subheader("Your Tasks")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Filter by Status", 
                                       ["All", "Open", "In Progress", "Closed"])
        with col2:
            priority_filter = st.selectbox("Filter by Priority", 
                                         ["All", "High", "Medium", "Low"])
        with col3:
            show_closed = st.checkbox("Show Closed Tasks", value=False)
        
        # Apply filters
        filtered_tasks = tasks_df.copy()
        if status_filter != "All":
            filtered_tasks = filtered_tasks[filtered_tasks['status'] == status_filter.lower().replace(' ', '_')]
        if priority_filter != "All":
            filtered_tasks = filtered_tasks[filtered_tasks['priority'] == priority_filter.lower()]
        if not show_closed:
            filtered_tasks = filtered_tasks[filtered_tasks['status'] != 'closed']
        
        # Display tasks
        for _, task in filtered_tasks.iterrows():
            with st.expander(f"📋 {task['title']} - {task['status'].title()}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Description:** {task['description']}")
                    st.write(f"**Domain:** {task['domain']}")
                    st.write(f"**Priority:** {task['priority'].title()}")
                with col2:
                    st.write(f"**Due Date:** {task['due_date'].strftime('%Y-%m-%d') if pd.notna(task['due_date']) else 'Not set'}")
                    st.write(f"**Status:** {task['status'].title()}")
                    
                    # Status update
                    new_status = st.selectbox(
                        "Update Status",
                        ["open", "in_progress", "closed"],
                        index=["open", "in_progress", "closed"].index(task['status']),
                        key=f"status_{task['task_id']}"
                    )
                    
                    if new_status != task['status']:
                        if st.button("Update Status", key=f"update_{task['task_id']}"):
                            if update_task_status(task['task_id'], new_status, st.session_state.user_id):
                                st.success("Status updated!")
                                st.rerun()

# =============================================
# Main Application Entry Point
# =============================================


def show_traditional_dashboard():
    """Show traditional dashboard for email/password users"""
    st.title(f"Welcome, {st.session_state.user_name}!")
    
    # Your existing dashboard code here
    if st.session_state.user_role == 'admin':
        st.write("Admin dashboard content...")
    else:
        st.write("User dashboard content...")

# =============================================
# Additional Enhanced Functions
# =============================================

def send_task_completion_notification(task, user_name, sender_email, sender_password):
    """Send notification to admins when a task is completed - FIXED: Better error handling"""
    try:
        admin_users = get_admin_users()
        
        if admin_users.empty:
            print("No admin users found to send completion notification")
            return False
        
        success_count = 0
        total_admins = len(admin_users)
        
        for _, admin in admin_users.iterrows():
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f'✅ Task Completed: {task.get("title", "Untitled Task")}'
                msg['From'] = sender_email
                msg['To'] = admin.get('email', '')
                
                # Safe data access
                title = task.get('title', 'Untitled Task')
                description = task.get('description', 'No description')
                domain = task.get('domain', 'Unknown')
                frequency = task.get('frequency', 'One-time')
                priority = task.get('priority', 'Medium')
                
                # Safe date handling
                due_date_str = "Not specified"
                if pd.notna(task.get('due_date')):
                    try:
                        due_date_str = task['due_date'].strftime("%Y-%m-%d")
                    except:
                        due_date_str = "Invalid date"
                
                completion_time = datetime.now().strftime("%Y-%m-%d at %I:%M %p")
                
                html = f"""
                <html>
                  <head>
                    <style>
                      body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
                      .container {{ max-width: 700px; margin: 0 auto; padding: 25px; }}
                      .header {{ border-bottom: 3px solid #10b981; padding-bottom: 20px; margin-bottom: 30px; }}
                      .success-box {{ background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 25px; }}
                      .info-box {{ background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 16px; margin-bottom: 25px; }}
                      .task-details {{ width: 100%; border-collapse: collapse; }}
                      .task-details td {{ padding: 8px 0; }}
                    </style>
                  </head>
                  <body>
                    <div class="container">
                      <div class="header">
                        <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 26px; font-weight: 700;">✅ Task Completed Successfully</h1>
                        <p style="color: #64748b; margin: 0; font-size: 16px;">Great news! A task has been marked as completed.</p>
                      </div>
                      
                      <div class="success-box">
                        <h2 style="color: #15803d; margin: 0 0 15px 0; font-size: 20px; font-weight: 600;">Task Details</h2>
                        
                        <table class="task-details">
                          <tr>
                            <td style="color: #475569; font-weight: 600; width: 120px;">Task Title:</td>
                            <td style="color: #1e293b;">{title}</td>
                          </tr>
                          <tr>
                            <td style="color: #475569; font-weight: 600;">Description:</td>
                            <td style="color: #1e293b;">{description}</td>
                          </tr>
                          <tr>
                            <td style="color: #475569; font-weight: 600;">Completed By:</td>
                            <td style="color: #1e293b;">{user_name}</td>
                          </tr>
                          <tr>
                            <td style="color: #475569; font-weight: 600;">Domain:</td>
                            <td style="color: #1e293b;">{domain}</td>
                          </tr>
                          <tr>
                            <td style="color: #475569; font-weight: 600;">Due Date:</td>
                            <td style="color: #1e293b;">{due_date_str}</td>
                          </tr>
                          <tr>
                            <td style="color: #475569; font-weight: 600;">Frequency:</td>
                            <td style="color: #1e293b;">{frequency}</td>
                          </tr>
                          <tr>
                            <td style="color: #475569; font-weight: 600;">Priority:</td>
                            <td style="color: #1e293b;">{priority}</td>
                          </tr>
                          <tr>
                            <td style="color: #475569; font-weight: 600;">Completed On:</td>
                            <td style="color: #15803d; font-weight: 600;">{completion_time}</td>
                          </tr>
                        </table>
                      </div>
                      
                      <div class="info-box">
                        <p style="margin: 0; color: #1e40af; font-size: 14px;">
                          <strong>Note:</strong> This task has been successfully completed and is now ready for your review.
                        </p>
                      </div>
                      
                      <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                        <p style="color: #64748b; margin: 0 0 10px 0; font-size: 14px;">
                          This is an automated notification from TaskFlow Pro System
                        </p>
                        <p style="color: #94a3b8; margin: 0; font-size: 12px;">
                          Please do not reply to this email
                        </p>
                      </div>
                    </div>
                  </body>
                </html>
                """
                
                part = MIMEText(html, 'html')
                msg.attach(part)
                
                # Send email
                with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
                    server.starttls()  # Enable TLS
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                
                success_count += 1
                print(f"✅ Completion notification sent to {admin.get('email')}")
                
            except Exception as e:
                print(f"❌ Failed to send completion notification to {admin.get('email', 'Unknown')}: {str(e)}")
        
        print(f"📧 Completion notifications: {success_count}/{total_admins} successful")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error in send_task_completion_notification: {str(e)}")
        return False

def update_task_status(task_id: int, new_status: str, changed_by: int) -> bool:
    """Update task status with history tracking"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        # Get old status
        cursor.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,))
        old_status = cursor.fetchone()[0]
        
        # Update task
        cursor.execute(
            "UPDATE tasks SET status = ?, updated_at = GETDATE() WHERE task_id = ?",
            (new_status, task_id)
        )
        
        # Add to history
        cursor.execute("""
            INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
            VALUES (?, 'status', ?, ?, ?)
        """, (task_id, old_status, new_status, changed_by))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating task status: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def get_domains() -> pd.DataFrame:
    """Get all active domains"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
            SELECT domain_id, domain_name, mancom_member_name, mancom_member_email
            FROM domains 
            WHERE is_active = 1
            ORDER BY domain_name
        """
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error fetching domains: {str(e)}")
        return pd.DataFrame()

def add_task_comment(task_id: int, user_id: int, comment_text: str) -> bool:
    """Add a comment to a task"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        # Get current comments
        cursor.execute("SELECT comments FROM tasks WHERE task_id = ?", (task_id,))
        result = cursor.fetchone()
        
        current_comments = []
        if result and result[0]:
            current_comments = json.loads(result[0])
        
        # Add new comment
        new_comment = {
            'id': len(current_comments) + 1,
            'user_id': user_id,
            'username': st.session_state.user_name,  # From session state
            'comment': comment_text,
            'timestamp': datetime.now().isoformat()
        }
        
        current_comments.append(new_comment)
        
        # Update task with new comments
        cursor.execute(
            "UPDATE tasks SET comments = ?, updated_at = GETDATE() WHERE task_id = ?",
            (json.dumps(current_comments), task_id)
        )
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding comment: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def delete_domain(domain_id: int) -> bool:
    """Delete a domain from the database"""
    conn = get_db_connection()
    if conn is None:
        st.error("❌ No database connection")
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # First, check if the domain exists
        cursor.execute("SELECT domain_name FROM domains WHERE domain_id = ?", (domain_id,))
        domain = cursor.fetchone()
        
        if not domain:
            st.error(f"❌ Domain with ID {domain_id} not found")
            return False
        
        domain_name = domain[0]
        
        # Check if there are tasks associated with this domain
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE domain = ?", (domain_name,))
        task_count = cursor.fetchone()[0]
        
        if task_count > 0:
            st.warning(f"⚠️ Cannot delete domain '{domain_name}' - it has {task_count} associated tasks")
            st.info("Please reassign or delete the tasks first, or update the domain name instead of deleting")
            return False
        
        # Perform the deletion
        cursor.execute("DELETE FROM domains WHERE domain_id = ?", (domain_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            st.success(f"✅ Domain '{domain_name}' deleted successfully!")
            return True
        else:
            st.error("❌ Failed to delete domain")
            return False
            
    except Exception as e:
        st.error(f"❌ Error deleting domain: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
          cursor.close()

def get_task_history(task_id):
    """Get history of changes for a task"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT th.field_name, th.old_value, th.new_value, th.changed_at, u.username as changed_by_name
        FROM task_history th
        LEFT JOIN users u ON th.changed_by = u.user_id
        WHERE th.task_id = ?
        ORDER BY th.changed_at DESC
        """
        df = pd.read_sql(query, conn, params=(task_id,))
        return df
    except Exception as e:
        st.error(f"Error fetching task history: {str(e)}")
        return pd.DataFrame()
    
def get_task_by_id(task_id: int) -> Optional[Dict]:
    """Get a specific task by ID"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        query = """
            SELECT 
                t.*,
                u.username AS assigned_username, u.email AS assigned_email,
                creator.username AS created_by_username
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.user_id
            LEFT JOIN users creator ON t.created_by = creator.user_id
            WHERE t.task_id = ?
        """
        df = pd.read_sql(query, conn, params=(task_id,))
        
        if df.empty:
            return None
        
        task = df.iloc[0].to_dict()
        
        # Parse comments JSON
        if task.get('comments'):
            task['comments'] = json.loads(task['comments'])
        else:
            task['comments'] = []
            
        return task
    except Exception as e:
        st.error(f"Error fetching task: {str(e)}")
        return None

def update_domain(domain_id, domain_name, mancom_member_name, mancom_member_email):
    """Update domain details"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE domains
            SET domain_name = ?, mancom_member_name = ?, mancom_member_email = ?
            WHERE domain_id = ?
        """, (domain_name, mancom_member_name, mancom_member_email, domain_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating domain: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close() 

def add_domain(domain_name: str, mancom_member_name: str, mancom_member_email: str) -> bool:
    """Add a new domain to the database"""
    conn = get_db_connection()
    if conn is None:
        st.error("❌ No database connection")
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Check if domain already exists
        cursor.execute("SELECT domain_id FROM domains WHERE domain_name = ?", (domain_name,))
        if cursor.fetchone():
            st.error(f"❌ Domain '{domain_name}' already exists")
            return False
        
        # Check if is_active column exists
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'domains' AND COLUMN_NAME = 'is_active'
        """)
        has_is_active = cursor.fetchone()[0] > 0
        
        # Insert new domain
        if has_is_active:
            cursor.execute("""
                INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email, is_active)
                VALUES (?, ?, ?, 1)
            """, (domain_name, mancom_member_name, mancom_member_email))
        else:
            cursor.execute("""
                INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
                VALUES (?, ?, ?)
            """, (domain_name, mancom_member_name, mancom_member_email))
        
        conn.commit()
        st.success(f"✅ Domain '{domain_name}' added successfully!")
        return True
        
    except Exception as e:
        st.error(f"❌ Error adding domain: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()

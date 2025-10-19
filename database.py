
# import pyodbc
# import streamlit as st
# import pandas as pd
# from datetime import datetime, date, timedelta
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import smtplib
# import os

# # ✅ MSSQL Connection with proper error handling
# @st.cache_resource
# def get_db_connection():
#     """
#     Creates a MSSQL connection using Streamlit secrets or local config.
#     Connection is cached to avoid multiple connections.
#     """
#     try:
#         conn = pyodbc.connect(
#             "DRIVER={ODBC Driver 17 for SQL Server};"
#             "SERVER=localhost,1433;"
#             "DATABASE=task_management_db;"
#             "UID=sa;"
#             "PWD=Yashal309;"
#         )
#         return conn
#     except Exception as e:
#         st.error(f"Failed to connect to SQL Server: {str(e)}")
#         return None

# def init_database():
#     """Initialize database schema and default data"""
#     conn = get_db_connection()
#     if conn is None:
#         st.error("❌ Cannot initialize database - no connection")
#         return
    
#     cursor = None
#     try:
#         cursor = conn.cursor()
        
#         # Create users table
#         cursor.execute("""
#             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
#             CREATE TABLE users (
#                 user_id INT PRIMARY KEY IDENTITY(1,1),
#                 name NVARCHAR(100) NOT NULL,
#                 email NVARCHAR(100) UNIQUE NOT NULL,
#                 role NVARCHAR(20) NOT NULL,
#                 created_at DATETIME DEFAULT GETDATE()
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
#                 created_at DATETIME DEFAULT GETDATE()
#             )
#         """)
        
#         # Create tasks table with enhanced fields
#         cursor.execute("""
#             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
#             CREATE TABLE tasks (
#                 task_id INT PRIMARY KEY IDENTITY(1,1),
#                 title NVARCHAR(255) NOT NULL,
#                 description NVARCHAR(MAX),
#                 domain NVARCHAR(100),
#                 assigned_to INT,
#                 attachment NVARCHAR(MAX),
#                 status NVARCHAR(50) DEFAULT 'Open',
#                 due_date DATETIME,
#                 frequency NVARCHAR(50),
#                 priority NVARCHAR(20) DEFAULT 'Medium',
#                 created_by INT,
#                 created_at DATETIME DEFAULT GETDATE(),
#                 updated_at DATETIME DEFAULT GETDATE(),
#                 FOREIGN KEY (assigned_to) REFERENCES users(user_id)
#             )
#         """)
        
#         # Check and add missing columns
#         missing_columns = [
#             ('tasks', 'priority', 'ALTER TABLE tasks ADD priority NVARCHAR(20) DEFAULT ''Medium'''),
#             ('tasks', 'created_by', 'ALTER TABLE tasks ADD created_by INT'),
#             ('tasks', 'updated_at', 'ALTER TABLE tasks ADD updated_at DATETIME DEFAULT GETDATE()')
#         ]
        
#         for table, column, alter_stmt in missing_columns:
#             try:
#                 cursor.execute(f"""
#                     IF NOT EXISTS (SELECT * FROM sys.columns 
#                                   WHERE object_id = OBJECT_ID('{table}') AND name = '{column}')
#                     BEGIN
#                         {alter_stmt}
#                     END
#                 """)
#                 print(f"✅ Checked/added column {table}.{column}")
#             except Exception as e:
#                 print(f"⚠️ Error with column {table}.{column}: {e}")
        
#         # Create comments table
#         cursor.execute("""
#             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='comments' AND xtype='U')
#             CREATE TABLE comments (
#                 comment_id INT PRIMARY KEY IDENTITY(1,1),
#                 task_id INT NOT NULL,
#                 user_id INT NOT NULL,
#                 comment_text NVARCHAR(MAX),
#                 created_at DATETIME DEFAULT GETDATE(),
#                 FOREIGN KEY (task_id) REFERENCES tasks(task_id),
#                 FOREIGN KEY (user_id) REFERENCES users(user_id)
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
#                 changed_at DATETIME DEFAULT GETDATE(),
#                 FOREIGN KEY (task_id) REFERENCES tasks(task_id)
#             )
#         """)
        
#         # Create indexes for better performance
#         cursor.execute("""
#             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_email' AND object_id=OBJECT_ID('users'))
#             CREATE INDEX idx_email ON users(email)
#         """)
#         cursor.execute("""
#             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_assigned_to' AND object_id=OBJECT_ID('tasks'))
#             CREATE INDEX idx_assigned_to ON tasks(assigned_to)
#         """)
#         cursor.execute("""
#             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_task_status' AND object_id=OBJECT_ID('tasks'))
#             CREATE INDEX idx_task_status ON tasks(status)
#         """)
#         cursor.execute("""
#             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_due_date' AND object_id=OBJECT_ID('tasks'))
#             CREATE INDEX idx_due_date ON tasks(due_date)
#         """)
        
#         conn.commit()
#         print("✅ Database schema updated successfully!")
        
#         # Insert default users - with existence check
#         default_users = [
#             ('Admin User', 'admin@nfoods.com', 'admin'),
#             ('Yashal Ali', 'yashal.ali@nfoods.com', 'admin'),
#             ('Ali', 'aliyashal309@gmail.com', 'user'),
#         ]
        
#         for name, email, role in default_users:
#             try:
#                 # Check if user already exists
#                 cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
#                 if cursor.fetchone()[0] == 0:
#                     cursor.execute("""
#                         INSERT INTO users (name, email, role)
#                         VALUES (?, ?, ?)
#                     """, (name, email, role))
#                     print(f"✅ Added user: {name} ({email})")
#                 else:
#                     print(f"ℹ️ User already exists: {name} ({email})")
#             except Exception as e:
#                 print(f"⚠️ User {email} already exists or error: {e}")
        
#         # Insert default domains with mancom members - with existence check
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
#                 # Check if domain already exists
#                 cursor.execute("SELECT COUNT(*) FROM domains WHERE domain_name = ?", (domain_name,))
#                 if cursor.fetchone()[0] == 0:
#                     cursor.execute("""
#                         INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
#                         VALUES (?, ?, ?)
#                     """, (domain_name, mancom_name, mancom_email))
#                     print(f"✅ Added domain: {domain_name}")
#                 else:
#                     print(f"ℹ️ Domain already exists: {domain_name}")
#             except Exception as e:
#                 print(f"⚠️ Domain {domain_name} already exists or error: {e}")
        
#         conn.commit()
#         print("✅ Database initialized successfully!")
        
#     except Exception as e:
#         st.error(f"Error initializing database: {str(e)}")
#         print(f"Database initialization error: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         # Only close cursor, not connection (connection is managed by streamlit cache)
#         if cursor:
#             cursor.close()
#         # Don't close the connection here - it's cached by streamlit

# # ✅ Helper Functions with proper connection handling
# def get_user_by_email(email):
#     """Get user by email address"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         query = "SELECT user_id, name, email, role FROM users WHERE email = ?"
#         df = pd.read_sql(query, conn, params=(email,))
#         if df.empty:
#             return None
#         return df.iloc[0].to_dict()
#     except Exception as e:
#         st.error(f"Error fetching user: {str(e)}")
#         return None
#     # Don't close connection - it's cached

# def get_all_users():
#     """Get all users as DataFrame"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = "SELECT user_id, name, email, role FROM users ORDER BY name"
#         df = pd.read_sql(query, conn)
#         return df
#     except Exception as e:
#         st.error(f"Error fetching users: {str(e)}")
#         return pd.DataFrame()

# def get_admin_users():
#     """Get all admin users"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = "SELECT user_id, name, email, role FROM users WHERE role = 'admin'"
#         df = pd.read_sql(query, conn)
#         return df
#     except Exception as e:
#         st.error(f"Error fetching admin users: {str(e)}")
#         return pd.DataFrame()

# def get_domains():
#     """Get all domains with mancom members"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = "SELECT domain_id, domain_name, mancom_member_name, mancom_member_email FROM domains ORDER BY domain_name"
#         df = pd.read_sql(query, conn)
#         return df
#     except Exception as e:
#         st.error(f"Error fetching domains: {str(e)}")
#         return pd.DataFrame()

# def get_mancom_member_by_domain(domain_name):
#     """Get mancom member for a specific domain"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         query = "SELECT mancom_member_name, mancom_member_email FROM domains WHERE domain_name = ?"
#         df = pd.read_sql(query, conn, params=(domain_name,))
#         if df.empty:
#             return None
#         return df.iloc[0].to_dict()
#     except Exception as e:
#         st.error(f"Error fetching mancom member: {str(e)}")
#         return None

# def create_task(title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, created_by):
#     """Create a new task with safe column handling"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     if isinstance(due_date, date) and not isinstance(due_date, datetime):
#         due_date = datetime.combine(due_date, datetime.min.time())
    
#     cursor = conn.cursor()
#     try:
#         # Check which columns exist
#         cursor.execute("""
#             SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
#             WHERE TABLE_NAME = 'tasks'
#         """)
#         existing_columns = [row[0] for row in cursor.fetchall()]
        
#         # Build dynamic INSERT statement based on available columns
#         columns = ['title', 'description', 'domain', 'assigned_to', 'attachment', 'status', 'due_date', 'frequency', 'priority']
#         placeholders = ['?'] * len(columns)
        
#         # Add created_by if column exists
#         if 'created_by' in existing_columns:
#             columns.append('created_by')
#             placeholders.append('?')
        
#         # Add updated_at if column exists
#         if 'updated_at' in existing_columns:
#             columns.append('updated_at')
#             placeholders.append('GETDATE()')
        
#         # Add created_at if column exists
#         if 'created_at' in existing_columns:
#             columns.append('created_at')
#             placeholders.append('GETDATE()')
        
#         columns_str = ', '.join(columns)
#         placeholders_str = ', '.join(placeholders)
        
#         # Prepare values
#         values = [title, description, domain, assigned_to, attachment, status, due_date, frequency, priority]
#         if 'created_by' in existing_columns:
#             values.append(created_by)
        
#         query = f"INSERT INTO tasks ({columns_str}) VALUES ({placeholders_str})"
#         cursor.execute(query, values)
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error creating task: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def get_tasks(user_id=None, role='user', include_completed=True):
#     """Get tasks with user info and comment counts - FIXED QUERY"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         # First check if priority column exists
#         cursor = conn.cursor()
#         cursor.execute("""
#             SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
#             WHERE TABLE_NAME = 'tasks' AND COLUMN_NAME = 'priority'
#         """)
#         has_priority = cursor.fetchone()[0] > 0
#         cursor.close()
        
#         # Build query based on available columns
#         if has_priority:
#             base_query = """
#             SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                    (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             """
#             order_by = "ORDER BY t.due_date ASC, t.priority DESC"
#         else:
#             base_query = """
#             SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                    (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             """
#             order_by = "ORDER BY t.due_date ASC"
        
#         if role == 'admin':
#             if include_completed:
#                 query = f"{base_query} {order_by}"
#                 df = pd.read_sql(query, conn)
#             else:
#                 query = f"{base_query} WHERE t.status != 'Completed' {order_by}"
#                 df = pd.read_sql(query, conn)
#         else:
#             if include_completed:
#                 query = f"{base_query} WHERE t.assigned_to = ? {order_by}"
#                 df = pd.read_sql(query, conn, params=(user_id,))
#             else:
#                 query = f"{base_query} WHERE t.assigned_to = ? AND t.status != 'Completed' {order_by}"
#                 df = pd.read_sql(query, conn, params=(user_id,))
        
#         # Ensure status column exists and has proper values
#         if 'status' not in df.columns:
#             df['status'] = 'Open'
#         else:
#             df['status'] = df['status'].fillna('Open')
            
#         # Ensure priority column exists
#         if 'priority' not in df.columns:
#             df['priority'] = 'Medium'
            
#         # Ensure due_date is properly formatted as datetime
#         if 'due_date' in df.columns:
#             df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
        
#         return df
#     except Exception as e:
#         st.error(f"Error fetching tasks: {str(e)}")
#         return pd.DataFrame()

# def get_task_by_id(task_id):
#     """Get a specific task by ID with safe column handling"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         # Check if created_by column exists
#         cursor = conn.cursor()
#         cursor.execute("""
#             SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
#             WHERE TABLE_NAME = 'tasks' AND COLUMN_NAME = 'created_by'
#         """)
#         has_created_by = cursor.fetchone()[0] > 0
#         cursor.close()
        
#         # Build query based on available columns
#         if has_created_by:
#             query = """
#             SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                    creator.name AS created_by_name
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             LEFT JOIN users creator ON t.created_by = creator.user_id
#             WHERE t.task_id = ?
#             """
#         else:
#             query = """
#             SELECT t.*, u.name AS assigned_name, u.email AS assigned_email
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             WHERE t.task_id = ?
#             """
        
#         df = pd.read_sql(query, conn, params=(task_id,))
#         if df.empty:
#             return None
        
#         task = df.iloc[0].to_dict()
#         # Ensure all required fields exist
#         if 'status' not in task or not task['status']:
#             task['status'] = 'Open'
#         if 'priority' not in task or not task['priority']:
#             task['priority'] = 'Medium'
#         if 'created_by_name' not in task:
#             task['created_by_name'] = 'Unknown'
            
#         return task
#     except Exception as e:
#         st.error(f"Error fetching task: {str(e)}")
#         return None

# def update_task_status(task_id, status, changed_by=None):
#     """Update task status with proper column handling"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Get old status for history
#         cursor.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,))
#         result = cursor.fetchone()
#         old_status = result[0] if result else 'Open'
        
#         # Check if updated_at column exists
#         cursor.execute("""
#             SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
#             WHERE TABLE_NAME = 'tasks' AND COLUMN_NAME = 'updated_at'
#         """)
#         has_updated_at = cursor.fetchone()[0] > 0
        
#         # Update task - with or without updated_at column
#         if has_updated_at:
#             cursor.execute("""
#                 UPDATE tasks
#                 SET status = ?, updated_at = GETDATE()
#                 WHERE task_id = ?
#             """, (status, task_id))
#         else:
#             cursor.execute("""
#                 UPDATE tasks
#                 SET status = ?
#                 WHERE task_id = ?
#             """, (status, task_id))
        
#         # Add to history if changed_by provided
#         if changed_by:
#             # Check if task_history table exists
#             cursor.execute("""
#                 SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
#                 WHERE TABLE_NAME = 'task_history'
#             """)
#             has_history_table = cursor.fetchone()[0] > 0
            
#             if has_history_table:
#                 cursor.execute("""
#                     INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
#                     VALUES (?, 'status', ?, ?, ?)
#                 """, (task_id, old_status, status, changed_by))
        
#         conn.commit()
        
#         # Send notification if task was completed
#         sender_email = os.environ.get("SMTP_USERNAME")
#         sender_password = os.environ.get("SMTP_PASSWORD")
#         if status == 'Completed' and old_status != 'Completed':
#             task = get_task_by_id(task_id)
#             if task and sender_email and sender_password:
#                 # Send completion notification to admins
#                 send_task_completion_notification(task, st.session_state.user_name, sender_email, sender_password)
        
#         return True
#     except Exception as e:
#         st.error(f"Error updating task status: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def update_task(task_id, title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, updated_by):
#     """Update entire task"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Get old values for history
#         cursor.execute("SELECT title, description, domain, assigned_to, attachment, status, due_date, frequency, priority FROM tasks WHERE task_id = ?", (task_id,))
#         old_values = cursor.fetchone()
        
#         if old_values:
#             old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = old_values
#         else:
#             # If no old values found, set defaults
#             old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = '', '', '', None, '', 'Open', None, '', 'Medium'

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
#         return True
#     except Exception as e:
#         st.error(f"Error updating task: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def delete_task(task_id):
#     """Delete task and its comments"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Delete all comments for this task
#         cursor.execute("DELETE FROM comments WHERE task_id = ?", (task_id,))
        
#         # Delete task history
#         cursor.execute("DELETE FROM task_history WHERE task_id = ?", (task_id,))
        
#         # Delete the task
#         cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error deleting task: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def get_comments(task_id):
#     """Get all comments for a task"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#         SELECT c.comment_id, c.task_id, c.user_id, c.comment_text, c.created_at,
#                u.name, u.email
#         FROM comments c
#         LEFT JOIN users u ON c.user_id = u.user_id
#         WHERE c.task_id = ?
#         ORDER BY c.created_at ASC
#         """
#         df = pd.read_sql(query, conn, params=(task_id,))
#         return df
#     except Exception as e:
#         st.error(f"Error fetching comments: {str(e)}")
#         return pd.DataFrame()

# def add_comment(task_id, user_id, comment_text):
#     """Add a comment to a task"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             INSERT INTO comments (task_id, user_id, comment_text, created_at)
#             VALUES (?, ?, ?, ?)
#         """, (task_id, user_id, comment_text, datetime.now()))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error adding comment: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def add_user(name, email, role='user'):
#     """Add a new user"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             INSERT INTO users (name, email, role)
#             VALUES (?, ?, ?)
#         """, (name, email, role))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error adding user: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def update_user(user_id, name, email, role):
#     """Update user details"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             UPDATE users
#             SET name = ?, email = ?, role = ?
#             WHERE user_id = ?
#         """, (name, email, role, user_id))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error updating user: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def delete_user(user_id):
#     """Delete a user"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # First, update tasks assigned to this user to NULL
#         cursor.execute("UPDATE tasks SET assigned_to = NULL WHERE assigned_to = ?", (user_id,))
        
#         # Delete user's comments
#         cursor.execute("DELETE FROM comments WHERE user_id = ?", (user_id,))
        
#         # Delete the user
#         cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error deleting user: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def add_domain(domain_name, mancom_member_name, mancom_member_email):
#     """Add a new domain"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
#             VALUES (?, ?, ?)
#         """, (domain_name, mancom_member_name, mancom_member_email))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error adding domain: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

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

# def delete_domain(domain_id):
#     """Delete a domain"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("DELETE FROM domains WHERE domain_id = ?", (domain_id,))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error deleting domain: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def get_overdue_tasks():
#     """Get tasks that are overdue"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#         SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#         FROM tasks t
#         LEFT JOIN users u ON t.assigned_to = u.user_id
#         WHERE t.due_date < GETDATE() AND t.status IN ('Open', 'In Progress')
#         ORDER BY t.due_date ASC
#         """
#         df = pd.read_sql(query, conn)
        
#         # Ensure status column exists
#         if 'status' not in df.columns:
#             df['status'] = 'Open'
            
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
#         SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#         FROM tasks t
#         LEFT JOIN users u ON t.assigned_to = u.user_id
#         WHERE t.due_date BETWEEN GETDATE() AND DATEADD(day, ?, GETDATE()) 
#           AND t.status IN ('Open', 'In Progress')
#         ORDER BY t.due_date ASC
#         """
#         df = pd.read_sql(query, conn, params=(days,))
        
#         # Ensure status column exists
#         if 'status' not in df.columns:
#             df['status'] = 'Open'
            
#         return df
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
#         SELECT th.field_name, th.old_value, th.new_value, th.changed_at, u.name as changed_by_name
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

# # Email functions
# def send_email_summary(user_email, user_name, tasks_df, sender_email, sender_password):
#     """Send email summary of pending tasks"""
#     try:
#         msg = MIMEMultipart('alternative')
#         msg['Subject'] = f'TaskFlow Pro - Pending Tasks Summary – {datetime.now().strftime("%B %Y")}'
#         msg['From'] = sender_email
#         msg['To'] = user_email

#         html = f"""
#         <html>
#           <head>
#             <style>
#               body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
#               .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
#               .header {{ border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; }}
#               .task-table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
#               .task-table th {{ background-color: #2563eb; color: white; padding: 12px 8px; text-align: left; }}
#               .task-table td {{ padding: 12px 8px; border-bottom: 1px solid #e2e8f0; }}
#               .priority-high {{ color: #dc2626; font-weight: bold; }}
#               .priority-medium {{ color: #f59e0b; font-weight: bold; }}
#               .priority-low {{ color: #10b981; font-weight: bold; }}
#               .status-open {{ color: #f59e0b; }}
#               .status-inprogress {{ color: #2563eb; }}
#               .status-completed {{ color: #10b981; }}
#               .info-box {{ background-color: #f8fafc; border-left: 3px solid #2563eb; padding: 16px; margin: 25px 0; }}
#             </style>
#           </head>
#           <body>
#             <div class="container">
#               <div class="header">
#                 <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 28px; font-weight: 700;">Task Summary Report</h1>
#                 <p style="color: #64748b; margin: 0; font-size: 16px;">Hello {user_name},</p>
#               </div>
#               <p style="color: #475569; font-size: 15px; margin-bottom: 25px;">Here are your pending tasks that require attention:</p>
              
#               <table class="task-table">
#                 <thead>
#                   <tr>
#                     <th>Task</th>
#                     <th>Domain</th>
#                     <th>Priority</th>
#                     <th>Due Date</th>
#                     <th>Status</th>
#                     <th style="text-align: center;">Comments</th>
#                   </tr>
#                 </thead>
#                 <tbody>
#         """

#         for _, task in tasks_df.iterrows():
#             # Safe data access with defaults
#             title = task.get('title', 'Untitled Task')
#             description = str(task.get('description', 'No description'))[:80] + '...' if task.get('description') else 'No description'
#             domain = task.get('domain', 'No domain')
#             priority = task.get('priority', 'Medium')
#             status = task.get('status', 'Open')
            
#             # Safe date formatting
#             due_date_str = "N/A"
#             if pd.notna(task.get('due_date')):
#                 try:
#                     due_date_str = task['due_date'].strftime("%Y-%m-%d")
#                 except:
#                     due_date_str = "Invalid date"
            
#             # Safe priority class
#             priority_lower = str(priority).lower() if priority else 'medium'
#             priority_class = f"priority-{priority_lower}"
            
#             # Safe status class
#             status_lower = str(status).lower().replace(' ', '') if status else 'open'
#             status_class = f"status-{status_lower}"
            
#             comment_count = task.get('comment_count', 0)

#             html += f"""
#                   <tr>
#                     <td><b>{title}</b><br><span style="color:#64748b; font-size: 12px;">{description}</span></td>
#                     <td>{domain}</td>
#                     <td><span class="{priority_class}">{priority}</span></td>
#                     <td>{due_date_str}</td>
#                     <td><span class="{status_class}">{status}</span></td>
#                     <td style="text-align:center; color:#2563eb; font-weight: bold;">{comment_count}</td>
#                   </tr>
#             """

#         html += """
#                 </tbody>
#               </table>
              
#               <div class="info-box">
#                 <p style="margin:0; font-weight: 500;">Please update task statuses and provide updates as you make progress.</p>
#               </div>
              
#               <div style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:10px; color:#64748b; font-size:13px;">
#                 <p>Best regards,</p>
#                 <p style="font-weight:600; color:#475569;">TaskFlow Pro Administration</p>
#                 <p style="font-size:12px; color:#94a3b8;">This is an automated email. Please do not reply directly to this message.</p>
#               </div>
#             </div>
#           </body>
#         </html>
#         """

#         part = MIMEText(html, 'html')
#         msg.attach(part)

#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#             server.login(sender_email, sender_password)
#             server.send_message(msg)

#         return True

#     except Exception as e:
#         st.error(f"Error sending email to {user_email}: {str(e)}")
#         return False

# def send_escalation_email(task, sender_email, sender_password):
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
#         assigned_name = task.get('assigned_name', 'Unassigned')
#         domain = task.get('domain', 'Unknown')
#         status = task.get('status', 'Open')
#         priority = task.get('priority', 'Medium')
        
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
        
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#             server.login(sender_email, sender_password)
#             server.send_message(msg)
        
#         return True
        
#     except Exception as e:
#         st.error(f"Error sending escalation email: {str(e)}")
#         return False

# def send_task_completion_notification(task, user_name, sender_email, sender_password):
#     """Send notification to admins when a task is completed"""
#     try:
#         admin_users = get_admin_users()
        
#         if admin_users.empty:
#             st.error("No admin users found to send notification")
#             return False
        
#         success_count = 0
        
#         for _, admin in admin_users.iterrows():
#             msg = MIMEMultipart('alternative')
#             msg['Subject'] = f'✅ Task Completed: {task.get("title", "Untitled Task")}'
#             msg['From'] = sender_email
#             msg['To'] = admin.get('email', '')
            
#             # Safe data access
#             title = task.get('title', 'Untitled Task')
#             description = task.get('description', 'No description')
#             domain = task.get('domain', 'Unknown')
#             frequency = task.get('frequency', 'One-time')
#             priority = task.get('priority', 'Medium')
            
#             # Safe date handling
#             due_date_str = "Not specified"
#             if pd.notna(task.get('due_date')):
#                 try:
#                     due_date_str = task['due_date'].strftime("%Y-%m-%d")
#                 except:
#                     due_date_str = "Invalid date"
            
#             completion_time = datetime.now().strftime("%Y-%m-%d at %I:%M %p")
            
#             html = f"""
#             <html>
#               <head>
#                 <style>
#                   body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
#                   .container {{ max-width: 700px; margin: 0 auto; padding: 25px; }}
#                   .header {{ border-bottom: 3px solid #10b981; padding-bottom: 20px; margin-bottom: 30px; }}
#                   .success-box {{ background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 25px; }}
#                   .info-box {{ background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 16px; margin-bottom: 25px; }}
#                   .task-details {{ width: 100%; border-collapse: collapse; }}
#                   .task-details td {{ padding: 8px 0; }}
#                 </style>
#               </head>
#               <body>
#                 <div class="container">
#                   <div class="header">
#                     <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 26px; font-weight: 700;">✅ Task Completed Successfully</h1>
#                     <p style="color: #64748b; margin: 0; font-size: 16px;">Great news! A task has been marked as completed.</p>
#                   </div>
                  
#                   <div class="success-box">
#                     <h2 style="color: #15803d; margin: 0 0 15px 0; font-size: 20px; font-weight: 600;">Task Details</h2>
                    
#                     <table class="task-details">
#                       <tr>
#                         <td style="color: #475569; font-weight: 600; width: 120px;">Task Title:</td>
#                         <td style="color: #1e293b;">{title}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Description:</td>
#                         <td style="color: #1e293b;">{description}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Completed By:</td>
#                         <td style="color: #1e293b;">{user_name}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Domain:</td>
#                         <td style="color: #1e293b;">{domain}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Due Date:</td>
#                         <td style="color: #1e293b;">{due_date_str}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Frequency:</td>
#                         <td style="color: #1e293b;">{frequency}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Priority:</td>
#                         <td style="color: #1e293b;">{priority}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Completed On:</td>
#                         <td style="color: #15803d; font-weight: 600;">{completion_time}</td>
#                       </tr>
#                     </table>
#                   </div>
                  
#                   <div class="info-box">
#                     <p style="margin: 0; color: #1e40af; font-size: 14px;">
#                       <strong>Note:</strong> This task has been successfully completed and is now ready for your review.
#                     </p>
#                   </div>
                  
#                   <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
#                     <p style="color: #64748b; margin: 0 0 10px 0; font-size: 14px;">
#                       This is an automated notification from TaskFlow Pro System
#                     </p>
#                     <p style="color: #94a3b8; margin: 0; font-size: 12px;">
#                       Please do not reply to this email
#                     </p>
#                   </div>
#                 </div>
#               </body>
#             </html>
#             """
            
#             part = MIMEText(html, 'html')
#             msg.attach(part)
            
#             try:
#                 with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#                     server.login(sender_email, sender_password)
#                     server.send_message(msg)
#                 success_count += 1
#             except Exception as e:
#                 st.error(f"Error sending completion notification to {admin.get('email', 'Unknown')}: {str(e)}")
        
#         return success_count > 0
        
#     except Exception as e:
#         st.error(f"Error sending task completion notifications: {str(e)}")

    
#     """Send notification to admins when a task is completed"""
#     try:
#         admin_users = get_admin_users()
        
#         if admin_users.empty:
#             st.error("No admin users found to send notification")
#             return False
        
#         success_count = 0
        
#         for _, admin in admin_users.iterrows():
#             msg = MIMEMultipart('alternative')
#             msg['Subject'] = f'✅ Task Completed: {task["title"]}'
#             msg['From'] = sender_email
#             msg['To'] = admin['email']
            
#             due_date_str = task['due_date'].strftime("%Y-%m-%d") if pd.notna(task['due_date']) else "Not specified"
#             completion_time = datetime.now().strftime("%Y-%m-%d at %I:%M %p")
            
#             html = f"""
#             <html>
#               <head>
#                 <style>
#                   body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
#                   .container {{ max-width: 700px; margin: 0 auto; padding: 25px; }}
#                   .header {{ border-bottom: 3px solid #10b981; padding-bottom: 20px; margin-bottom: 30px; }}
#                   .success-box {{ background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 25px; }}
#                   .info-box {{ background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 16px; margin-bottom: 25px; }}
#                   .task-details {{ width: 100%; border-collapse: collapse; }}
#                   .task-details td {{ padding: 8px 0; }}
#                 </style>
#               </head>
#               <body>
#                 <div class="container">
#                   <div class="header">
#                     <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 26px; font-weight: 700;">✅ Task Completed Successfully</h1>
#                     <p style="color: #64748b; margin: 0; font-size: 16px;">Great news! A task has been marked as completed.</p>
#                   </div>
                  
#                   <div class="success-box">
#                     <h2 style="color: #15803d; margin: 0 0 15px 0; font-size: 20px; font-weight: 600;">Task Details</h2>
                    
#                     <table class="task-details">
#                       <tr>
#                         <td style="color: #475569; font-weight: 600; width: 120px;">Task Title:</td>
#                         <td style="color: #1e293b;">{task['title']}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Description:</td>
#                         <td style="color: #1e293b;">{task['description']}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Completed By:</td>
#                         <td style="color: #1e293b;">{user_name}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Domain:</td>
#                         <td style="color: #1e293b;">{task['domain']}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Due Date:</td>
#                         <td style="color: #1e293b;">{due_date_str}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Frequency:</td>
#                         <td style="color: #1e293b;">{task['frequency']}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Priority:</td>
#                         <td style="color: #1e293b;">{task.get('priority', 'Medium')}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Completed On:</td>
#                         <td style="color: #15803d; font-weight: 600;">{completion_time}</td>
#                       </tr>
#                     </table>
#                   </div>
                  
#                   <div class="info-box">
#                     <p style="margin: 0; color: #1e40af; font-size: 14px;">
#                       <strong>Note:</strong> This task has been successfully completed and is now ready for your review.
#                     </p>
#                   </div>
                  
#                   <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
#                     <p style="color: #64748b; margin: 0 0 10px 0; font-size: 14px;">
#                       This is an automated notification from TaskFlow Pro System
#                     </p>
#                     <p style="color: #94a3b8; margin: 0; font-size: 12px;">
#                       Please do not reply to this email
#                     </p>
#                   </div>
#                 </div>
#               </body>
#             </html>
#             """
            
#             part = MIMEText(html, 'html')
#             msg.attach(part)
            
#             try:
#                 with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#                     server.login(sender_email, sender_password)
#                     server.send_message(msg)
#                 success_count += 1
#             except Exception as e:
#                 st.error(f"Error sending completion notification to {admin['email']}: {str(e)}")
        
#         return success_count > 0
        
#     except Exception as e:
#         st.error(f"Error sending task completion notifications: {str(e)}")
#         return False


# import pyodbc
# import streamlit as st
# import pandas as pd
# from datetime import datetime, date, timedelta
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import smtplib
# import os

# # ✅ MSSQL Connection with proper error handling
# @st.cache_resource
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
#                     "DATABASE=task_management_db;"
#                     "UID=sa;"
#                     "PWD=Yashal309;"
#                     "Encrypt=yes;"
#                     "TrustServerCertificate=yes;"
#                 )
#                 print(f"✅ SUCCESS with driver: {driver}")
#                 return conn  # Return the successful connection immediately
#             except Exception as driver_error:
#                 print(f"❌ Failed with {driver}: {driver_error}")
#                 continue  # Try next driver
        
#         # If no driver worked
#         st.error("❌ All ODBC drivers failed to connect")
#         return None
        
#     except Exception as e:
#         st.error(f"Failed to connect to SQL Server: {str(e)}")
#         return None
# def init_database():
#     """Initialize database schema and default data"""
#     conn = get_db_connection()
#     if conn is None:
#         st.error("❌ Cannot initialize database - no connection")
#         return
    
#     cursor = None
#     try:
#         cursor = conn.cursor()
        
#         # Create users table
#         cursor.execute("""
#             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
#             CREATE TABLE users (
#                 user_id INT PRIMARY KEY IDENTITY(1,1),
#                 name NVARCHAR(100) NOT NULL,
#                 email NVARCHAR(100) UNIQUE NOT NULL,
#                 role NVARCHAR(20) NOT NULL,
#                 created_at DATETIME DEFAULT GETDATE()
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
#                 created_at DATETIME DEFAULT GETDATE()
#             )
#         """)
        
#         # Create tasks table with enhanced fields
#         cursor.execute("""
#             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
#             CREATE TABLE tasks (
#                 task_id INT PRIMARY KEY IDENTITY(1,1),
#                 title NVARCHAR(255) NOT NULL,
#                 description NVARCHAR(MAX),
#                 domain NVARCHAR(100),
#                 assigned_to INT,
#                 attachment NVARCHAR(MAX),
#                 status NVARCHAR(50) DEFAULT 'Open',
#                 due_date DATETIME,
#                 frequency NVARCHAR(50),
#                 priority NVARCHAR(20) DEFAULT 'Medium',
#                 created_by INT,
#                 created_at DATETIME DEFAULT GETDATE(),
#                 updated_at DATETIME DEFAULT GETDATE(),
#                 FOREIGN KEY (assigned_to) REFERENCES users(user_id)
#             )
#         """)
        
#         # Check and add missing columns
#         missing_columns = [
#             ('tasks', 'priority', 'ALTER TABLE tasks ADD priority NVARCHAR(20) DEFAULT ''Medium'''),
#             ('tasks', 'created_by', 'ALTER TABLE tasks ADD created_by INT'),
#             ('tasks', 'updated_at', 'ALTER TABLE tasks ADD updated_at DATETIME DEFAULT GETDATE()')
#         ]
        
#         for table, column, alter_stmt in missing_columns:
#             try:
#                 cursor.execute(f"""
#                     IF NOT EXISTS (SELECT * FROM sys.columns 
#                                   WHERE object_id = OBJECT_ID('{table}') AND name = '{column}')
#                     BEGIN
#                         {alter_stmt}
#                     END
#                 """)
#                 print(f"✅ Checked/added column {table}.{column}")
#             except Exception as e:
#                 print(f"⚠️ Error with column {table}.{column}: {e}")
        
#         # Create comments table
#         cursor.execute("""
#             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='comments' AND xtype='U')
#             CREATE TABLE comments (
#                 comment_id INT PRIMARY KEY IDENTITY(1,1),
#                 task_id INT NOT NULL,
#                 user_id INT NOT NULL,
#                 comment_text NVARCHAR(MAX),
#                 created_at DATETIME DEFAULT GETDATE(),
#                 FOREIGN KEY (task_id) REFERENCES tasks(task_id),
#                 FOREIGN KEY (user_id) REFERENCES users(user_id)
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
#                 changed_at DATETIME DEFAULT GETDATE(),
#                 FOREIGN KEY (task_id) REFERENCES tasks(task_id)
#             )
#         """)
        
#         # Create indexes for better performance
#         cursor.execute("""
#             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_email' AND object_id=OBJECT_ID('users'))
#             CREATE INDEX idx_email ON users(email)
#         """)
#         cursor.execute("""
#             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_assigned_to' AND object_id=OBJECT_ID('tasks'))
#             CREATE INDEX idx_assigned_to ON tasks(assigned_to)
#         """)
#         cursor.execute("""
#             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_task_status' AND object_id=OBJECT_ID('tasks'))
#             CREATE INDEX idx_task_status ON tasks(status)
#         """)
#         cursor.execute("""
#             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_due_date' AND object_id=OBJECT_ID('tasks'))
#             CREATE INDEX idx_due_date ON tasks(due_date)
#         """)
        
#         conn.commit()
#         print("✅ Database schema updated successfully!")
        
#         # Insert default users - with existence check
#         default_users = [
#             ('Admin User', 'admin@nfoods.com', 'admin'),
#             ('Yashal Ali', 'yashal.ali@nfoods.com', 'admin'),
#             ('Ali', 'aliyashal309@gmail.com', 'user'),
#         ]
        
#         for name, email, role in default_users:
#             try:
#                 # Check if user already exists
#                 cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
#                 if cursor.fetchone()[0] == 0:
#                     cursor.execute("""
#                         INSERT INTO users (name, email, role)
#                         VALUES (?, ?, ?)
#                     """, (name, email, role))
#                     print(f"✅ Added user: {name} ({email})")
#                 else:
#                     print(f"ℹ️ User already exists: {name} ({email})")
#             except Exception as e:
#                 print(f"⚠️ User {email} already exists or error: {e}")
        
#         # Insert default domains with mancom members - with existence check
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
#                 # Check if domain already exists
#                 cursor.execute("SELECT COUNT(*) FROM domains WHERE domain_name = ?", (domain_name,))
#                 if cursor.fetchone()[0] == 0:
#                     cursor.execute("""
#                         INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
#                         VALUES (?, ?, ?)
#                     """, (domain_name, mancom_name, mancom_email))
#                     print(f"✅ Added domain: {domain_name}")
#                 else:
#                     print(f"ℹ️ Domain already exists: {domain_name}")
#             except Exception as e:
#                 print(f"⚠️ Domain {domain_name} already exists or error: {e}")
        
#         conn.commit()
#         print("✅ Database initialized successfully!")
        
#     except Exception as e:
#         st.error(f"Error initializing database: {str(e)}")
#         print(f"Database initialization error: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         # Only close cursor, not connection (connection is managed by streamlit cache)
#         if cursor:
#             cursor.close()
#         # Don't close the connection here - it's cached by streamlit

# # ✅ Helper Functions with proper connection handling
# def get_user_by_email(email):
#     """Get user by email address"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         query = "SELECT user_id, name, email, role FROM users WHERE email = ?"
#         df = pd.read_sql(query, conn, params=(email,))
#         if df.empty:
#             return None
#         return df.iloc[0].to_dict()
#     except Exception as e:
#         st.error(f"Error fetching user: {str(e)}")
#         return None
#     # Don't close connection - it's cached

# def get_all_users():
#     """Get all users as DataFrame"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = "SELECT user_id, name, email, role FROM users ORDER BY name"
#         df = pd.read_sql(query, conn)
#         return df
#     except Exception as e:
#         st.error(f"Error fetching users: {str(e)}")
#         return pd.DataFrame()

# def get_admin_users():
#     """Get all admin users"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = "SELECT user_id, name, email, role FROM users WHERE role = 'admin'"
#         df = pd.read_sql(query, conn)
#         return df
#     except Exception as e:
#         st.error(f"Error fetching admin users: {str(e)}")
#         return pd.DataFrame()

# def get_domains():
#     """Get all domains with mancom members"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = "SELECT domain_id, domain_name, mancom_member_name, mancom_member_email FROM domains ORDER BY domain_name"
#         df = pd.read_sql(query, conn)
#         return df
#     except Exception as e:
#         st.error(f"Error fetching domains: {str(e)}")
#         return pd.DataFrame()

# def get_mancom_member_by_domain(domain_name):
#     """Get mancom member for a specific domain"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         query = "SELECT mancom_member_name, mancom_member_email FROM domains WHERE domain_name = ?"
#         df = pd.read_sql(query, conn, params=(domain_name,))
#         if df.empty:
#             return None
#         return df.iloc[0].to_dict()
#     except Exception as e:
#         st.error(f"Error fetching mancom member: {str(e)}")
#         return None

# def create_task(title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, created_by):
#     """Create a new task with safe column handling"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     if isinstance(due_date, date) and not isinstance(due_date, datetime):
#         due_date = datetime.combine(due_date, datetime.min.time())
    
#     cursor = conn.cursor()
#     try:
#         # Check which columns exist
#         cursor.execute("""
#             SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
#             WHERE TABLE_NAME = 'tasks'
#         """)
#         existing_columns = [row[0] for row in cursor.fetchall()]
        
#         # Build dynamic INSERT statement based on available columns
#         columns = ['title', 'description', 'domain', 'assigned_to', 'attachment', 'status', 'due_date', 'frequency', 'priority']
#         placeholders = ['?'] * len(columns)
        
#         # Add created_by if column exists
#         if 'created_by' in existing_columns:
#             columns.append('created_by')
#             placeholders.append('?')
        
#         # Add updated_at if column exists
#         if 'updated_at' in existing_columns:
#             columns.append('updated_at')
#             placeholders.append('GETDATE()')
        
#         # Add created_at if column exists
#         if 'created_at' in existing_columns:
#             columns.append('created_at')
#             placeholders.append('GETDATE()')
        
#         columns_str = ', '.join(columns)
#         placeholders_str = ', '.join(placeholders)
        
#         # Prepare values
#         values = [title, description, domain, assigned_to, attachment, status, due_date, frequency, priority]
#         if 'created_by' in existing_columns:
#             values.append(created_by)
        
#         query = f"INSERT INTO tasks ({columns_str}) VALUES ({placeholders_str})"
#         cursor.execute(query, values)
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error creating task: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def get_tasks(user_id=None, role='user', include_completed=True):
#     """Get tasks with user info and comment counts - FIXED QUERY"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         # First check if priority column exists
#         cursor = conn.cursor()
#         cursor.execute("""
#             SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
#             WHERE TABLE_NAME = 'tasks' AND COLUMN_NAME = 'priority'
#         """)
#         has_priority = cursor.fetchone()[0] > 0
#         cursor.close()
        
#         # Build query based on available columns
#         if has_priority:
#             base_query = """
#             SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                    (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             """
#             order_by = "ORDER BY t.due_date ASC, t.priority DESC"
#         else:
#             base_query = """
#             SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                    (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             """
#             order_by = "ORDER BY t.due_date ASC"
        
#         if role == 'admin':
#             if include_completed:
#                 query = f"{base_query} {order_by}"
#                 df = pd.read_sql(query, conn)
#             else:
#                 query = f"{base_query} WHERE t.status != 'Completed' {order_by}"
#                 df = pd.read_sql(query, conn)
#         else:
#             if include_completed:
#                 query = f"{base_query} WHERE t.assigned_to = ? {order_by}"
#                 df = pd.read_sql(query, conn, params=(user_id,))
#             else:
#                 query = f"{base_query} WHERE t.assigned_to = ? AND t.status != 'Completed' {order_by}"
#                 df = pd.read_sql(query, conn, params=(user_id,))
        
#         # Ensure status column exists and has proper values
#         if 'status' not in df.columns:
#             df['status'] = 'Open'
#         else:
#             df['status'] = df['status'].fillna('Open')
            
#         # Ensure priority column exists
#         if 'priority' not in df.columns:
#             df['priority'] = 'Medium'
            
#         # Ensure due_date is properly formatted as datetime
#         if 'due_date' in df.columns:
#             df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
        
#         return df
#     except Exception as e:
#         st.error(f"Error fetching tasks: {str(e)}")
#         return pd.DataFrame()

# def get_task_by_id(task_id):
#     """Get a specific task by ID with safe column handling"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         # Check if created_by column exists
#         cursor = conn.cursor()
#         cursor.execute("""
#             SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
#             WHERE TABLE_NAME = 'tasks' AND COLUMN_NAME = 'created_by'
#         """)
#         has_created_by = cursor.fetchone()[0] > 0
#         cursor.close()
        
#         # Build query based on available columns
#         if has_created_by:
#             query = """
#             SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                    creator.name AS created_by_name
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             LEFT JOIN users creator ON t.created_by = creator.user_id
#             WHERE t.task_id = ?
#             """
#         else:
#             query = """
#             SELECT t.*, u.name AS assigned_name, u.email AS assigned_email
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             WHERE t.task_id = ?
#             """
        
#         df = pd.read_sql(query, conn, params=(task_id,))
#         if df.empty:
#             return None
        
#         task = df.iloc[0].to_dict()
#         # Ensure all required fields exist
#         if 'status' not in task or not task['status']:
#             task['status'] = 'Open'
#         if 'priority' not in task or not task['priority']:
#             task['priority'] = 'Medium'
#         if 'created_by_name' not in task:
#             task['created_by_name'] = 'Unknown'
            
#         return task
#     except Exception as e:
#         st.error(f"Error fetching task: {str(e)}")
#         return None

# def update_task_status(task_id, status, changed_by=None):
#     """Update task status with proper column handling"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Get old status for history
#         cursor.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,))
#         result = cursor.fetchone()
#         old_status = result[0] if result else 'Open'
        
#         # Check if updated_at column exists
#         cursor.execute("""
#             SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
#             WHERE TABLE_NAME = 'tasks' AND COLUMN_NAME = 'updated_at'
#         """)
#         has_updated_at = cursor.fetchone()[0] > 0
        
#         # Update task - with or without updated_at column
#         if has_updated_at:
#             cursor.execute("""
#                 UPDATE tasks
#                 SET status = ?, updated_at = GETDATE()
#                 WHERE task_id = ?
#             """, (status, task_id))
#         else:
#             cursor.execute("""
#                 UPDATE tasks
#                 SET status = ?
#                 WHERE task_id = ?
#             """, (status, task_id))
        
#         # Add to history if changed_by provided
#         if changed_by:
#             # Check if task_history table exists
#             cursor.execute("""
#                 SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
#                 WHERE TABLE_NAME = 'task_history'
#             """)
#             has_history_table = cursor.fetchone()[0] > 0
            
#             if has_history_table:
#                 cursor.execute("""
#                     INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
#                     VALUES (?, 'status', ?, ?, ?)
#                 """, (task_id, old_status, status, changed_by))
        
#         conn.commit()
        
#         # Send notification if task was completed
#         sender_email = os.environ.get("SMTP_USERNAME")
#         sender_password = os.environ.get("SMTP_PASSWORD")
#         if status == 'Completed' and old_status != 'Completed':
#             task = get_task_by_id(task_id)
#             if task and sender_email and sender_password:
#                 # Send completion notification to admins
#                 send_task_completion_notification(task, st.session_state.user_name, sender_email, sender_password)
        
#         return True
#     except Exception as e:
#         st.error(f"Error updating task status: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def update_task(task_id, title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, updated_by):
#     """Update entire task"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Get old values for history
#         cursor.execute("SELECT title, description, domain, assigned_to, attachment, status, due_date, frequency, priority FROM tasks WHERE task_id = ?", (task_id,))
#         old_values = cursor.fetchone()
        
#         if old_values:
#             old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = old_values
#         else:
#             # If no old values found, set defaults
#             old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = '', '', '', None, '', 'Open', None, '', 'Medium'

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
#         return True
#     except Exception as e:
#         st.error(f"Error updating task: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def delete_task(task_id):
#     """Delete task and its comments"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Delete all comments for this task
#         cursor.execute("DELETE FROM comments WHERE task_id = ?", (task_id,))
        
#         # Delete task history
#         cursor.execute("DELETE FROM task_history WHERE task_id = ?", (task_id,))
        
#         # Delete the task
#         cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error deleting task: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def get_comments(task_id):
#     """Get all comments for a task"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#         SELECT c.comment_id, c.task_id, c.user_id, c.comment_text, c.created_at,
#                u.name, u.email
#         FROM comments c
#         LEFT JOIN users u ON c.user_id = u.user_id
#         WHERE c.task_id = ?
#         ORDER BY c.created_at ASC
#         """
#         df = pd.read_sql(query, conn, params=(task_id,))
#         return df
#     except Exception as e:
#         st.error(f"Error fetching comments: {str(e)}")
#         return pd.DataFrame()

# def add_comment(task_id, user_id, comment_text):
#     """Add a comment to a task"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             INSERT INTO comments (task_id, user_id, comment_text, created_at)
#             VALUES (?, ?, ?, ?)
#         """, (task_id, user_id, comment_text, datetime.now()))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error adding comment: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def add_user(name, email, role='user'):
#     """Add a new user"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             INSERT INTO users (name, email, role)
#             VALUES (?, ?, ?)
#         """, (name, email, role))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error adding user: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def update_user(user_id, name, email, role):
#     """Update user details"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             UPDATE users
#             SET name = ?, email = ?, role = ?
#             WHERE user_id = ?
#         """, (name, email, role, user_id))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error updating user: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def delete_user(user_id):
#     """Delete a user"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # First, update tasks assigned to this user to NULL
#         cursor.execute("UPDATE tasks SET assigned_to = NULL WHERE assigned_to = ?", (user_id,))
        
#         # Delete user's comments
#         cursor.execute("DELETE FROM comments WHERE user_id = ?", (user_id,))
        
#         # Delete the user
#         cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error deleting user: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def add_domain(domain_name, mancom_member_name, mancom_member_email):
#     """Add a new domain"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
#             VALUES (?, ?, ?)
#         """, (domain_name, mancom_member_name, mancom_member_email))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error adding domain: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

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

# def delete_domain(domain_id):
#     """Delete a domain"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("DELETE FROM domains WHERE domain_id = ?", (domain_id,))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error deleting domain: {str(e)}")
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()

# def get_overdue_tasks():
#     """Get tasks that are overdue"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         query = """
#         SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#         FROM tasks t
#         LEFT JOIN users u ON t.assigned_to = u.user_id
#         WHERE t.due_date < GETDATE() AND t.status IN ('Open', 'In Progress')
#         ORDER BY t.due_date ASC
#         """
#         df = pd.read_sql(query, conn)
        
#         # Ensure status column exists
#         if 'status' not in df.columns:
#             df['status'] = 'Open'
            
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
#         SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#         FROM tasks t
#         LEFT JOIN users u ON t.assigned_to = u.user_id
#         WHERE t.due_date BETWEEN GETDATE() AND DATEADD(day, ?, GETDATE()) 
#           AND t.status IN ('Open', 'In Progress')
#         ORDER BY t.due_date ASC
#         """
#         df = pd.read_sql(query, conn, params=(days,))
        
#         # Ensure status column exists
#         if 'status' not in df.columns:
#             df['status'] = 'Open'
            
#         return df
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
#         SELECT th.field_name, th.old_value, th.new_value, th.changed_at, u.name as changed_by_name
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

# # Email functions
# def send_email_summary(user_email, user_name, tasks_df, sender_email, sender_password):
#     """Send email summary of pending tasks"""
#     try:
#         msg = MIMEMultipart('alternative')
#         msg['Subject'] = f'TaskFlow Pro - Pending Tasks Summary – {datetime.now().strftime("%B %Y")}'
#         msg['From'] = sender_email
#         msg['To'] = user_email

#         html = f"""
#         <html>
#           <head>
#             <style>
#               body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
#               .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
#               .header {{ border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; }}
#               .task-table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
#               .task-table th {{ background-color: #2563eb; color: white; padding: 12px 8px; text-align: left; }}
#               .task-table td {{ padding: 12px 8px; border-bottom: 1px solid #e2e8f0; }}
#               .priority-high {{ color: #dc2626; font-weight: bold; }}
#               .priority-medium {{ color: #f59e0b; font-weight: bold; }}
#               .priority-low {{ color: #10b981; font-weight: bold; }}
#               .status-open {{ color: #f59e0b; }}
#               .status-inprogress {{ color: #2563eb; }}
#               .status-completed {{ color: #10b981; }}
#               .info-box {{ background-color: #f8fafc; border-left: 3px solid #2563eb; padding: 16px; margin: 25px 0; }}
#             </style>
#           </head>
#           <body>
#             <div class="container">
#               <div class="header">
#                 <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 28px; font-weight: 700;">Task Summary Report</h1>
#                 <p style="color: #64748b; margin: 0; font-size: 16px;">Hello {user_name},</p>
#               </div>
#               <p style="color: #475569; font-size: 15px; margin-bottom: 25px;">Here are your pending tasks that require attention:</p>
              
#               <table class="task-table">
#                 <thead>
#                   <tr>
#                     <th>Task</th>
#                     <th>Domain</th>
#                     <th>Priority</th>
#                     <th>Due Date</th>
#                     <th>Status</th>
#                     <th style="text-align: center;">Comments</th>
#                   </tr>
#                 </thead>
#                 <tbody>
#         """

#         for _, task in tasks_df.iterrows():
#             # Safe data access with defaults
#             title = task.get('title', 'Untitled Task')
#             description = str(task.get('description', 'No description'))[:80] + '...' if task.get('description') else 'No description'
#             domain = task.get('domain', 'No domain')
#             priority = task.get('priority', 'Medium')
#             status = task.get('status', 'Open')
            
#             # Safe date formatting
#             due_date_str = "N/A"
#             if pd.notna(task.get('due_date')):
#                 try:
#                     due_date_str = task['due_date'].strftime("%Y-%m-%d")
#                 except:
#                     due_date_str = "Invalid date"
            
#             # Safe priority class
#             priority_lower = str(priority).lower() if priority else 'medium'
#             priority_class = f"priority-{priority_lower}"
            
#             # Safe status class
#             status_lower = str(status).lower().replace(' ', '') if status else 'open'
#             status_class = f"status-{status_lower}"
            
#             comment_count = task.get('comment_count', 0)

#             html += f"""
#                   <tr>
#                     <td><b>{title}</b><br><span style="color:#64748b; font-size: 12px;">{description}</span></td>
#                     <td>{domain}</td>
#                     <td><span class="{priority_class}">{priority}</span></td>
#                     <td>{due_date_str}</td>
#                     <td><span class="{status_class}">{status}</span></td>
#                     <td style="text-align:center; color:#2563eb; font-weight: bold;">{comment_count}</td>
#                   </tr>
#             """

#         html += """
#                 </tbody>
#               </table>
              
#               <div class="info-box">
#                 <p style="margin:0; font-weight: 500;">Please update task statuses and provide updates as you make progress.</p>
#               </div>
              
#               <div style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:10px; color:#64748b; font-size:13px;">
#                 <p>Best regards,</p>
#                 <p style="font-weight:600; color:#475569;">TaskFlow Pro Administration</p>
#                 <p style="font-size:12px; color:#94a3b8;">This is an automated email. Please do not reply directly to this message.</p>
#               </div>
#             </div>
#           </body>
#         </html>
#         """

#         part = MIMEText(html, 'html')
#         msg.attach(part)

#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#             server.login(sender_email, sender_password)
#             server.send_message(msg)

#         return True

#     except Exception as e:
#         st.error(f"Error sending email to {user_email}: {str(e)}")
#         return False

# def send_escalation_email(task, sender_email, sender_password):
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
#         assigned_name = task.get('assigned_name', 'Unassigned')
#         domain = task.get('domain', 'Unknown')
#         status = task.get('status', 'Open')
#         priority = task.get('priority', 'Medium')
        
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
        
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#             server.login(sender_email, sender_password)
#             server.send_message(msg)
        
#         return True
        
#     except Exception as e:
#         st.error(f"Error sending escalation email: {str(e)}")
#         return False

# def send_task_completion_notification(task, user_name, sender_email, sender_password):
#     """Send notification to admins when a task is completed"""
#     try:
#         admin_users = get_admin_users()
        
#         if admin_users.empty:
#             st.error("No admin users found to send notification")
#             return False
        
#         success_count = 0
        
#         for _, admin in admin_users.iterrows():
#             msg = MIMEMultipart('alternative')
#             msg['Subject'] = f'✅ Task Completed: {task.get("title", "Untitled Task")}'
#             msg['From'] = sender_email
#             msg['To'] = admin.get('email', '')
            
#             # Safe data access
#             title = task.get('title', 'Untitled Task')
#             description = task.get('description', 'No description')
#             domain = task.get('domain', 'Unknown')
#             frequency = task.get('frequency', 'One-time')
#             priority = task.get('priority', 'Medium')
            
#             # Safe date handling
#             due_date_str = "Not specified"
#             if pd.notna(task.get('due_date')):
#                 try:
#                     due_date_str = task['due_date'].strftime("%Y-%m-%d")
#                 except:
#                     due_date_str = "Invalid date"
            
#             completion_time = datetime.now().strftime("%Y-%m-%d at %I:%M %p")
            
#             html = f"""
#             <html>
#               <head>
#                 <style>
#                   body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
#                   .container {{ max-width: 700px; margin: 0 auto; padding: 25px; }}
#                   .header {{ border-bottom: 3px solid #10b981; padding-bottom: 20px; margin-bottom: 30px; }}
#                   .success-box {{ background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 25px; }}
#                   .info-box {{ background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 16px; margin-bottom: 25px; }}
#                   .task-details {{ width: 100%; border-collapse: collapse; }}
#                   .task-details td {{ padding: 8px 0; }}
#                 </style>
#               </head>
#               <body>
#                 <div class="container">
#                   <div class="header">
#                     <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 26px; font-weight: 700;">✅ Task Completed Successfully</h1>
#                     <p style="color: #64748b; margin: 0; font-size: 16px;">Great news! A task has been marked as completed.</p>
#                   </div>
                  
#                   <div class="success-box">
#                     <h2 style="color: #15803d; margin: 0 0 15px 0; font-size: 20px; font-weight: 600;">Task Details</h2>
                    
#                     <table class="task-details">
#                       <tr>
#                         <td style="color: #475569; font-weight: 600; width: 120px;">Task Title:</td>
#                         <td style="color: #1e293b;">{title}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Description:</td>
#                         <td style="color: #1e293b;">{description}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Completed By:</td>
#                         <td style="color: #1e293b;">{user_name}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Domain:</td>
#                         <td style="color: #1e293b;">{domain}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Due Date:</td>
#                         <td style="color: #1e293b;">{due_date_str}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Frequency:</td>
#                         <td style="color: #1e293b;">{frequency}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Priority:</td>
#                         <td style="color: #1e293b;">{priority}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Completed On:</td>
#                         <td style="color: #15803d; font-weight: 600;">{completion_time}</td>
#                       </tr>
#                     </table>
#                   </div>
                  
#                   <div class="info-box">
#                     <p style="margin: 0; color: #1e40af; font-size: 14px;">
#                       <strong>Note:</strong> This task has been successfully completed and is now ready for your review.
#                     </p>
#                   </div>
                  
#                   <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
#                     <p style="color: #64748b; margin: 0 0 10px 0; font-size: 14px;">
#                       This is an automated notification from TaskFlow Pro System
#                     </p>
#                     <p style="color: #94a3b8; margin: 0; font-size: 12px;">
#                       Please do not reply to this email
#                     </p>
#                   </div>
#                 </div>
#               </body>
#             </html>
#             """
            
#             part = MIMEText(html, 'html')
#             msg.attach(part)
            
#             try:
#                 with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#                     server.login(sender_email, sender_password)
#                     server.send_message(msg)
#                 success_count += 1
#             except Exception as e:
#                 st.error(f"Error sending completion notification to {admin.get('email', 'Unknown')}: {str(e)}")
        
#         return success_count > 0
        
#     except Exception as e:
#         st.error(f"Error sending task completion notifications: {str(e)}")

    
#     """Send notification to admins when a task is completed"""
#     try:
#         admin_users = get_admin_users()
        
#         if admin_users.empty:
#             st.error("No admin users found to send notification")
#             return False
        
#         success_count = 0
        
#         for _, admin in admin_users.iterrows():
#             msg = MIMEMultipart('alternative')
#             msg['Subject'] = f'✅ Task Completed: {task["title"]}'
#             msg['From'] = sender_email
#             msg['To'] = admin['email']
            
#             due_date_str = task['due_date'].strftime("%Y-%m-%d") if pd.notna(task['due_date']) else "Not specified"
#             completion_time = datetime.now().strftime("%Y-%m-%d at %I:%M %p")
            
#             html = f"""
#             <html>
#               <head>
#                 <style>
#                   body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
#                   .container {{ max-width: 700px; margin: 0 auto; padding: 25px; }}
#                   .header {{ border-bottom: 3px solid #10b981; padding-bottom: 20px; margin-bottom: 30px; }}
#                   .success-box {{ background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 25px; }}
#                   .info-box {{ background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 16px; margin-bottom: 25px; }}
#                   .task-details {{ width: 100%; border-collapse: collapse; }}
#                   .task-details td {{ padding: 8px 0; }}
#                 </style>
#               </head>
#               <body>
#                 <div class="container">
#                   <div class="header">
#                     <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 26px; font-weight: 700;">✅ Task Completed Successfully</h1>
#                     <p style="color: #64748b; margin: 0; font-size: 16px;">Great news! A task has been marked as completed.</p>
#                   </div>
                  
#                   <div class="success-box">
#                     <h2 style="color: #15803d; margin: 0 0 15px 0; font-size: 20px; font-weight: 600;">Task Details</h2>
                    
#                     <table class="task-details">
#                       <tr>
#                         <td style="color: #475569; font-weight: 600; width: 120px;">Task Title:</td>
#                         <td style="color: #1e293b;">{task['title']}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Description:</td>
#                         <td style="color: #1e293b;">{task['description']}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Completed By:</td>
#                         <td style="color: #1e293b;">{user_name}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Domain:</td>
#                         <td style="color: #1e293b;">{task['domain']}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Due Date:</td>
#                         <td style="color: #1e293b;">{due_date_str}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Frequency:</td>
#                         <td style="color: #1e293b;">{task['frequency']}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Priority:</td>
#                         <td style="color: #1e293b;">{task.get('priority', 'Medium')}</td>
#                       </tr>
#                       <tr>
#                         <td style="color: #475569; font-weight: 600;">Completed On:</td>
#                         <td style="color: #15803d; font-weight: 600;">{completion_time}</td>
#                       </tr>
#                     </table>
#                   </div>
                  
#                   <div class="info-box">
#                     <p style="margin: 0; color: #1e40af; font-size: 14px;">
#                       <strong>Note:</strong> This task has been successfully completed and is now ready for your review.
#                     </p>
#                   </div>
                  
#                   <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
#                     <p style="color: #64748b; margin: 0 0 10px 0; font-size: 14px;">
#                       This is an automated notification from TaskFlow Pro System
#                     </p>
#                     <p style="color: #94a3b8; margin: 0; font-size: 12px;">
#                       Please do not reply to this email
#                     </p>
#                   </div>
#                 </div>
#               </body>
#             </html>
#             """
            
#             part = MIMEText(html, 'html')
#             msg.attach(part)
            
#             try:
#                 with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#                     server.login(sender_email, sender_password)
#                     server.send_message(msg)
#                 success_count += 1
#             except Exception as e:
#                 st.error(f"Error sending completion notification to {admin['email']}: {str(e)}")
        
#         return success_count > 0
        
#     except Exception as e:
#         st.error(f"Error sending task completion notifications: {str(e)}")
#         return False


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


# =============================================
# Database Configuration & Connection
# =============================================

@st.cache_resource
def get_db_connection():
    """
    Creates a MSSQL connection using Streamlit secrets or local config.
    Connection is cached to avoid multiple connections.
    """
    try:
        drivers = pyodbc.drivers()
        print("Available drivers:", drivers)
        
        # Try each driver until one works
        
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
# Database Initialization
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
        
        # Create users table with proper security
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                user_id INT PRIMARY KEY IDENTITY(1,1),
                username NVARCHAR(50) UNIQUE NOT NULL,
                email NVARCHAR(100) UNIQUE NOT NULL,
                password_hash NVARCHAR(255) NOT NULL,
                role NVARCHAR(20) NOT NULL CHECK (role IN ('admin', 'user')),
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
                comments NVARCHAR(MAX), -- JSON string for comments array
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
            ('admin', 'admin@nfoods.com', hashed_password, 'admin'),
            ('yashal.ali', 'yashal.ali@nfoods.com', hashed_password, 'admin'),
        ]
        
        for username, email, password, role in default_users:
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM users WHERE email = ?)
                    INSERT INTO users (username, email, password_hash, role)
                    VALUES (?, ?, ?, ?)
                """, (email, username, email, password, role))
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
# User Management Functions
# =============================================

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user by email and return user data if successful"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        query = """
            SELECT user_id, username, email, password_hash, role, is_active 
            FROM users 
            WHERE email = ? AND is_active = 1
        """
        df = pd.read_sql(query, conn, params=(email,))
        
        if df.empty:
            return None
            
        user = df.iloc[0].to_dict()
        
        if PasswordHasher.verify_password(password, user['password_hash']):
            # Update last login
            cursor = conn.cursor()
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
    
def change_user_password(user_id: int, current_password: str, new_password: str) -> bool:
    """Change user password with verification"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        # Verify current password
        cursor.execute(
            "SELECT password_hash FROM users WHERE user_id = ?", 
            (user_id,)
        )
        result = cursor.fetchone()
        
        if not result or not PasswordHasher.verify_password(current_password, result[0]):
            st.error("Current password is incorrect")
            return False
        
        # Update to new password
        new_hashed_password = PasswordHasher.hash_password(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = ?, updated_at = GETDATE() WHERE user_id = ?",
            (new_hashed_password, user_id)
        )
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Error changing password: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
def create_user(username: str, email: str, password: str, role: str = 'user') -> bool:
    """Create a new user with hashed password"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        hashed_password = PasswordHasher.hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (username, email, hashed_password, role))
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
            SELECT user_id, username, email, role, is_active, created_at, last_login
            FROM users 
            ORDER BY username
        """
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error fetching users: {str(e)}")
        return pd.DataFrame()

def get_all_users_with_names():
    """Get all users with proper name field"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
            SELECT user_id, username, email, role, is_active, created_at, last_login,
                   COALESCE(name, username) as display_name
            FROM users 
            ORDER BY username
        """
        df = pd.read_sql(query, conn)
        return df
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
        
        # Simply delete the user (let database handle foreign key constraints)
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

#delete with proper checks and reassignment prompts to N/A or other users
# def delete_user(user_id: int) -> bool:
#     """Delete a user and set their assigned tasks to NULL"""
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
        
#         # Count tasks assigned to this user
#         cursor.execute("SELECT COUNT(*) FROM tasks WHERE assigned_to = ?", (user_id,))
#         task_count = cursor.fetchone()[0]
        
#         # Set assigned_to to NULL for all tasks assigned to this user
#         if task_count > 0:
#             cursor.execute("UPDATE tasks SET assigned_to = NULL WHERE assigned_to = ?", (user_id,))
#             st.info(f"✅ Unassigned {task_count} tasks from user '{username}'")
        
#         # Delete the user
#         cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
#         conn.commit()
        
#         if cursor.rowcount > 0:
#             st.success(f"✅ User '{username}' deleted successfully!")
#             if task_count > 0:
#                 st.info(f"📝 {task_count} tasks were unassigned and need to be reassigned")
#             return True
#         else:
#             st.error("❌ Failed to delete user")
#             return False
            
#     except Exception as e:
#         st.error(f"❌ Error deleting user: {str(e)}")
#         if conn:
#             conn.rollback()
#         return False
#     finally:
#         if cursor:
#             cursor.close()

# =============================================
# Task Management Functions
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
    include_closed: bool = True  # Changed default to True
) -> pd.DataFrame:
    """Get tasks based on user role and filters - NOW INCLUDES CLOSED TASKS BY DEFAULT"""
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
    
def get_overdue_tasks():
    """Get tasks that are overdue"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT t.*, u.username AS assigned_username, u.email AS assigned_email
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.user_id
        WHERE t.due_date < GETDATE() AND t.status IN ('open', 'in_progress')
        ORDER BY t.due_date ASC
        """
        df = pd.read_sql(query, conn)
        
        # Ensure status column exists
        if 'status' not in df.columns:
            df['status'] = 'open'
            
        return df
    except Exception as e:
        st.error(f"Error fetching overdue tasks: {str(e)}")
        return pd.DataFrame()

def get_tasks_due_soon(days=7):
    """Get tasks due within specified days"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT t.*, u.username AS assigned_username, u.email AS assigned_email
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.user_id
        WHERE t.due_date BETWEEN GETDATE() AND DATEADD(day, ?, GETDATE()) 
          AND t.status IN ('open', 'in_progress')
        ORDER BY t.due_date ASC
        """
        df = pd.read_sql(query, conn, params=(days,))
        
        # Ensure status column exists
        if 'status' not in df.columns:
            df['status'] = 'open'
            
        return df
    except Exception as e:
        st.error(f"Error fetching tasks due soon: {str(e)}")
        return pd.DataFrame()


def get_overdue_tasks():
    """Get tasks that are overdue (fallback implementation)"""
    try:
        tasks_df = get_tasks(role='admin')
        if tasks_df.empty:
            return pd.DataFrame()
        
        # Filter overdue tasks
        overdue_tasks = tasks_df[
            (tasks_df['due_date'] < datetime.now()) & 
            (tasks_df['status'].isin(['open', 'in_progress']))
        ]
        
        return overdue_tasks
    except Exception as e:
        st.error(f"Error fetching overdue tasks: {str(e)}")
        return pd.DataFrame()

def get_tasks_due_soon(days=7):
    """Get tasks due within specified days (fallback implementation)"""
    try:
        tasks_df = get_tasks(role='admin')
        if tasks_df.empty:
            return pd.DataFrame()
        
        # Calculate date range
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        # Filter tasks due soon
        due_soon_tasks = tasks_df[
            (tasks_df['due_date'] >= start_date) & 
            (tasks_df['due_date'] <= end_date) & 
            (tasks_df['status'].isin(['open', 'in_progress']))
        ]
        
        return due_soon_tasks
    except Exception as e:
        st.error(f"Error fetching tasks due soon: {str(e)}")
        return pd.DataFrame()

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

def send_escalation_email(task: dict, sender_email: str, sender_password: str) -> bool:
    """Send escalation email to mancom member for overdue tasks"""
    try:
        mancom_member = get_mancom_member_by_domain(task.get('domain', ''))
        if not mancom_member:
            st.error(f"No mancom member found for domain: {task.get('domain', 'Unknown')}")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🚨 ESCALATION: Overdue Task - {task.get("title", "Untitled Task")}'
        msg['From'] = sender_email
        msg['To'] = mancom_member.get('mancom_member_email', '')
        
        # Safe data access
        title = task.get('title', 'Untitled Task')
        description = task.get('description', 'No description')
        assigned_name = task.get('assigned_username', 'Unassigned')
        domain = task.get('domain', 'Unknown')
        status = task.get('status', 'open')
        priority = task.get('priority', 'medium')
        
        # Safe date handling
        due_date_str = "Not specified"
        overdue_days = 0
        if pd.notna(task.get('due_date')):
            try:
                due_date_str = task['due_date'].strftime("%Y-%m-%d")
                if isinstance(task['due_date'], (pd.Timestamp, datetime)):
                    overdue_days = (datetime.now().date() - task['due_date'].date()).days
                else:
                    due_date_str = str(task['due_date'])
            except:
                due_date_str = "Invalid date"
        
        html = f"""
        <html>
          <head>
            <style>
              body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
              .container {{ max-width: 700px; margin: 0 auto; padding: 25px; }}
              .header {{ border-bottom: 3px solid #dc2626; padding-bottom: 20px; margin-bottom: 30px; }}
              .alert-box {{ background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 20px; margin-bottom: 25px; }}
              .info-box {{ background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 16px; margin-bottom: 25px; }}
              .task-details {{ width: 100%; border-collapse: collapse; }}
              .task-details td {{ padding: 8px 0; }}
            </style>
          </head>
          <body>
            <div class="container">
              <div class="header">
                <h1 style="color: #dc2626; margin: 0 0 10px 0; font-size: 26px; font-weight: 700;">🚨 Task Escalation Required</h1>
                <p style="color: #64748b; margin: 0; font-size: 16px;">A task requires your immediate attention as Mancom Member.</p>
              </div>
              
              <div class="alert-box">
                <h2 style="color: #dc2626; margin: 0 0 15px 0; font-size: 20px; font-weight: 600;">Task Details</h2>
                
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
                    <td style="color: #475569; font-weight: 600;">Assigned To:</td>
                    <td style="color: #1e293b;">{assigned_name}</td>
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
                    <td style="color: #475569; font-weight: 600;">Current Status:</td>
                    <td style="color: #dc2626; font-weight: 600;">{status}</td>
                  </tr>
                  <tr>
                    <td style="color: #475569; font-weight: 600;">Overdue By:</td>
                    <td style="color: #dc2626; font-weight: 600;">{overdue_days} days</td>
                  </tr>
                  <tr>
                    <td style="color: #475569; font-weight: 600;">Priority:</td>
                    <td style="color: #dc2626; font-weight: 600;">{priority}</td>
                  </tr>
                </table>
              </div>
              
              <div class="info-box">
                <p style="margin: 0; color: #1e40af; font-size: 14px; font-weight: 500;">
                  <strong>Action Required:</strong> This task is overdue and requires your attention as the Mancom member for the {domain} domain. 
                  Please follow up with the assigned team member and ensure completion.
                </p>
              </div>
              
              <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                <p style="color: #64748b; margin: 0 0 10px 0; font-size: 14px;">
                  This is an automated escalation email from TaskFlow Pro System
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
        
        with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
            server.starttls()  # Enable TLS
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        st.success(f"✅ Escalation email sent to {mancom_member.get('mancom_member_name')}")
        return True
        
    except Exception as e:
        st.error(f"❌ Error sending escalation email: {str(e)}")
        return False

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

def get_mancom_member_by_domain(domain_name: str):
    """Get mancom member for a specific domain"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mancom_member_name, mancom_member_email 
            FROM domains 
            WHERE domain_name = ? AND (is_active = 1 OR is_active IS NULL)
        """, (domain_name,))
        
        result = cursor.fetchone()
        if result:
            return {
                'mancom_member_name': result[0],
                'mancom_member_email': result[1]
            }
        return None
        
    except Exception as e:
        st.error(f"Error fetching mancom member: {str(e)}")
        return None
    finally:
        if cursor:
            cursor.close()

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
# =============================================
# Domain Management Functions
# =============================================

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

def get_mancom_member_by_domain(domain_name: str) -> Optional[Dict]:
    """Get mancom member for a specific domain"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        query = """
            SELECT mancom_member_name, mancom_member_email 
            FROM domains 
            WHERE domain_name = ? AND is_active = 1
        """
        df = pd.read_sql(query, conn, params=(domain_name,))
        return df.iloc[0].to_dict() if not df.empty else None
    except Exception as e:
        st.error(f"Error fetching mancom member: {str(e)}")
        return None

# =============================================
# Email Notification Functions
# =============================================

def send_task_notification(task: Dict, notification_type: str, sender_email: str, sender_password: str) -> bool:
    """Send email notifications for task events"""
    try:
        if notification_type == 'completion':
            return send_completion_notification(task, sender_email, sender_password)
        elif notification_type == 'escalation':
            return send_escalation_notification(task, sender_email, sender_password)
        elif notification_type == 'assignment':
            return send_assignment_notification(task, sender_email, sender_password)
        else:
            return False
    except Exception as e:
        st.error(f"Error sending notification: {str(e)}")
        return False

def send_completion_notification(task: Dict, sender_email: str, sender_password: str) -> bool:
    """Send notification when task is completed"""
    try:
        admin_users = get_all_users()
        admin_users = admin_users[admin_users['role'] == 'admin']
        
        success_count = 0
        for _, admin in admin_users.iterrows():
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'✅ Task Completed: {task["title"]}'
            msg['From'] = sender_email
            msg['To'] = admin['email']
            
            html = create_completion_email_html(task, admin['username'])
            part = MIMEText(html, 'html')
            msg.attach(part)
            
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                success_count += 1
            except Exception as e:
                print(f"Failed to send to {admin['email']}: {e}")
        
        return success_count > 0
    except Exception as e:
        st.error(f"Error sending completion notification: {str(e)}")
        return False

def send_escalation_notification(task: Dict, sender_email: str, sender_password: str) -> bool:
    """Send escalation notification for overdue tasks"""
    try:
        mancom_member = get_mancom_member_by_domain(task.get('domain', ''))
        if not mancom_member:
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🚨 ESCALATION: Overdue Task - {task["title"]}'
        msg['From'] = sender_email
        msg['To'] = mancom_member['mancom_member_email']
        
        html = create_escalation_email_html(task, mancom_member)
        part = MIMEText(html, 'html')
        msg.attach(part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"Error sending escalation notification: {str(e)}")
        return False

def send_assignment_notification(task: Dict, sender_email: str, sender_password: str) -> bool:
    """Send notification when task is assigned"""
    # Implementation similar to above
    pass

def create_completion_email_html(task: Dict, admin_name: str) -> str:
    """Create HTML email for task completion"""
    due_date = task.get('due_date', 'Not specified')
    if isinstance(due_date, (datetime, pd.Timestamp)):
        due_date = due_date.strftime("%Y-%m-%d")
    
    return f"""
    <html>
      <body>
        <h2>Task Completed Successfully</h2>
        <p>Hello {admin_name},</p>
        <p>The following task has been marked as completed:</p>
        <div style="background: #f0f8ff; padding: 15px; border-radius: 5px;">
          <h3>{task['title']}</h3>
          <p><strong>Description:</strong> {task.get('description', 'N/A')}</p>
          <p><strong>Domain:</strong> {task.get('domain', 'N/A')}</p>
          <p><strong>Due Date:</strong> {due_date}</p>
          <p><strong>Priority:</strong> {task.get('priority', 'Medium')}</p>
          <p><strong>Completed by:</strong> {st.session_state.user_name}</p>
        </div>
        <p>Best regards,<br>TaskFlow Pro System</p>
      </body>
    </html>
    """

def create_escalation_email_html(task: Dict, mancom_member: Dict) -> str:
    """Create HTML email for task escalation"""
    due_date = task.get('due_date', 'Not specified')
    if isinstance(due_date, (datetime, pd.Timestamp)):
        due_date = due_date.strftime("%Y-%m-%d")
    
    return f"""
    <html>
      <body>
        <h2 style="color: #dc3545;">🚨 Task Escalation Required</h2>
        <p>Hello {mancom_member['mancom_member_name']},</p>
        <p>The following task requires your immediate attention as it is overdue:</p>
        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
          <h3>{task['title']}</h3>
          <p><strong>Description:</strong> {task.get('description', 'N/A')}</p>
          <p><strong>Domain:</strong> {task.get('domain', 'N/A')}</p>
          <p><strong>Due Date:</strong> {due_date}</p>
          <p><strong>Assigned To:</strong> {task.get('assigned_username', 'Unassigned')}</p>
          <p><strong>Current Status:</strong> {task.get('status', 'Open')}</p>
        </div>
        <p>Please follow up with the assigned team member to ensure timely completion.</p>
        <p>Best regards,<br>TaskFlow Pro System</p>
      </body>
    </html>
    """


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
# =============================================
# Streamlit UI Components
# =============================================

def render_login_form():
    """Render user login form"""
    st.title("🔐 TaskFlow Pro - Login")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
                return
            
            user = authenticate_user(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user_id = user['user_id']
                st.session_state.user_name = user['username']
                st.session_state.user_role = user['role']
                st.session_state.user_email = user['email']
                st.success(f"Welcome back, {user['username']}!")
                st.rerun()
            else:
                st.error("Invalid username or password")

def render_change_password_form():
    """Render change password form"""
    with st.expander("🔐 Change Password"):
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password"):
                if not current_password or not new_password:
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("New passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    if change_user_password(
                        st.session_state.user_id, 
                        current_password, 
                        new_password
                    ):
                        st.success("Password changed successfully!")
                    else:
                        st.error("Failed to change password")

def render_task_form(mode='create', task=None):
    """Render task creation/editing form"""
    users_df = get_all_users()
    domains_df = get_domains()
    
    with st.form(key=f"task_form_{mode}"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Task Title", value=task.get('title', '') if task else '')
            description = st.text_area("Description", value=task.get('description', '') if task else '')
            domain = st.selectbox(
                "Domain", 
                options=domains_df['domain_name'].tolist(),
                index=domains_df[domains_df['domain_name'] == task.get('domain', '')].index[0] if task and task.get('domain') else 0
            )
            assigned_to = st.selectbox(
                "Assign To",
                options=users_df[users_df['is_active'] == True]['username'].tolist(),
                index=users_df[users_df['username'] == task.get('assigned_username', '')].index[0] if task and task.get('assigned_username') else 0
            )
        
        with col2:
            priority = st.selectbox(
                "Priority",
                options=['high', 'medium', 'low'],
                index=['high', 'medium', 'low'].index(task.get('priority', 'medium')) if task else 1
            )
            due_date = st.date_input("Due Date", value=task.get('due_date', date.today()) if task else date.today())
            frequency = st.selectbox(
                "Frequency",
                options=['One-time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'],
                index=['One-time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'].index(task.get('frequency', 'One-time')) if task else 0
            )
            attachment = st.text_input("Attachment URL", value=task.get('attachment', '') if task else '')
        
        submitted = st.form_submit_button("Create Task" if mode == 'create' else "Update Task")
        
        if submitted:
            if not title:
                st.error("Task title is required")
                return False
            
            # Get user_id from username
            assigned_user_id = users_df[users_df['username'] == assigned_to]['user_id'].iloc[0]
            
            if mode == 'create':
                success = create_task(
                    title=title,
                    description=description,
                    domain=domain,
                    assigned_to=assigned_user_id,
                    priority=priority,
                    due_date=due_date,
                    frequency=frequency,
                    attachment=attachment,
                    created_by=st.session_state.user_id
                )
                if success:
                    st.success("Task created successfully!")
                    return True
                else:
                    st.error("Failed to create task")
                    return False
            else:
                # Update task logic would go here
                pass
    
    return False


# =============================================
# Main Application
# =============================================

def main():
    """Main application entry point"""
    
    # Initialize database
    init_database()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Check authentication
    if not st.session_state.authenticated:
        render_login_form()
        return
    
    # Main application after login
    st.sidebar.title(f"👋 Welcome, {st.session_state.user_name}!")
    st.sidebar.write(f"Role: {st.session_state.user_role}")
    
    # Navigation
    menu_options = ["📋 My Tasks", "➕ Create Task", "👥 User Management", "🏷️ Domain Management"]
    if st.session_state.user_role == 'admin':
        menu_options.extend(["📊 Admin Dashboard", "📧 Email Reports"])
    
    selected_menu = st.sidebar.selectbox("Navigation", menu_options)
    
    # Change password form in sidebar
    render_change_password_form()
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Main content area
    if selected_menu == "📋 My Tasks":
        st.title("My Tasks")
        tasks_df = get_tasks(
            user_id=st.session_state.user_id,
            role=st.session_state.user_role,
            include_closed=False
        )
        
        if tasks_df.empty:
            st.info("No tasks assigned to you.")
        else:
            st.dataframe(tasks_df, use_container_width=True)
    
    elif selected_menu == "➕ Create Task":
        st.title("Create New Task")
        render_task_form(mode='create')
    
    elif selected_menu == "👥 User Management" and st.session_state.user_role == 'admin':
        st.title("User Management")
        users_df = get_all_users()
        st.dataframe(users_df, use_container_width=True)
    
    elif selected_menu == "🏷️ Domain Management" and st.session_state.user_role == 'admin':
        st.title("Domain Management")
        domains_df = get_domains()
        st.dataframe(domains_df, use_container_width=True)
    
    elif selected_menu == "📊 Admin Dashboard" and st.session_state.user_role == 'admin':
        st.title("Admin Dashboard")
        # Dashboard implementation would go here
    
    elif selected_menu == "📧 Email Reports" and st.session_state.user_role == 'admin':
        st.title("Email Reports")
        # Email reporting implementation would go here

if __name__ == "__main__":
    st.set_page_config(
        page_title="TaskFlow Pro",
        page_icon="✅",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()
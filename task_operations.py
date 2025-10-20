
import pandas as pd
import json
from datetime import datetime, date
from database_connection import get_db_connection
import streamlit as st
from user_operations import get_admin_users
from typing import Optional, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

def get_task_by_id(task_id: int):
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

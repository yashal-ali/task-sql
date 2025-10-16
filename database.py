# # # # # from datetime import datetime, date
# # # # # import smtplib
# # # # # from email.mime.text import MIMEText
# # # # # from email.mime.multipart import MIMEMultipart
# # # # # import sqlite3
# # # # # import pandas as pd
# # # # # import os
# # # # # import streamlit as st


# # # # # # ✅ Database Connection
# # # # # def get_db_connection():
# # # # #     """
# # # # #     Creates a new SQLite connection.
# # # # #     Database file stored in the same directory as the app.
# # # # #     """
# # # # #     db_path = "task_management.db"
# # # # #     conn = sqlite3.connect(db_path, check_same_thread=False)
# # # # #     return conn


# # # # # # ✅ Initialize Database (create tables if not exist)
# # # # # def init_database():
# # # # #     conn = get_db_connection()
# # # # #     c = conn.cursor()
    
# # # # #     # Create tables
# # # # #     c.execute('''CREATE TABLE IF NOT EXISTS users (
# # # # #         user_id INTEGER PRIMARY KEY AUTOINCREMENT,
# # # # #         name TEXT NOT NULL,
# # # # #         email TEXT UNIQUE NOT NULL,
# # # # #         role TEXT NOT NULL
# # # # #     )''')

# # # # #     c.execute('''CREATE TABLE IF NOT EXISTS tasks (
# # # # #         task_id INTEGER PRIMARY KEY AUTOINCREMENT,
# # # # #         title TEXT NOT NULL,
# # # # #         description TEXT,
# # # # #         domain TEXT,
# # # # #         assigned_to INTEGER,
# # # # #         attachment TEXT,
# # # # #         status TEXT DEFAULT 'Pending',
# # # # #         due_date DATE,
# # # # #         frequency TEXT,
# # # # #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# # # # #         FOREIGN KEY (assigned_to) REFERENCES users(user_id)
# # # # #     )''')

# # # # #     c.execute('''CREATE TABLE IF NOT EXISTS comments (
# # # # #         comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
# # # # #         task_id INTEGER,
# # # # #         user_id INTEGER,
# # # # #         comment_text TEXT NOT NULL,
# # # # #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# # # # #         FOREIGN KEY (task_id) REFERENCES tasks(task_id),
# # # # #         FOREIGN KEY (user_id) REFERENCES users(user_id)
# # # # #     )''')

# # # # #     # Default Users
# # # # #     users = [
# # # # #         ('Admin','admin@company.com', 'admin'),
# # # # #         ('Yashal Ali', 'yashalalifarooqui30@gmail.com', 'user'),
# # # # #         ('Ali Yashal', 'aliyashal309@gmail.com', 'user'),
# # # # #         ('Farooqui Yashal', 'farooquiyashal@gmail.com', 'user')
# # # # #     ]

# # # # #     for user in users:
# # # # #         try:
# # # # #             c.execute('INSERT INTO users (name, email, role) VALUES (?, ?, ?)', user)
# # # # #         except sqlite3.IntegrityError:
# # # # #             pass

# # # # #     conn.commit()
# # # # #     conn.close()


# # # # # # ✅ Helper Functions
# # # # # def get_user_by_email(email):
# # # # #     conn = get_db_connection()
# # # # #     c = conn.cursor()
# # # # #     c.execute('SELECT * FROM users WHERE email = ?', (email,))
# # # # #     user = c.fetchone()
# # # # #     conn.close()
# # # # #     return user


# # # # # def get_all_users():
# # # # #     conn = get_db_connection()
# # # # #     df = pd.read_sql_query('SELECT * FROM users', conn)
# # # # #     conn.close()
# # # # #     return df


# # # # # def create_task(title, description, domain, assigned_to, attachment, status, due_date, frequency):
# # # # #     conn = get_db_connection()
# # # # #     c = conn.cursor()
# # # # #     c.execute('''INSERT INTO tasks (title, description, domain, assigned_to, attachment, status, due_date, frequency)
# # # # #                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
# # # # #               (title, description, domain, assigned_to, attachment, status, due_date, frequency))
# # # # #     conn.commit()
# # # # #     conn.close()


# # # # # def get_tasks(user_id=None, role='user'):
# # # # #     conn = get_db_connection()
# # # # #     if role == 'admin':
# # # # #         query = '''SELECT t.*, u.name as assigned_name, u.email as assigned_email,
# # # # #                    (SELECT COUNT(*) FROM comments WHERE task_id = t.task_id) as comment_count
# # # # #                    FROM tasks t
# # # # #                    LEFT JOIN users u ON t.assigned_to = u.user_id
# # # # #                    ORDER BY t.created_at DESC'''
# # # # #         df = pd.read_sql_query(query, conn)
# # # # #     else:
# # # # #         query = '''SELECT t.*, u.name as assigned_name, u.email as assigned_email,
# # # # #                    (SELECT COUNT(*) FROM comments WHERE task_id = t.task_id) as comment_count
# # # # #                    FROM tasks t
# # # # #                    LEFT JOIN users u ON t.assigned_to = u.user_id
# # # # #                    WHERE t.assigned_to = ?
# # # # #                    ORDER BY t.created_at DESC'''
# # # # #         df = pd.read_sql_query(query, conn, params=(user_id,))
# # # # #     conn.close()
# # # # #     return df


# # # # # def update_task_status(task_id, status):
# # # # #     conn = get_db_connection()
# # # # #     c = conn.cursor()
# # # # #     c.execute('UPDATE tasks SET status = ? WHERE task_id = ?', (status, task_id))
# # # # #     conn.commit()
# # # # #     conn.close()


# # # # # def update_task(task_id, title, description, domain, assigned_to, attachment, status, due_date, frequency):
# # # # #     conn = get_db_connection()
# # # # #     c = conn.cursor()
# # # # #     c.execute('''UPDATE tasks SET title=?, description=?, domain=?, assigned_to=?, 
# # # # #                  attachment=?, status=?, due_date=?, frequency=? WHERE task_id=?''',
# # # # #               (title, description, domain, assigned_to, attachment, status, due_date, frequency, task_id))
# # # # #     conn.commit()
# # # # #     conn.close()


# # # # # def delete_task(task_id):
# # # # #     conn = get_db_connection()
# # # # #     c = conn.cursor()
# # # # #     c.execute('DELETE FROM comments WHERE task_id = ?', (task_id,))
# # # # #     c.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
# # # # #     conn.commit()
# # # # #     conn.close()


# # # # # def get_comments(task_id):
# # # # #     conn = get_db_connection()
# # # # #     query = '''SELECT c.*, u.name, u.email FROM comments c
# # # # #                JOIN users u ON c.user_id = u.user_id
# # # # #                WHERE c.task_id = ?
# # # # #                ORDER BY c.created_at ASC'''
# # # # #     df = pd.read_sql_query(query, conn, params=(task_id,))
# # # # #     conn.close()
# # # # #     return df


# # # # # def add_comment(task_id, user_id, comment_text):
# # # # #     conn = get_db_connection()
# # # # #     c = conn.cursor()
# # # # #     c.execute('INSERT INTO comments (task_id, user_id, comment_text) VALUES (?, ?, ?)',
# # # # #               (task_id, user_id, comment_text))
# # # # #     conn.commit()
# # # # #     conn.close()


# # # # # def add_user(name, email, role='user'):
# # # # #     conn = get_db_connection()
# # # # #     c = conn.cursor()
# # # # #     try:
# # # # #         c.execute('INSERT INTO users (name, email, role) VALUES (?, ?, ?)', (name, email, role))
# # # # #         conn.commit()
# # # # #         conn.close()
# # # # #         return True
# # # # #     except sqlite3.IntegrityError:
# # # # #         conn.close()
# # # # #         return False


# # # # # # ✅ Email Summary Function
# # # # # def send_email_summary(user_email, user_name, tasks_df, sender_email, sender_password):
# # # # #     try:
# # # # #         msg = MIMEMultipart('alternative')
# # # # #         msg['Subject'] = f'Pending Tasks Summary – {datetime.now().strftime("%B %Y")}'
# # # # #         msg['From'] = sender_email
# # # # #         msg['To'] = user_email

# # # # #         html = f"""
# # # # #         <html>
# # # # #           <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1a202c; line-height: 1.6;">
# # # # #             <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
# # # # #               <div style="border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px;">
# # # # #                 <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 28px; font-weight: 700;">Task Summary Report</h1>
# # # # #                 <p style="color: #64748b; margin: 0; font-size: 16px;">Hello {user_name},</p>
# # # # #               </div>
# # # # #               <p style="color: #475569; font-size: 15px; margin-bottom: 25px;">Here are your pending tasks that require attention:</p>
# # # # #               <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
# # # # #                 <thead>
# # # # #                   <tr style="border-bottom: 2px solid #e2e8f0;">
# # # # #                     <th style="padding: 12px 8px; text-align: left;">Task</th>
# # # # #                     <th style="padding: 12px 8px; text-align: left;">Domain</th>
# # # # #                     <th style="padding: 12px 8px; text-align: left;">Due Date</th>
# # # # #                     <th style="padding: 12px 8px; text-align: left;">Frequency</th>
# # # # #                     <th style="padding: 12px 8px; text-align: center;">Comments</th>
# # # # #                   </tr>
# # # # #                 </thead>
# # # # #                 <tbody>
# # # # #         """

# # # # #         for _, task in tasks_df.iterrows():
# # # # #             html += f"""
# # # # #                   <tr style="border-bottom: 1px solid #e2e8f0;">
# # # # #                     <td style="padding: 12px 8px;"><b>{task['title']}</b><br><span style="color:#64748b;">{task['description'][:60]}...</span></td>
# # # # #                     <td style="padding: 12px 8px;">{task['domain']}</td>
# # # # #                     <td style="padding: 12px 8px;">{task['due_date']}</td>
# # # # #                     <td style="padding: 12px 8px;">{task['frequency']}</td>
# # # # #                     <td style="padding: 12px 8px; text-align:center; color:#2563eb;">{task['comment_count']}</td>
# # # # #                   </tr>
# # # # #             """

# # # # #         html += """
# # # # #                 </tbody>
# # # # #               </table>
# # # # #               <div style="background-color:#f8fafc; border-left:3px solid #2563eb; padding:16px; margin:25px 0;">
# # # # #                 <p style="margin:0;">Please update task statuses once completed.</p>
# # # # #               </div>
# # # # #               <div style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:10px; color:#64748b; font-size:13px;">
# # # # #                 <p>Best regards,</p>
# # # # #                 <p style="font-weight:600; color:#475569;">TaskFlow Pro Admin</p>
# # # # #               </div>
# # # # #             </div>
# # # # #           </body>
# # # # #         </html>
# # # # #         """

# # # # #         part = MIMEText(html, 'html')
# # # # #         msg.attach(part)

# # # # #         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
# # # # #             server.login(sender_email, sender_password)
# # # # #             server.send_message(msg)

# # # # #         return True

# # # # #     except Exception as e:
# # # # #         st.error(f"Error sending email to {user_email}: {str(e)}")
# # # # #         return False


# # # # from pymongo import MongoClient
# # # # import streamlit as st
# # # # import pandas as pd
# # # # from datetime import datetime, date
# # # # from bson.objectid import ObjectId


# # # # # ✅ MongoDB Connection
# # # # @st.cache_resource
# # # # def get_db_connection():
# # # #     """
# # # #     Creates a MongoDB connection using Streamlit secrets.
# # # #     Connection is cached to avoid multiple connections.
# # # #     """
# # # #     try:
# # # #         # Get connection string from Streamlit secrets
# # # #         mongo_uri = st.secrets["mongodb"]["uri"]
# # # #         client = MongoClient(mongo_uri)
        
# # # #         # Test connection
# # # #         client.admin.command('ping')
        
# # # #         # Return database
# # # #         db = client['task_management_db']  # Database name
# # # #         return db
# # # #     except Exception as e:
# # # #         st.error(f"Failed to connect to MongoDB: {str(e)}")
# # # #         return None


# # # # # ✅ Initialize Database (create collections and default users)
# # # # def init_database():
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return
    
# # # #     # Collections (equivalent to SQL tables)
# # # #     users_collection = db['users']
# # # #     tasks_collection = db['tasks']
# # # #     comments_collection = db['comments']
    
# # # #     # Create indexes for better performance
# # # #     users_collection.create_index('email', unique=True)
# # # #     tasks_collection.create_index('assigned_to')
# # # #     comments_collection.create_index('task_id')
    
# # # #     # Default Users
# # # #     default_users = [
# # # #         {'name': 'Admin', 'email': 'admin@company.com', 'role': 'admin'},
# # # #         {'name': 'Yashal Ali', 'email': 'yashalalifarooqui30@gmail.com', 'role': 'user'},
# # # #         {'name': 'Ali Yashal', 'email': 'aliyashal309@gmail.com', 'role': 'user'},
# # # #         {'name': 'Farooqui Yashal', 'email': 'farooquiyashal@gmail.com', 'role': 'user'}
# # # #     ]
    
# # # #     for user in default_users:
# # # #         try:
# # # #             # Check if user already exists
# # # #             if users_collection.find_one({'email': user['email']}) is None:
# # # #                 users_collection.insert_one(user)
# # # #         except Exception as e:
# # # #             pass  # User already exists


# # # # # ✅ Helper Functions
# # # # def get_user_by_email(email):
# # # #     """Get user by email address"""
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return None
    
# # # #     user = db['users'].find_one({'email': email})
# # # #     return user


# # # # def get_all_users():
# # # #     """Get all users as DataFrame"""
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return pd.DataFrame()
    
# # # #     users = list(db['users'].find())
    
# # # #     # Convert MongoDB _id to user_id for compatibility
# # # #     for user in users:
# # # #         user['user_id'] = str(user['_id'])
# # # #         del user['_id']
    
# # # #     return pd.DataFrame(users)


# # # # def create_task(title, description, domain, assigned_to, attachment, status, due_date, frequency):
# # # #     """Create a new task"""
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return
# # # #     if isinstance(due_date, date) and not isinstance(due_date, datetime):
# # # #         due_date = datetime.combine(due_date, datetime.min.time())
    
# # # #     task = {
# # # #         'title': title,
# # # #         'description': description,
# # # #         'domain': domain,
# # # #         'assigned_to': assigned_to,
# # # #         'attachment': attachment,
# # # #         'status': status,
# # # #         'due_date': due_date,
# # # #         'frequency': frequency,
# # # #         'created_at': datetime.now()
# # # #     }
    
# # # #     db['tasks'].insert_one(task)


# # # # def get_tasks(user_id=None, role='user'):
# # # #     """Get tasks with user info and comment counts"""
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return pd.DataFrame()
    
# # # #     # Build query based on role
# # # #     if role == 'admin':
# # # #         tasks = list(db['tasks'].find())
# # # #     else:
# # # #         tasks = list(db['tasks'].find({'assigned_to': user_id}))
    
# # # #     # Enrich tasks with user info and comment counts
# # # #     for task in tasks:
# # # #         task['task_id'] = str(task['_id'])
# # # #         del task['_id']
        
# # # #         # Get assigned user info
# # # #         if task.get('assigned_to'):
# # # #             user = db['users'].find_one({'_id': ObjectId(task['assigned_to'])})
# # # #             if user:
# # # #                 task['assigned_name'] = user.get('name', 'Unknown')
# # # #                 task['assigned_email'] = user.get('email', 'N/A')
# # # #             else:
# # # #                 task['assigned_name'] = 'Unknown'
# # # #                 task['assigned_email'] = 'N/A'
# # # #         else:
# # # #             task['assigned_name'] = 'Unassigned'
# # # #             task['assigned_email'] = 'N/A'
        
# # # #         # Count comments
# # # #         task['comment_count'] = db['comments'].count_documents({'task_id': task['task_id']})
    
# # # #     # Sort by created_at descending
# # # #     tasks.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
    
# # # #     return pd.DataFrame(tasks)


# # # # def update_task_status(task_id, status):
# # # #     """Update task status"""
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return
    
# # # #     db['tasks'].update_one(
# # # #         {'_id': ObjectId(task_id)},
# # # #         {'$set': {'status': status}}
# # # #     )


# # # # def update_task(task_id, title, description, domain, assigned_to, attachment, status, due_date, frequency):
# # # #     """Update entire task"""
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return
    
# # # #     db['tasks'].update_one(
# # # #         {'_id': ObjectId(task_id)},
# # # #         {'$set': {
# # # #             'title': title,
# # # #             'description': description,
# # # #             'domain': domain,
# # # #             'assigned_to': assigned_to,
# # # #             'attachment': attachment,
# # # #             'status': status,
# # # #             'due_date': due_date,
# # # #             'frequency': frequency
# # # #         }}
# # # #     )


# # # # def delete_task(task_id):
# # # #     """Delete task and its comments"""
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return
    
# # # #     # Delete all comments for this task
# # # #     db['comments'].delete_many({'task_id': task_id})
    
# # # #     # Delete the task
# # # #     db['tasks'].delete_one({'_id': ObjectId(task_id)})


# # # # def get_comments(task_id):
# # # #     """Get all comments for a task"""
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return pd.DataFrame()
    
# # # #     comments = list(db['comments'].find({'task_id': task_id}))
    
# # # #     # Enrich with user info
# # # #     for comment in comments:
# # # #         comment['comment_id'] = str(comment['_id'])
# # # #         del comment['_id']
        
# # # #         # Get user info
# # # #         user = db['users'].find_one({'_id': ObjectId(comment['user_id'])})
# # # #         if user:
# # # #             comment['name'] = user.get('name', 'Unknown')
# # # #             comment['email'] = user.get('email', 'N/A')
# # # #         else:
# # # #             comment['name'] = 'Unknown'
# # # #             comment['email'] = 'N/A'
    
# # # #     # Sort by created_at ascending
# # # #     comments.sort(key=lambda x: x.get('created_at', datetime.min))
    
# # # #     return pd.DataFrame(comments)


# # # # def add_comment(task_id, user_id, comment_text):
# # # #     """Add a comment to a task"""
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return
    
# # # #     comment = {
# # # #         'task_id': task_id,
# # # #         'user_id': user_id,
# # # #         'comment_text': comment_text,
# # # #         'created_at': datetime.now()
# # # #     }
    
# # # #     db['comments'].insert_one(comment)


# # # # def add_user(name, email, role='user'):
# # # #     """Add a new user"""
# # # #     db = get_db_connection()
# # # #     if db is None:
# # # #         return False
    
# # # #     try:
# # # #         user = {
# # # #             'name': name,
# # # #             'email': email,
# # # #             'role': role
# # # #         }
# # # #         db['users'].insert_one(user)
# # # #         return True
# # # #     except Exception as e:
# # # #         # Duplicate email
# # # #         return False


# # # # # ✅ Email Summary Function
# # # # def send_email_summary(user_email, user_name, tasks_df, sender_email, sender_password):
# # # #     try:
# # # #         msg = MIMEMultipart('alternative')
# # # #         msg['Subject'] = f'Pending Tasks Summary – {datetime.now().strftime("%B %Y")}'
# # # #         msg['From'] = sender_email
# # # #         msg['To'] = user_email

# # # #         html = f"""
# # # #         <html>
# # # #           <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1a202c; line-height: 1.6;">
# # # #             <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
# # # #               <div style="border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px;">
# # # #                 <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 28px; font-weight: 700;">Task Summary Report</h1>
# # # #                 <p style="color: #64748b; margin: 0; font-size: 16px;">Hello {user_name},</p>
# # # #               </div>
# # # #               <p style="color: #475569; font-size: 15px; margin-bottom: 25px;">Here are your pending tasks that require attention:</p>
# # # #               <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
# # # #                 <thead>
# # # #                   <tr style="border-bottom: 2px solid #e2e8f0;">
# # # #                     <th style="padding: 12px 8px; text-align: left;">Task</th>
# # # #                     <th style="padding: 12px 8px; text-align: left;">Domain</th>
# # # #                     <th style="padding: 12px 8px; text-align: left;">Due Date</th>
# # # #                     <th style="padding: 12px 8px; text-align: left;">Frequency</th>
# # # #                     <th style="padding: 12px 8px; text-align: center;">Comments</th>
# # # #                   </tr>
# # # #                 </thead>
# # # #                 <tbody>
# # # #         """

# # # #         for _, task in tasks_df.iterrows():
# # # #             html += f"""
# # # #                   <tr style="border-bottom: 1px solid #e2e8f0;">
# # # #                     <td style="padding: 12px 8px;"><b>{task['title']}</b><br><span style="color:#64748b;">{task['description'][:60]}...</span></td>
# # # #                     <td style="padding: 12px 8px;">{task['domain']}</td>
# # # #                     <td style="padding: 12px 8px;">{task['due_date']}</td>
# # # #                     <td style="padding: 12px 8px;">{task['frequency']}</td>
# # # #                     <td style="padding: 12px 8px; text-align:center; color:#2563eb;">{task['comment_count']}</td>
# # # #                   </tr>
# # # #             """

# # # #         html += """
# # # #                 </tbody>
# # # #               </table>
# # # #               <div style="background-color:#f8fafc; border-left:3px solid #2563eb; padding:16px; margin:25px 0;">
# # # #                 <p style="margin:0;">Please update task statuses once completed.</p>
# # # #               </div>
# # # #               <div style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:10px; color:#64748b; font-size:13px;">
# # # #                 <p>Best regards,</p>
# # # #                 <p style="font-weight:600; color:#475569;">TaskFlow Pro Admin</p>
# # # #               </div>
# # # #             </div>
# # # #           </body>
# # # #         </html>
# # # #         """

# # # #         part = MIMEText(html, 'html')
# # # #         msg.attach(part)

# # # #         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
# # # #             server.login(sender_email, sender_password)
# # # #             server.send_message(msg)

# # # #         return True

# # # #     except Exception as e:
# # # #         st.error(f"Error sending email to {user_email}: {str(e)}")
# # # #         return False

# # # import pyodbc
# # # import streamlit as st

# # # from pymongo import MongoClient
# # # import streamlit as st
# # # import pandas as pd
# # # from datetime import datetime, date
# # # from bson.objectid import ObjectId

# # # @st.cache_resource
# # # def get_db_connection():
# # #     try:
# # #         conn = pyodbc.connect(
# # #             "DRIVER={ODBC Driver 17 for SQL Server};"
# # #             "SERVER=localhost,1433;"
# # #             "DATABASE=task_management_db;"
# # #             "UID=sa;"
# # #             "PWD=Yashal309;"
# # #         )
# # #         return conn
# # #     except Exception as e:
# # #         st.error(f"Failed to connect to SQL Server: {str(e)}")
# # #         return None

# # # def add_user(name, email, role='user'):
# # #     conn = get_db_connection()
# # #     if conn is None:
# # #         return False
    
# # #     cursor = conn.cursor()
# # #     try:
# # #         cursor.execute("""
# # #             INSERT INTO users (name, email, role)
# # #             VALUES (?, ?, ?)
# # #         """, (name, email, role))
# # #         conn.commit()
# # #         return True
# # #     except Exception as e:
# # #         st.error(f"Error adding user: {e}")
# # #         return False
# # #     finally:
# # #         cursor.close()

# # # def get_all_users():
# # #     conn = get_db_connection()
# # #     if conn is None:
# # #         return pd.DataFrame()

# # #     query = "SELECT user_id, name, email, role FROM users"
# # #     df = pd.read_sql(query, conn)
# # #     return df

# # # def create_task(title, description, domain, assigned_to, attachment, status, due_date, frequency):
# # #     conn = get_db_connection()
# # #     if conn is None:
# # #         return
# # #     cursor = conn.cursor()
# # #     cursor.execute("""
# # #         INSERT INTO tasks (title, description, domain, assigned_to, attachment, status, due_date, frequency)
# # #         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
# # #     """, (title, description, domain, assigned_to, attachment, status, due_date, frequency))
# # #     conn.commit()
# # #     cursor.close()

# # # def get_tasks(user_id=None, role='user'):
# # #     conn = get_db_connection()
# # #     if conn is None:
# # #         return pd.DataFrame()

# # #     if role == 'admin':
# # #         query = """
# # #         SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
# # #                (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
# # #         FROM tasks t
# # #         LEFT JOIN users u ON t.assigned_to = u.user_id
# # #         ORDER BY t.created_at DESC
# # #         """
# # #         df = pd.read_sql(query, conn)
# # #     else:
# # #         query = f"""
# # #         SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
# # #                (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
# # #         FROM tasks t
# # #         LEFT JOIN users u ON t.assigned_to = u.user_id
# # #         WHERE t.assigned_to = {user_id}
# # #         ORDER BY t.created_at DESC
# # #         """
# # #         df = pd.read_sql(query, conn)

# # #     return df

# # import pyodbc
# # import streamlit as st
# # import pandas as pd
# # from datetime import datetime, date
# # from email.mime.multipart import MIMEMultipart
# # from email.mime.text import MIMEText
# # import smtplib


# # # ✅ MSSQL Connection
# # @st.cache_resource
# # def get_db_connection():
# #     """
# #     Creates a MSSQL connection using Streamlit secrets or local config.
# #     Connection is cached to avoid multiple connections.
# #     """
# #     try:
# #         conn = pyodbc.connect(
# #             "DRIVER={ODBC Driver 17 for SQL Server};"
# #             "SERVER=localhost,1433;"
# #             "DATABASE=task_management_db;"
# #             "UID=sa;"
# #             "PWD=Yashal309;"
# #         )
# #         return conn
# #     except Exception as e:
# #         st.error(f"Failed to connect to SQL Server: {str(e)}")
# #         return None


# # # ✅ Initialize Database (create tables and default users)
# # def init_database():
# #     conn = get_db_connection()
# #     if conn is None:
# #         return
    
# #     cursor = conn.cursor()
    
# #     try:
# #         # Create users table
# #         cursor.execute("""
# #             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
# #             CREATE TABLE users (
# #                 user_id INT PRIMARY KEY IDENTITY(1,1),
# #                 name NVARCHAR(100) NOT NULL,
# #                 email NVARCHAR(100) UNIQUE NOT NULL,
# #                 role NVARCHAR(20) NOT NULL
# #             )
# #         """)
        
# #         # Create tasks table
# #         cursor.execute("""
# #             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
# #             CREATE TABLE tasks (
# #                 task_id INT PRIMARY KEY IDENTITY(1,1),
# #                 title NVARCHAR(255) NOT NULL,
# #                 description NVARCHAR(MAX),
# #                 domain NVARCHAR(100),
# #                 assigned_to INT,
# #                 attachment NVARCHAR(MAX),
# #                 status NVARCHAR(50),
# #                 due_date DATETIME,
# #                 frequency NVARCHAR(50),
# #                 created_at DATETIME DEFAULT GETDATE(),
# #                 FOREIGN KEY (assigned_to) REFERENCES users(user_id)
# #             )
# #         """)
        
# #         # Create comments table
# #         cursor.execute("""
# #             IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='comments' AND xtype='U')
# #             CREATE TABLE comments (
# #                 comment_id INT PRIMARY KEY IDENTITY(1,1),
# #                 task_id INT NOT NULL,
# #                 user_id INT NOT NULL,
# #                 comment_text NVARCHAR(MAX),
# #                 created_at DATETIME DEFAULT GETDATE(),
# #                 FOREIGN KEY (task_id) REFERENCES tasks(task_id),
# #                 FOREIGN KEY (user_id) REFERENCES users(user_id)
# #             )
# #         """)
        
# #         # Create indexes for better performance (only if they don't exist)
# #         cursor.execute("""
# #             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_email' AND object_id=OBJECT_ID('users'))
# #             CREATE INDEX idx_email ON users(email)
# #         """)
# #         cursor.execute("""
# #             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_assigned_to' AND object_id=OBJECT_ID('tasks'))
# #             CREATE INDEX idx_assigned_to ON tasks(assigned_to)
# #         """)
# #         cursor.execute("""
# #             IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_task_id' AND object_id=OBJECT_ID('comments'))
# #             CREATE INDEX idx_task_id ON comments(task_id)
# #         """)
        
# #         conn.commit()
        
# #         # Default Users
# #         default_users = [
# #             ('Admin', 'yashal.ali@nfoods.com', 'admin'),
# #             ('Yashal Ali', 'yashalalifarooqui30@gmail.com', 'user'),
# #             ('Ali Yashal', 'aliyashal309@gmail.com', 'user'),
# #             ('Farooqui Yashal', 'farooquiyashal@gmail.com', 'user')
# #         ]
        
# #         for name, email, role in default_users:
# #             try:
# #                 cursor.execute("""
# #                     INSERT INTO users (name, email, role)
# #                     VALUES (?, ?, ?)
# #                 """, (name, email, role))
# #             except Exception:
# #                 pass  # User already exists
        
# #         conn.commit()
        
# #     except Exception as e:
# #         st.error(f"Error initializing database: {str(e)}")
# #     finally:
# #         cursor.close()


# # # ✅ Helper Functions
# # def get_user_by_email(email):
# #     """Get user by email address"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return None
    
# #     try:
# #         query = "SELECT user_id, name, email, role FROM users WHERE email = ?"
# #         df = pd.read_sql(query, conn, params=(email,))
# #         if df.empty:
# #             return None
# #         return df.iloc[0].to_dict()
# #     except Exception as e:
# #         st.error(f"Error fetching user: {str(e)}")
# #         return None


# # def get_all_users():
# #     """Get all users as DataFrame"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return pd.DataFrame()
    
# #     try:
# #         query = "SELECT user_id, name, email, role FROM users"
# #         df = pd.read_sql(query, conn)
# #         return df
# #     except Exception as e:
# #         st.error(f"Error fetching users: {str(e)}")
# #         return pd.DataFrame()

# # def get_admin_users():
# #     """Get all admin users"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return pd.DataFrame()
    
# #     try:
# #         query = "SELECT user_id, name, email, role FROM users WHERE role = 'admin'"
# #         df = pd.read_sql(query, conn)
# #         return df
# #     except Exception as e:
# #         st.error(f"Error fetching admin users: {str(e)}")
# #         return pd.DataFrame()


# # def create_task(title, description, domain, assigned_to, attachment, status, due_date, frequency):
# #     """Create a new task"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return
    
# #     if isinstance(due_date, date) and not isinstance(due_date, datetime):
# #         due_date = datetime.combine(due_date, datetime.min.time())
    
# #     cursor = conn.cursor()
# #     try:
# #         cursor.execute("""
# #             INSERT INTO tasks (title, description, domain, assigned_to, attachment, status, due_date, frequency, created_at)
# #             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
# #         """, (title, description, domain, assigned_to, attachment, status, due_date, frequency, datetime.now()))
# #         conn.commit()
# #     except Exception as e:
# #         st.error(f"Error creating task: {str(e)}")
# #     finally:
# #         cursor.close()


# # def get_tasks(user_id=None, role='user'):
# #     """Get tasks with user info and comment counts"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return pd.DataFrame()
    
# #     try:
# #         if role == 'admin':
# #             query = """
# #             SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
# #                    (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
# #             FROM tasks t
# #             LEFT JOIN users u ON t.assigned_to = u.user_id
# #             ORDER BY t.created_at DESC
# #             """
# #             df = pd.read_sql(query, conn)
# #         else:
# #             query = """
# #             SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
# #                    (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
# #             FROM tasks t
# #             LEFT JOIN users u ON t.assigned_to = u.user_id
# #             WHERE t.assigned_to = ?
# #             ORDER BY t.created_at DESC
# #             """
# #             df = pd.read_sql(query, conn, params=(user_id,))
        
# #         return df
# #     except Exception as e:
# #         st.error(f"Error fetching tasks: {str(e)}")
# #         return pd.DataFrame()


# # def get_task_by_id(task_id):
# #     """Get a specific task by ID"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return None
    
# #     try:
# #         query = """
# #         SELECT t.*, u.name AS assigned_name, u.email AS assigned_email
# #         FROM tasks t
# #         LEFT JOIN users u ON t.assigned_to = u.user_id
# #         WHERE t.task_id = ?
# #         """
# #         df = pd.read_sql(query, conn, params=(task_id,))
# #         if df.empty:
# #             return None
# #         return df.iloc[0].to_dict()
# #     except Exception as e:
# #         st.error(f"Error fetching task: {str(e)}")
# #         return None


# # def update_task_status(task_id, status):
# #     """Update task status"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return
    
# #     cursor = conn.cursor()
# #     try:
# #         cursor.execute("""
# #             UPDATE tasks
# #             SET status = ?
# #             WHERE task_id = ?
# #         """, (status, task_id))
# #         conn.commit()
# #     except Exception as e:
# #         st.error(f"Error updating task status: {str(e)}")
# #     finally:
# #         cursor.close()


# # def update_task(task_id, title, description, domain, assigned_to, attachment, status, due_date, frequency):
# #     """Update entire task"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return
    
# #     cursor = conn.cursor()
# #     try:
# #         cursor.execute("""
# #             UPDATE tasks
# #             SET title = ?, description = ?, domain = ?, assigned_to = ?, 
# #                 attachment = ?, status = ?, due_date = ?, frequency = ?
# #             WHERE task_id = ?
# #         """, (title, description, domain, assigned_to, attachment, status, due_date, frequency, task_id))
# #         conn.commit()
# #     except Exception as e:
# #         st.error(f"Error updating task: {str(e)}")
# #     finally:
# #         cursor.close()


# # def delete_task(task_id):
# #     """Delete task and its comments"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return
    
# #     cursor = conn.cursor()
# #     try:
# #         # Delete all comments for this task
# #         cursor.execute("DELETE FROM comments WHERE task_id = ?", (task_id,))
        
# #         # Delete the task
# #         cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        
# #         conn.commit()
# #     except Exception as e:
# #         st.error(f"Error deleting task: {str(e)}")
# #     finally:
# #         cursor.close()


# # def get_comments(task_id):
# #     """Get all comments for a task"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return pd.DataFrame()
    
# #     try:
# #         query = """
# #         SELECT c.comment_id, c.task_id, c.user_id, c.comment_text, c.created_at,
# #                u.name, u.email
# #         FROM comments c
# #         LEFT JOIN users u ON c.user_id = u.user_id
# #         WHERE c.task_id = ?
# #         ORDER BY c.created_at ASC
# #         """
# #         df = pd.read_sql(query, conn, params=(task_id,))
# #         return df
# #     except Exception as e:
# #         st.error(f"Error fetching comments: {str(e)}")
# #         return pd.DataFrame()


# # def add_comment(task_id, user_id, comment_text):
# #     """Add a comment to a task"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return
    
# #     cursor = conn.cursor()
# #     try:
# #         cursor.execute("""
# #             INSERT INTO comments (task_id, user_id, comment_text, created_at)
# #             VALUES (?, ?, ?, ?)
# #         """, (task_id, user_id, comment_text, datetime.now()))
# #         conn.commit()
# #     except Exception as e:
# #         st.error(f"Error adding comment: {str(e)}")
# #     finally:
# #         cursor.close()


# # def add_user(name, email, role='user'):
# #     """Add a new user"""
# #     conn = get_db_connection()
# #     if conn is None:
# #         return False
    
# #     cursor = conn.cursor()
# #     try:
# #         cursor.execute("""
# #             INSERT INTO users (name, email, role)
# #             VALUES (?, ?, ?)
# #         """, (name, email, role))
# #         conn.commit()
# #         return True
# #     except Exception as e:
# #         st.error(f"Error adding user: {str(e)}")
# #         return False
# #     finally:
# #         cursor.close()


# # # ✅ Email Summary Function
# # def send_email_summary(user_email, user_name, tasks_df, sender_email, sender_password):
# #     """Send email summary of pending tasks"""
# #     try:
# #         msg = MIMEMultipart('alternative')
# #         msg['Subject'] = f'Pending Tasks Summary – {datetime.now().strftime("%B %Y")}'
# #         msg['From'] = sender_email
# #         msg['To'] = user_email

# #         html = f"""
# #         <html>
# #           <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1a202c; line-height: 1.6;">
# #             <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
# #               <div style="border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px;">
# #                 <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 28px; font-weight: 700;">Task Summary Report</h1>
# #                 <p style="color: #64748b; margin: 0; font-size: 16px;">Hello {user_name},</p>
# #               </div>
# #               <p style="color: #475569; font-size: 15px; margin-bottom: 25px;">Here are your pending tasks that require attention:</p>
# #               <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
# #                 <thead>
# #                   <tr style="border-bottom: 2px solid #e2e8f0;">
# #                     <th style="padding: 12px 8px; text-align: left;">Task</th>
# #                     <th style="padding: 12px 8px; text-align: left;">Domain</th>
# #                     <th style="padding: 12px 8px; text-align: left;">Due Date</th>
# #                     <th style="padding: 12px 8px; text-align: left;">Frequency</th>
# #                     <th style="padding: 12px 8px; text-align: center;">Comments</th>
# #                   </tr>
# #                 </thead>
# #                 <tbody>
# #         """

# #         for _, task in tasks_df.iterrows():
# #             due_date_str = task['due_date'].strftime("%Y-%m-%d") if pd.notna(task['due_date']) else "N/A"
# #             html += f"""
# #                   <tr style="border-bottom: 1px solid #e2e8f0;">
# #                     <td style="padding: 12px 8px;"><b>{task['title']}</b><br><span style="color:#64748b;">{str(task['description'])[:60]}...</span></td>
# #                     <td style="padding: 12px 8px;">{task['domain']}</td>
# #                     <td style="padding: 12px 8px;">{due_date_str}</td>
# #                     <td style="padding: 12px 8px;">{task['frequency']}</td>
# #                     <td style="padding: 12px 8px; text-align:center; color:#2563eb;">{task['comment_count']}</td>
# #                   </tr>
# #             """

# #         html += """
# #                 </tbody>
# #               </table>
# #               <div style="background-color:#f8fafc; border-left:3px solid #2563eb; padding:16px; margin:25px 0;">
# #                 <p style="margin:0;">Please update task statuses once completed.</p>
# #               </div>
# #               <div style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:10px; color:#64748b; font-size:13px;">
# #                 <p>Best regards,</p>
# #                 <p style="font-weight:600; color:#475569;">TaskFlow Pro Admin</p>
# #               </div>
# #             </div>
# #           </body>
# #         </html>
# #         """

# #         part = MIMEText(html, 'html')
# #         msg.attach(part)

# #         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
# #             server.login(sender_email, sender_password)
# #             server.send_message(msg)

# #         return True

# #     except Exception as e:
# #         st.error(f"Error sending email to {user_email}: {str(e)}")
# #         return False


# # # ✅ Task Completion Notification Function
# # def send_task_completion_notification(task, user_name, sender_email, sender_password):
# #     """Send notification to admins when a task is completed"""
# #     try:
# #         # Get all admin users
# #         admin_users = get_admin_users()
# #         print(admin_users)
# #         st.write(admin_users)
        
# #         if admin_users.empty:
# #             st.error("No admin users found to send notification")
# #             return False
        
# #         success_count = 0
        
# #         for _, admin in admin_users.iterrows():
# #             msg = MIMEMultipart('alternative')
# #             msg['Subject'] = f'Task Completed: {task["title"]}'
# #             msg['From'] = sender_email
# #             msg['To'] = admin['email']
            
# #             due_date_str = task['due_date'].strftime("%Y-%m-%d") if pd.notna(task['due_date']) else "Not specified"
# #             completion_time = datetime.now().strftime("%Y-%m-%d at %I:%M %p")
            
# #             html = f"""
# #             <html>
# #               <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1a202c; line-height: 1.6;">
# #                 <div style="max-width: 700px; margin: 0 auto; padding: 25px;">
# #                   <div style="border-bottom: 3px solid #10b981; padding-bottom: 20px; margin-bottom: 30px;">
# #                     <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 26px; font-weight: 700;">Task Completed Successfully</h1>
# #                     <p style="color: #64748b; margin: 0; font-size: 16px;">Great news! A task has been marked as completed.</p>
# #                   </div>
                  
# #                   <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin-bottom: 25px;">
# #                     <h2 style="color: #15803d; margin: 0 0 15px 0; font-size: 20px; font-weight: 600;">Task Details</h2>
                    
# #                     <table style="width: 100%; border-collapse: collapse;">
# #                       <tr>
# #                         <td style="padding: 8px 0; color: #475569; font-weight: 600; width: 120px;">Task Title:</td>
# #                         <td style="padding: 8px 0; color: #1e293b;">{task['title']}</td>
# #                       </tr>
# #                       <tr>
# #                         <td style="padding: 8px 0; color: #475569; font-weight: 600;">Description:</td>
# #                         <td style="padding: 8px 0; color: #1e293b;">{task['description']}</td>
# #                       </tr>
# #                       <tr>
# #                         <td style="padding: 8px 0; color: #475569; font-weight: 600;">Completed By:</td>
# #                         <td style="padding: 8px 0; color: #1e293b;">{user_name}</td>
# #                       </tr>
# #                       <tr>
# #                         <td style="padding: 8px 0; color: #475569; font-weight: 600;">Domain:</td>
# #                         <td style="padding: 8px 0; color: #1e293b;">{task['domain']}</td>
# #                       </tr>
# #                       <tr>
# #                         <td style="padding: 8px 0; color: #475569; font-weight: 600;">Due Date:</td>
# #                         <td style="padding: 8px 0; color: #1e293b;">{due_date_str}</td>
# #                       </tr>
# #                       <tr>
# #                         <td style="padding: 8px 0; color: #475569; font-weight: 600;">Frequency:</td>
# #                         <td style="padding: 8px 0; color: #1e293b;">{task['frequency']}</td>
# #                       </tr>
# #                       <tr>
# #                         <td style="padding: 8px 0; color: #475569; font-weight: 600;">Completed On:</td>
# #                         <td style="padding: 8px 0; color: #1e293b; font-weight: 600;">{completion_time}</td>
# #                       </tr>
# #                     </table>
# #                   </div>
                  
# #                   <div style="background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 16px; margin-bottom: 25px;">
# #                     <p style="margin: 0; color: #1e40af; font-size: 14px;">
# #                       <strong>Note:</strong> This task has been successfully completed and is now ready for your review.
# #                     </p>
# #                   </div>
                  
# #                   <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
# #                     <p style="color: #64748b; margin: 0 0 10px 0; font-size: 14px;">
# #                       This is an automated notification from TaskFlow Pro System
# #                     </p>
# #                     <p style="color: #94a3b8; margin: 0; font-size: 12px;">
# #                       Please do not reply to this email
# #                     </p>
# #                   </div>
# #                 </div>
# #               </body>
# #             </html>
# #             """
            
# #             part = MIMEText(html, 'html')
# #             msg.attach(part)
            
# #             try:
# #                 with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
# #                     server.login(sender_email, sender_password)
# #                     server.send_message(msg)
# #                 success_count += 1
# #             except Exception as e:
# #                 st.error(f"Error sending completion notification to {admin['email']}: {str(e)}")
        
# #         return success_count > 0
        
# #     except Exception as e:
# #         st.error(f"Error sending task completion notifications: {str(e)}")
# #         return False


# import pyodbc
# import streamlit as st
# import pandas as pd
# from datetime import datetime, date, timedelta
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import smtplib
# import os

# # ✅ MSSQL Connection
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

# # ✅ Initialize Database (create tables and default data)
# def init_database():
#     conn = get_db_connection()
#     if conn is None:
#         return
    
#     cursor = conn.cursor()
    
#     try:
#         # Create users table WITHOUT is_active column for now
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
        
#         # Create domains table WITHOUT is_active column for now
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
        
#         # Insert default users
#         default_users = [
#             ('Admin User', 'admin@nfoods.com', 'admin'),
#             ('Yashal Ali', 'yashal.ali@nfoods.com', 'user'),
#             ('Ali', 'aliyashal309@gmail.com', 'user'),
#         ]
        
#         for name, email, role in default_users:
#             try:
#                 cursor.execute("""
#                     INSERT INTO users (name, email, role)
#                     VALUES (?, ?, ?)
#                 """, (name, email, role))
#             except Exception as e:
#                 print(f"User {email} already exists or error: {e}")
        
#         # Insert default domains with mancom members
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
#                     INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
#                     VALUES (?, ?, ?)
#                 """, (domain_name, mancom_name, mancom_email))
#             except Exception as e:
#                 print(f"Domain {domain_name} already exists or error: {e}")
        
#         conn.commit()
#         print("✅ Database initialized successfully!")
        
#     except Exception as e:
#         st.error(f"Error initializing database: {str(e)}")
#         print(f"Database initialization error: {e}")
#     finally:
#         cursor.close()
# # ✅ Helper Functions
# # ✅ Helper Functions
# def get_user_by_email(email):
#     """Get user by email address"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         # Remove AND is_active = 1 from the query
#         query = "SELECT user_id, name, email, role FROM users WHERE email = ?"
#         df = pd.read_sql(query, conn, params=(email,))
#         if df.empty:
#             return None
#         return df.iloc[0].to_dict()
#     except Exception as e:
#         st.error(f"Error fetching user: {str(e)}")
#         return None

# def get_all_users(include_inactive=False):
#     """Get all users as DataFrame"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         # Remove is_active references
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
#         # Remove AND is_active = 1
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
#         # Remove WHERE is_active = 1
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
#         # Remove AND is_active = 1
#         query = "SELECT mancom_member_name, mancom_member_email FROM domains WHERE domain_name = ?"
#         df = pd.read_sql(query, conn, params=(domain_name,))
#         if df.empty:
#             return None
#         return df.iloc[0].to_dict()
#     except Exception as e:
#         st.error(f"Error fetching mancom member: {str(e)}")
#         return None

# def get_domain_by_id(domain_id):
#     """Get domain by ID"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         # Remove AND is_active = 1
#         query = """
#         SELECT domain_id, domain_name, mancom_member_name, mancom_member_email 
#         FROM domains 
#         WHERE domain_id = ?
#         """
#         df = pd.read_sql(query, conn, params=(domain_id,))
#         if df.empty:
#             return None
#         return df.iloc[0].to_dict()
#     except Exception as e:
#         st.error(f"Error fetching domain: {str(e)}")
#         return None
# def create_task(title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, created_by):
#     """Create a new task"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     if isinstance(due_date, date) and not isinstance(due_date, datetime):
#         due_date = datetime.combine(due_date, datetime.min.time())
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             INSERT INTO tasks (title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, created_by)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """, (title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, created_by))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error creating task: {str(e)}")
#         return False
#     finally:
#         cursor.close()

# def get_tasks(user_id=None, role='user', include_completed=True):
#     """Get tasks with user info and comment counts"""
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
    
#     try:
#         if role == 'admin':
#             if include_completed:
#                 query = """
#                 SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                        (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#                 FROM tasks t
#                 LEFT JOIN users u ON t.assigned_to = u.user_id
#                 ORDER BY t.due_date ASC, t.priority DESC
#                 """
#                 df = pd.read_sql(query, conn)
#             else:
#                 query = """
#                 SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                        (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#                 FROM tasks t
#                 LEFT JOIN users u ON t.assigned_to = u.user_id
#                 WHERE t.status != 'Completed'
#                 ORDER BY t.due_date ASC, t.priority DESC
#                 """
#                 df = pd.read_sql(query, conn)
#         else:
#             if include_completed:
#                 query = """
#                 SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                        (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#                 FROM tasks t
#                 LEFT JOIN users u ON t.assigned_to = u.user_id
#                 WHERE t.assigned_to = ?
#                 ORDER BY t.due_date ASC, t.priority DESC
#                 """
#                 df = pd.read_sql(query, conn, params=(user_id,))
#             else:
#                 query = """
#                 SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                        (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
#                 FROM tasks t
#                 LEFT JOIN users u ON t.assigned_to = u.user_id
#                 WHERE t.assigned_to = ? AND t.status != 'Completed'
#                 ORDER BY t.due_date ASC, t.priority DESC
#                 """
#                 df = pd.read_sql(query, conn, params=(user_id,))
        
#         return df
#     except Exception as e:
#         st.error(f"Error fetching tasks: {str(e)}")
#         return pd.DataFrame()

# def get_task_by_id(task_id):
#     """Get a specific task by ID"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         query = """
#         SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
#                creator.name AS created_by_name
#         FROM tasks t
#         LEFT JOIN users u ON t.assigned_to = u.user_id
#         LEFT JOIN users creator ON t.created_by = creator.user_id
#         WHERE t.task_id = ?
#         """
#         df = pd.read_sql(query, conn, params=(task_id,))
#         if df.empty:
#             return None
#         return df.iloc[0].to_dict()
#     except Exception as e:
#         st.error(f"Error fetching task: {str(e)}")
#         return None

# def update_task_status(task_id, status, changed_by=None):
#     """Update task status"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Get old status for history
#         cursor.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,))
#         old_status = cursor.fetchone()[0]
        
#         # Update task
#         cursor.execute("""
#             UPDATE tasks
#             SET status = ?, updated_at = GETDATE()
#             WHERE task_id = ?
#         """, (status, task_id))
        
#         # Add to history
#         if changed_by:
#             cursor.execute("""
#                 INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
#                 VALUES (?, 'status', ?, ?, ?)
#             """, (task_id, old_status, status, changed_by))
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error updating task status: {str(e)}")
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
#         old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = old_values
        
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
#         return False
#     finally:
#         cursor.close()

# def delete_user(user_id):
#     """Delete a user (hard delete for now)"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # First, update tasks assigned to this user to NULL
#         cursor.execute("UPDATE tasks SET assigned_to = NULL WHERE assigned_to = ?", (user_id,))
        
#         # Delete user's comments
#         cursor.execute("DELETE FROM comments WHERE user_id = ?", (user_id,))
        
#         # Delete the user (hard delete since no is_active column)
#         cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error deleting user: {str(e)}")
#         return False
#     finally:
#         cursor.close()

# def delete_domain(domain_id):
#     """Delete a domain (hard delete for now)"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         # Hard delete since no is_active column
#         cursor.execute("DELETE FROM domains WHERE domain_id = ?", (domain_id,))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error deleting domain: {str(e)}")
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
#         return df
#     except Exception as e:
#         st.error(f"Error fetching overdue tasks: {str(e)}")
#         return pd.DataFrame()

# def get_tasks_due_soon(days=15):
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

# # ✅ Email Functions
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
#             due_date_str = task['due_date'].strftime("%Y-%m-%d") if pd.notna(task['due_date']) else "N/A"
#             priority_class = f"priority-{task['priority'].lower()}" if 'priority' in task else "priority-medium"
#             status_class = f"status-{task['status'].lower().replace(' ', '')}"
            
#             html += f"""
#                   <tr>
#                     <td><b>{task['title']}</b><br><span style="color:#64748b; font-size: 12px;">{str(task['description'])[:80]}...</span></td>
#                     <td>{task['domain']}</td>
#                     <td><span class="{priority_class}">{task.get('priority', 'Medium')}</span></td>
#                     <td>{due_date_str}</td>
#                     <td><span class="{status_class}">{task['status']}</span></td>
#                     <td style="text-align:center; color:#2563eb; font-weight: bold;">{task['comment_count']}</td>
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
#         mancom_member = get_mancom_member_by_domain(task['domain'])
#         if not mancom_member:
#             st.error(f"No mancom member found for domain: {task['domain']}")
#             return False
        
#         msg = MIMEMultipart('alternative')
#         msg['Subject'] = f'🚨 ESCALATION: Overdue Task - {task["title"]}'
#         msg['From'] = sender_email
#         msg['To'] = mancom_member['mancom_member_email']
        
#         due_date_str = task['due_date'].strftime("%Y-%m-%d") if pd.notna(task['due_date']) else "Not specified"
#         overdue_days = (datetime.now().date() - task['due_date'].date()).days if task['due_date'] else 0
        
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
#                     <td style="color: #1e293b;">{task['title']}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Description:</td>
#                     <td style="color: #1e293b;">{task['description']}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Assigned To:</td>
#                     <td style="color: #1e293b;">{task.get('assigned_name', 'Unassigned')}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Domain:</td>
#                     <td style="color: #1e293b;">{task['domain']}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Due Date:</td>
#                     <td style="color: #1e293b;">{due_date_str}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Current Status:</td>
#                     <td style="color: #dc2626; font-weight: 600;">{task['status']}</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Overdue By:</td>
#                     <td style="color: #dc2626; font-weight: 600;">{overdue_days} days</td>
#                   </tr>
#                   <tr>
#                     <td style="color: #475569; font-weight: 600;">Priority:</td>
#                     <td style="color: #dc2626; font-weight: 600;">{task.get('priority', 'Medium')}</td>
#                   </tr>
#                 </table>
#               </div>
              
#               <div class="info-box">
#                 <p style="margin: 0; color: #1e40af; font-size: 14px; font-weight: 500;">
#                   <strong>Action Required:</strong> This task is overdue and requires your attention as the Mancom member for the {task['domain']} domain. 
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
    

# def get_domain_by_id(domain_id):
#     """Get domain by ID"""
#     conn = get_db_connection()
#     if conn is None:
#         return None
    
#     try:
#         query = """
#         SELECT domain_id, domain_name, mancom_member_name, mancom_member_email 
#         FROM domains 
#         WHERE domain_id = ? AND is_active = 1
#         """
#         df = pd.read_sql(query, conn, params=(domain_id,))
#         if df.empty:
#             return None
#         return df.iloc[0].to_dict()
#     except Exception as e:
#         st.error(f"Error fetching domain: {str(e)}")
#         return None

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
#         return False
#     finally:
#         cursor.close()

# def delete_domain(domain_id):
#     """Soft delete a domain"""
#     conn = get_db_connection()
#     if conn is None:
#         return False
    
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             UPDATE domains 
#             SET is_active = 0 
#             WHERE domain_id = ?
#         """, (domain_id,))
#         conn.commit()
#         return True
#     except Exception as e:
#         st.error(f"Error deleting domain: {str(e)}")
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
#         return False
#     finally:
#         cursor.close()

# def get_user_task_stats(user_id):
#     """Get task statistics for a specific user"""
#     conn = get_db_connection()
#     if conn is None:
#         return {}
    
#     try:
#         query = """
#         SELECT 
#             COUNT(*) as total_tasks,
#             SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks,
#             SUM(CASE WHEN status IN ('Open', 'In Progress') AND due_date < GETDATE() THEN 1 ELSE 0 END) as overdue_tasks,
#             SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_tasks
#         FROM tasks 
#         WHERE assigned_to = ?
#         """
#         df = pd.read_sql(query, conn, params=(user_id,))
#         if df.empty:
#             return {}
#         return df.iloc[0].to_dict()
#     except Exception as e:
#         st.error(f"Error fetching user stats: {str(e)}")
#         return {}

import pyodbc
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os

# ✅ MSSQL Connection with proper error handling
@st.cache_resource
def get_db_connection():
    """
    Creates a MSSQL connection using Streamlit secrets or local config.
    Connection is cached to avoid multiple connections.
    """
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=task_management_db;"
            "UID=sa;"
            "PWD=Yashal309;"
        )
        return conn
    except Exception as e:
        st.error(f"Failed to connect to SQL Server: {str(e)}")
        return None

def init_database():
    """Initialize database schema and default data"""
    conn = get_db_connection()
    if conn is None:
        st.error("❌ Cannot initialize database - no connection")
        return
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                user_id INT PRIMARY KEY IDENTITY(1,1),
                name NVARCHAR(100) NOT NULL,
                email NVARCHAR(100) UNIQUE NOT NULL,
                role NVARCHAR(20) NOT NULL,
                created_at DATETIME DEFAULT GETDATE()
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
                created_at DATETIME DEFAULT GETDATE()
            )
        """)
        
        # Create tasks table with enhanced fields
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
            CREATE TABLE tasks (
                task_id INT PRIMARY KEY IDENTITY(1,1),
                title NVARCHAR(255) NOT NULL,
                description NVARCHAR(MAX),
                domain NVARCHAR(100),
                assigned_to INT,
                attachment NVARCHAR(MAX),
                status NVARCHAR(50) DEFAULT 'Open',
                due_date DATETIME,
                frequency NVARCHAR(50),
                priority NVARCHAR(20) DEFAULT 'Medium',
                created_by INT,
                created_at DATETIME DEFAULT GETDATE(),
                updated_at DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (assigned_to) REFERENCES users(user_id)
            )
        """)
        
        # Check and add missing columns
        missing_columns = [
            ('tasks', 'priority', 'ALTER TABLE tasks ADD priority NVARCHAR(20) DEFAULT ''Medium'''),
            ('tasks', 'created_by', 'ALTER TABLE tasks ADD created_by INT'),
            ('tasks', 'updated_at', 'ALTER TABLE tasks ADD updated_at DATETIME DEFAULT GETDATE()')
        ]
        
        for table, column, alter_stmt in missing_columns:
            try:
                cursor.execute(f"""
                    IF NOT EXISTS (SELECT * FROM sys.columns 
                                  WHERE object_id = OBJECT_ID('{table}') AND name = '{column}')
                    BEGIN
                        {alter_stmt}
                    END
                """)
                print(f"✅ Checked/added column {table}.{column}")
            except Exception as e:
                print(f"⚠️ Error with column {table}.{column}: {e}")
        
        # Create comments table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='comments' AND xtype='U')
            CREATE TABLE comments (
                comment_id INT PRIMARY KEY IDENTITY(1,1),
                task_id INT NOT NULL,
                user_id INT NOT NULL,
                comment_text NVARCHAR(MAX),
                created_at DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (task_id) REFERENCES tasks(task_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
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
                changed_at DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_email' AND object_id=OBJECT_ID('users'))
            CREATE INDEX idx_email ON users(email)
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_assigned_to' AND object_id=OBJECT_ID('tasks'))
            CREATE INDEX idx_assigned_to ON tasks(assigned_to)
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_task_status' AND object_id=OBJECT_ID('tasks'))
            CREATE INDEX idx_task_status ON tasks(status)
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='idx_due_date' AND object_id=OBJECT_ID('tasks'))
            CREATE INDEX idx_due_date ON tasks(due_date)
        """)
        
        conn.commit()
        print("✅ Database schema updated successfully!")
        
        # Insert default users - with existence check
        default_users = [
            ('Admin User', 'admin@nfoods.com', 'admin'),
            ('Yashal Ali', 'yashal.ali@nfoods.com', 'admin'),
            ('Ali', 'aliyashal309@gmail.com', 'user'),
        ]
        
        for name, email, role in default_users:
            try:
                # Check if user already exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO users (name, email, role)
                        VALUES (?, ?, ?)
                    """, (name, email, role))
                    print(f"✅ Added user: {name} ({email})")
                else:
                    print(f"ℹ️ User already exists: {name} ({email})")
            except Exception as e:
                print(f"⚠️ User {email} already exists or error: {e}")
        
        # Insert default domains with mancom members - with existence check
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
                # Check if domain already exists
                cursor.execute("SELECT COUNT(*) FROM domains WHERE domain_name = ?", (domain_name,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
                        VALUES (?, ?, ?)
                    """, (domain_name, mancom_name, mancom_email))
                    print(f"✅ Added domain: {domain_name}")
                else:
                    print(f"ℹ️ Domain already exists: {domain_name}")
            except Exception as e:
                print(f"⚠️ Domain {domain_name} already exists or error: {e}")
        
        conn.commit()
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")
        print(f"Database initialization error: {e}")
        if conn:
            conn.rollback()
    finally:
        # Only close cursor, not connection (connection is managed by streamlit cache)
        if cursor:
            cursor.close()
        # Don't close the connection here - it's cached by streamlit

# ✅ Helper Functions with proper connection handling
def get_user_by_email(email):
    """Get user by email address"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        query = "SELECT user_id, name, email, role FROM users WHERE email = ?"
        df = pd.read_sql(query, conn, params=(email,))
        if df.empty:
            return None
        return df.iloc[0].to_dict()
    except Exception as e:
        st.error(f"Error fetching user: {str(e)}")
        return None
    # Don't close connection - it's cached

def get_all_users():
    """Get all users as DataFrame"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = "SELECT user_id, name, email, role FROM users ORDER BY name"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching users: {str(e)}")
        return pd.DataFrame()

def get_admin_users():
    """Get all admin users"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = "SELECT user_id, name, email, role FROM users WHERE role = 'admin'"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching admin users: {str(e)}")
        return pd.DataFrame()

def get_domains():
    """Get all domains with mancom members"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = "SELECT domain_id, domain_name, mancom_member_name, mancom_member_email FROM domains ORDER BY domain_name"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching domains: {str(e)}")
        return pd.DataFrame()

def get_mancom_member_by_domain(domain_name):
    """Get mancom member for a specific domain"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        query = "SELECT mancom_member_name, mancom_member_email FROM domains WHERE domain_name = ?"
        df = pd.read_sql(query, conn, params=(domain_name,))
        if df.empty:
            return None
        return df.iloc[0].to_dict()
    except Exception as e:
        st.error(f"Error fetching mancom member: {str(e)}")
        return None

def create_task(title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, created_by):
    """Create a new task with safe column handling"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    if isinstance(due_date, date) and not isinstance(due_date, datetime):
        due_date = datetime.combine(due_date, datetime.min.time())
    
    cursor = conn.cursor()
    try:
        # Check which columns exist
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'tasks'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Build dynamic INSERT statement based on available columns
        columns = ['title', 'description', 'domain', 'assigned_to', 'attachment', 'status', 'due_date', 'frequency', 'priority']
        placeholders = ['?'] * len(columns)
        
        # Add created_by if column exists
        if 'created_by' in existing_columns:
            columns.append('created_by')
            placeholders.append('?')
        
        # Add updated_at if column exists
        if 'updated_at' in existing_columns:
            columns.append('updated_at')
            placeholders.append('GETDATE()')
        
        # Add created_at if column exists
        if 'created_at' in existing_columns:
            columns.append('created_at')
            placeholders.append('GETDATE()')
        
        columns_str = ', '.join(columns)
        placeholders_str = ', '.join(placeholders)
        
        # Prepare values
        values = [title, description, domain, assigned_to, attachment, status, due_date, frequency, priority]
        if 'created_by' in existing_columns:
            values.append(created_by)
        
        query = f"INSERT INTO tasks ({columns_str}) VALUES ({placeholders_str})"
        cursor.execute(query, values)
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error creating task: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def get_tasks(user_id=None, role='user', include_completed=True):
    """Get tasks with user info and comment counts - FIXED QUERY"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        # First check if priority column exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'tasks' AND COLUMN_NAME = 'priority'
        """)
        has_priority = cursor.fetchone()[0] > 0
        cursor.close()
        
        # Build query based on available columns
        if has_priority:
            base_query = """
            SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
                   (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.user_id
            """
            order_by = "ORDER BY t.due_date ASC, t.priority DESC"
        else:
            base_query = """
            SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
                   (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.user_id
            """
            order_by = "ORDER BY t.due_date ASC"
        
        if role == 'admin':
            if include_completed:
                query = f"{base_query} {order_by}"
                df = pd.read_sql(query, conn)
            else:
                query = f"{base_query} WHERE t.status != 'Completed' {order_by}"
                df = pd.read_sql(query, conn)
        else:
            if include_completed:
                query = f"{base_query} WHERE t.assigned_to = ? {order_by}"
                df = pd.read_sql(query, conn, params=(user_id,))
            else:
                query = f"{base_query} WHERE t.assigned_to = ? AND t.status != 'Completed' {order_by}"
                df = pd.read_sql(query, conn, params=(user_id,))
        
        # Ensure status column exists and has proper values
        if 'status' not in df.columns:
            df['status'] = 'Open'
        else:
            df['status'] = df['status'].fillna('Open')
            
        # Ensure priority column exists
        if 'priority' not in df.columns:
            df['priority'] = 'Medium'
            
        # Ensure due_date is properly formatted as datetime
        if 'due_date' in df.columns:
            df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error fetching tasks: {str(e)}")
        return pd.DataFrame()

def get_task_by_id(task_id):
    """Get a specific task by ID with safe column handling"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        # Check if created_by column exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'tasks' AND COLUMN_NAME = 'created_by'
        """)
        has_created_by = cursor.fetchone()[0] > 0
        cursor.close()
        
        # Build query based on available columns
        if has_created_by:
            query = """
            SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
                   creator.name AS created_by_name
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.user_id
            LEFT JOIN users creator ON t.created_by = creator.user_id
            WHERE t.task_id = ?
            """
        else:
            query = """
            SELECT t.*, u.name AS assigned_name, u.email AS assigned_email
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.user_id
            WHERE t.task_id = ?
            """
        
        df = pd.read_sql(query, conn, params=(task_id,))
        if df.empty:
            return None
        
        task = df.iloc[0].to_dict()
        # Ensure all required fields exist
        if 'status' not in task or not task['status']:
            task['status'] = 'Open'
        if 'priority' not in task or not task['priority']:
            task['priority'] = 'Medium'
        if 'created_by_name' not in task:
            task['created_by_name'] = 'Unknown'
            
        return task
    except Exception as e:
        st.error(f"Error fetching task: {str(e)}")
        return None

def update_task_status(task_id, status, changed_by=None):
    """Update task status with proper column handling"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        # Get old status for history
        cursor.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,))
        result = cursor.fetchone()
        old_status = result[0] if result else 'Open'
        
        # Check if updated_at column exists
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'tasks' AND COLUMN_NAME = 'updated_at'
        """)
        has_updated_at = cursor.fetchone()[0] > 0
        
        # Update task - with or without updated_at column
        if has_updated_at:
            cursor.execute("""
                UPDATE tasks
                SET status = ?, updated_at = GETDATE()
                WHERE task_id = ?
            """, (status, task_id))
        else:
            cursor.execute("""
                UPDATE tasks
                SET status = ?
                WHERE task_id = ?
            """, (status, task_id))
        
        # Add to history if changed_by provided
        if changed_by:
            # Check if task_history table exists
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'task_history'
            """)
            has_history_table = cursor.fetchone()[0] > 0
            
            if has_history_table:
                cursor.execute("""
                    INSERT INTO task_history (task_id, field_name, old_value, new_value, changed_by)
                    VALUES (?, 'status', ?, ?, ?)
                """, (task_id, old_status, status, changed_by))
        
        conn.commit()
        
        # Send notification if task was completed
        sender_email = os.environ.get("SMTP_USERNAME")
        sender_password = os.environ.get("SMTP_PASSWORD")
        if status == 'Completed' and old_status != 'Completed':
            task = get_task_by_id(task_id)
            if task and sender_email and sender_password:
                # Send completion notification to admins
                send_task_completion_notification(task, st.session_state.user_name, sender_email, sender_password)
        
        return True
    except Exception as e:
        st.error(f"Error updating task status: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def update_task(task_id, title, description, domain, assigned_to, attachment, status, due_date, frequency, priority, updated_by):
    """Update entire task"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        # Get old values for history
        cursor.execute("SELECT title, description, domain, assigned_to, attachment, status, due_date, frequency, priority FROM tasks WHERE task_id = ?", (task_id,))
        old_values = cursor.fetchone()
        
        if old_values:
            old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = old_values
        else:
            # If no old values found, set defaults
            old_title, old_description, old_domain, old_assigned_to, old_attachment, old_status, old_due_date, old_frequency, old_priority = '', '', '', None, '', 'Open', None, '', 'Medium'

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
        return True
    except Exception as e:
        st.error(f"Error updating task: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def delete_task(task_id):
    """Delete task and its comments"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        # Delete all comments for this task
        cursor.execute("DELETE FROM comments WHERE task_id = ?", (task_id,))
        
        # Delete task history
        cursor.execute("DELETE FROM task_history WHERE task_id = ?", (task_id,))
        
        # Delete the task
        cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting task: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def get_comments(task_id):
    """Get all comments for a task"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT c.comment_id, c.task_id, c.user_id, c.comment_text, c.created_at,
               u.name, u.email
        FROM comments c
        LEFT JOIN users u ON c.user_id = u.user_id
        WHERE c.task_id = ?
        ORDER BY c.created_at ASC
        """
        df = pd.read_sql(query, conn, params=(task_id,))
        return df
    except Exception as e:
        st.error(f"Error fetching comments: {str(e)}")
        return pd.DataFrame()

def add_comment(task_id, user_id, comment_text):
    """Add a comment to a task"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO comments (task_id, user_id, comment_text, created_at)
            VALUES (?, ?, ?, ?)
        """, (task_id, user_id, comment_text, datetime.now()))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding comment: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def add_user(name, email, role='user'):
    """Add a new user"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (name, email, role)
            VALUES (?, ?, ?)
        """, (name, email, role))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding user: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def update_user(user_id, name, email, role):
    """Update user details"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users
            SET name = ?, email = ?, role = ?
            WHERE user_id = ?
        """, (name, email, role, user_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating user: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def delete_user(user_id):
    """Delete a user"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        # First, update tasks assigned to this user to NULL
        cursor.execute("UPDATE tasks SET assigned_to = NULL WHERE assigned_to = ?", (user_id,))
        
        # Delete user's comments
        cursor.execute("DELETE FROM comments WHERE user_id = ?", (user_id,))
        
        # Delete the user
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting user: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def add_domain(domain_name, mancom_member_name, mancom_member_email):
    """Add a new domain"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email)
            VALUES (?, ?, ?)
        """, (domain_name, mancom_member_name, mancom_member_email))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding domain: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

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

def delete_domain(domain_id):
    """Delete a domain"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM domains WHERE domain_id = ?", (domain_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting domain: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def get_overdue_tasks():
    """Get tasks that are overdue"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
               (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.user_id
        WHERE t.due_date < GETDATE() AND t.status IN ('Open', 'In Progress')
        ORDER BY t.due_date ASC
        """
        df = pd.read_sql(query, conn)
        
        # Ensure status column exists
        if 'status' not in df.columns:
            df['status'] = 'Open'
            
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
        SELECT t.*, u.name AS assigned_name, u.email AS assigned_email,
               (SELECT COUNT(*) FROM comments c WHERE c.task_id = t.task_id) AS comment_count
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.user_id
        WHERE t.due_date BETWEEN GETDATE() AND DATEADD(day, ?, GETDATE()) 
          AND t.status IN ('Open', 'In Progress')
        ORDER BY t.due_date ASC
        """
        df = pd.read_sql(query, conn, params=(days,))
        
        # Ensure status column exists
        if 'status' not in df.columns:
            df['status'] = 'Open'
            
        return df
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
        SELECT th.field_name, th.old_value, th.new_value, th.changed_at, u.name as changed_by_name
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

# Email functions
def send_email_summary(user_email, user_name, tasks_df, sender_email, sender_password):
    """Send email summary of pending tasks"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'TaskFlow Pro - Pending Tasks Summary – {datetime.now().strftime("%B %Y")}'
        msg['From'] = sender_email
        msg['To'] = user_email

        html = f"""
        <html>
          <head>
            <style>
              body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2d3748; line-height: 1.6; }}
              .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
              .header {{ border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; }}
              .task-table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
              .task-table th {{ background-color: #2563eb; color: white; padding: 12px 8px; text-align: left; }}
              .task-table td {{ padding: 12px 8px; border-bottom: 1px solid #e2e8f0; }}
              .priority-high {{ color: #dc2626; font-weight: bold; }}
              .priority-medium {{ color: #f59e0b; font-weight: bold; }}
              .priority-low {{ color: #10b981; font-weight: bold; }}
              .status-open {{ color: #f59e0b; }}
              .status-inprogress {{ color: #2563eb; }}
              .status-completed {{ color: #10b981; }}
              .info-box {{ background-color: #f8fafc; border-left: 3px solid #2563eb; padding: 16px; margin: 25px 0; }}
            </style>
          </head>
          <body>
            <div class="container">
              <div class="header">
                <h1 style="color: #1a202c; margin: 0 0 10px 0; font-size: 28px; font-weight: 700;">Task Summary Report</h1>
                <p style="color: #64748b; margin: 0; font-size: 16px;">Hello {user_name},</p>
              </div>
              <p style="color: #475569; font-size: 15px; margin-bottom: 25px;">Here are your pending tasks that require attention:</p>
              
              <table class="task-table">
                <thead>
                  <tr>
                    <th>Task</th>
                    <th>Domain</th>
                    <th>Priority</th>
                    <th>Due Date</th>
                    <th>Status</th>
                    <th style="text-align: center;">Comments</th>
                  </tr>
                </thead>
                <tbody>
        """

        for _, task in tasks_df.iterrows():
            # Safe data access with defaults
            title = task.get('title', 'Untitled Task')
            description = str(task.get('description', 'No description'))[:80] + '...' if task.get('description') else 'No description'
            domain = task.get('domain', 'No domain')
            priority = task.get('priority', 'Medium')
            status = task.get('status', 'Open')
            
            # Safe date formatting
            due_date_str = "N/A"
            if pd.notna(task.get('due_date')):
                try:
                    due_date_str = task['due_date'].strftime("%Y-%m-%d")
                except:
                    due_date_str = "Invalid date"
            
            # Safe priority class
            priority_lower = str(priority).lower() if priority else 'medium'
            priority_class = f"priority-{priority_lower}"
            
            # Safe status class
            status_lower = str(status).lower().replace(' ', '') if status else 'open'
            status_class = f"status-{status_lower}"
            
            comment_count = task.get('comment_count', 0)

            html += f"""
                  <tr>
                    <td><b>{title}</b><br><span style="color:#64748b; font-size: 12px;">{description}</span></td>
                    <td>{domain}</td>
                    <td><span class="{priority_class}">{priority}</span></td>
                    <td>{due_date_str}</td>
                    <td><span class="{status_class}">{status}</span></td>
                    <td style="text-align:center; color:#2563eb; font-weight: bold;">{comment_count}</td>
                  </tr>
            """

        html += """
                </tbody>
              </table>
              
              <div class="info-box">
                <p style="margin:0; font-weight: 500;">Please update task statuses and provide updates as you make progress.</p>
              </div>
              
              <div style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:10px; color:#64748b; font-size:13px;">
                <p>Best regards,</p>
                <p style="font-weight:600; color:#475569;">TaskFlow Pro Administration</p>
                <p style="font-size:12px; color:#94a3b8;">This is an automated email. Please do not reply directly to this message.</p>
              </div>
            </div>
          </body>
        </html>
        """

        part = MIMEText(html, 'html')
        msg.attach(part)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return True

    except Exception as e:
        st.error(f"Error sending email to {user_email}: {str(e)}")
        return False

def send_escalation_email(task, sender_email, sender_password):
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
        assigned_name = task.get('assigned_name', 'Unassigned')
        domain = task.get('domain', 'Unknown')
        status = task.get('status', 'Open')
        priority = task.get('priority', 'Medium')
        
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
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        st.error(f"Error sending escalation email: {str(e)}")
        return False

def send_task_completion_notification(task, user_name, sender_email, sender_password):
    """Send notification to admins when a task is completed"""
    try:
        admin_users = get_admin_users()
        
        if admin_users.empty:
            st.error("No admin users found to send notification")
            return False
        
        success_count = 0
        
        for _, admin in admin_users.iterrows():
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
            
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                success_count += 1
            except Exception as e:
                st.error(f"Error sending completion notification to {admin.get('email', 'Unknown')}: {str(e)}")
        
        return success_count > 0
        
    except Exception as e:
        st.error(f"Error sending task completion notifications: {str(e)}")

    
    """Send notification to admins when a task is completed"""
    try:
        admin_users = get_admin_users()
        
        if admin_users.empty:
            st.error("No admin users found to send notification")
            return False
        
        success_count = 0
        
        for _, admin in admin_users.iterrows():
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'✅ Task Completed: {task["title"]}'
            msg['From'] = sender_email
            msg['To'] = admin['email']
            
            due_date_str = task['due_date'].strftime("%Y-%m-%d") if pd.notna(task['due_date']) else "Not specified"
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
                        <td style="color: #1e293b;">{task['title']}</td>
                      </tr>
                      <tr>
                        <td style="color: #475569; font-weight: 600;">Description:</td>
                        <td style="color: #1e293b;">{task['description']}</td>
                      </tr>
                      <tr>
                        <td style="color: #475569; font-weight: 600;">Completed By:</td>
                        <td style="color: #1e293b;">{user_name}</td>
                      </tr>
                      <tr>
                        <td style="color: #475569; font-weight: 600;">Domain:</td>
                        <td style="color: #1e293b;">{task['domain']}</td>
                      </tr>
                      <tr>
                        <td style="color: #475569; font-weight: 600;">Due Date:</td>
                        <td style="color: #1e293b;">{due_date_str}</td>
                      </tr>
                      <tr>
                        <td style="color: #475569; font-weight: 600;">Frequency:</td>
                        <td style="color: #1e293b;">{task['frequency']}</td>
                      </tr>
                      <tr>
                        <td style="color: #475569; font-weight: 600;">Priority:</td>
                        <td style="color: #1e293b;">{task.get('priority', 'Medium')}</td>
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
            
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                success_count += 1
            except Exception as e:
                st.error(f"Error sending completion notification to {admin['email']}: {str(e)}")
        
        return success_count > 0
        
    except Exception as e:
        st.error(f"Error sending task completion notifications: {str(e)}")
        return False
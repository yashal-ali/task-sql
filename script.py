
# import os
# import sys
# import logging
# import sqlite3
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from datetime import datetime, timedelta
# from typing import Dict, Any, List
# import pandas as pd

# # ✅ Conditional dotenv loading
# if os.path.exists(".env"):
#     from dotenv import load_dotenv
#     load_dotenv()
#     print("✅ Loaded .env file for local testing")
# else:
#     print("🌀 No .env file found - using system environment variables")

# # Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)


# class ComplianceEmailSystem:
#     def __init__(self, db_path: str = "task_management.db"):
#         self.db_path = db_path
#         self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        
#         # Handle empty or invalid SMTP_PORT values
#         smtp_port_str = os.environ.get("SMTP_PORT", "587")
#         try:
#             self.smtp_port = int(smtp_port_str) if smtp_port_str else 587
#         except ValueError:
#             logger.warning(f"Invalid SMTP_PORT value '{smtp_port_str}', using default 587")
#             self.smtp_port = 587
            
#         self.smtp_username = os.environ.get("SMTP_USERNAME")
#         self.smtp_password = os.environ.get("SMTP_PASSWORD")

#         # Department heads mapping - UPDATED WITH EXACT DOMAIN NAMES
#         self.department_heads = {
#             'SAP': 'yashal.ali@nfoods.com',
#             'SalesFlo': 'haniyamaqsood18@gmail.com',
#             'NFlo': 'haniyamaqsood18@gmail.com',
#             'EC': 'yashal.ali@nfoods.com',
#             'Network': 'yashal.ali@nfoods.com',
#             'Help Desk': 'farooqui4408609@cloud.neduet.edu.pk',
#             'IT-Governance': 'yasir.sarwar@nfoods.com'
#         }

#         # Debug environment variables (mask password)
#         smtp_password_debug = "***SET***" if self.smtp_password else "***MISSING***"
#         logger.info(
#             f"SMTP Configuration: Server={self.smtp_server}, Port={self.smtp_port}, "
#             f"Username={self.smtp_username}, Password={smtp_password_debug}"
#         )

#         if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
#             missing = []
#             if not self.smtp_server: missing.append("SMTP_SERVER")
#             if not self.smtp_port: missing.append("SMTP_PORT")
#             if not self.smtp_username: missing.append("SMTP_USERNAME")
#             if not self.smtp_password: missing.append("SMTP_PASSWORD")
#             logger.error(f"❌ Missing SMTP credentials: {missing}")
#         self.data = None
    
#     def load_database_data(self) -> bool:
#         """Load and validate data from SQLite database"""
#         try:
#             conn = sqlite3.connect(self.db_path)
            
#             query = """
#             SELECT 
#                 t.domain as 'Domain',
#                 t.title as 'Task', 
#                 t.description as 'Task Description',
#                 u.email as 'Email',
#                 u.name as 'User Name',
#                 t.attachment as 'Attachment Link',
#                 t.status as 'Status',
#                 t.due_date as 'Due Date',
#                 t.frequency as 'Frequency'
#             FROM tasks t
#             LEFT JOIN users u ON t.assigned_to = u.user_id
#             WHERE t.status = 'Pending'
#             """
            
#             self.data = pd.read_sql_query(query, conn)
#             conn.close()
            
#             # Validate required columns
#             required_columns = ['Domain', 'Task', 'Task Description', 'Email', 'Attachment Link', 
#                               'Status', 'Due Date', 'Frequency']
#             missing_columns = [col for col in required_columns if col not in self.data.columns]
            
#             if missing_columns:
#                 logger.error(f"Missing required columns: {missing_columns}")
#                 logger.error(f"Available columns: {list(self.data.columns)}")
#                 return False
                
#             # FIXED: Better date conversion with error handling
#             logger.info(f"Due Date column type before conversion: {self.data['Due Date'].dtype}")
#             logger.info(f"Sample Due Date values: {self.data['Due Date'].head().tolist()}")
            
#             # Convert date columns with better error handling
#             try:
#                 self.data['Due Date'] = pd.to_datetime(self.data['Due Date'], errors='coerce').dt.date
#                 # Check for any failed conversions
#                 if self.data['Due Date'].isnull().any():
#                     invalid_dates = self.data[self.data['Due Date'].isnull()]
#                     logger.warning(f"Found {len(invalid_dates)} tasks with invalid due dates. They will be excluded.")
#                     logger.warning(f"Invalid date tasks: {invalid_dates[['Task', 'Due Date']].to_dict('records')}")
#             except Exception as e:
#                 logger.error(f"Error converting Due Date column: {e}")
#                 return False
            
#             # Fill missing domains with a default value if any
#             if self.data['Domain'].isnull().any():
#                 logger.warning("Some tasks have missing Domain values, filling with 'General'")
#                 self.data['Domain'] = self.data['Domain'].fillna('General')
            
#             # Filter out tasks without valid email addresses
#             original_count = len(self.data)
#             self.data = self.data[self.data['Email'].notna() & (self.data['Email'] != '')]
#             if len(self.data) < original_count:
#                 logger.warning(f"Filtered out {original_count - len(self.data)} tasks without valid email addresses")
            
#             logger.info(f"Successfully loaded {len(self.data)} tasks across {self.data['Domain'].nunique()} domains")
#             if len(self.data) > 0:
#                 logger.info(f"Users with tasks: {self.data['Email'].unique().tolist()}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error loading database: {e}")
#             return False

#     def get_overdue_tasks(self, days_overdue: int = 15) -> pd.DataFrame:
#         """Get tasks that are overdue by specified number of days"""
#         today = datetime.now().date()
        
#         # FIXED: Better date filtering with error handling
#         try:
#             # Ensure we only work with valid dates
#             valid_dates_data = self.data[self.data['Due Date'].notna()].copy()
            
#             overdue_tasks = valid_dates_data[
#                 (valid_dates_data['Status'].str.lower() == 'pending') &
#                 (valid_dates_data['Due Date'] < today)
#             ].copy()
            
#             if overdue_tasks.empty:
#                 logger.info(f"No overdue tasks found")
#                 return overdue_tasks
            
#             # FIXED: Calculate days overdue safely
#             overdue_tasks['Days Overdue'] = overdue_tasks['Due Date'].apply(
#                 lambda x: (today - x).days if pd.notna(x) else 0
#             )
            
#             # Filter for tasks overdue by specified days or more
#             overdue_tasks = overdue_tasks[overdue_tasks['Days Overdue'] >= days_overdue]
            
#             logger.info(f"Found {len(overdue_tasks)} tasks overdue by {days_overdue}+ days across {overdue_tasks['Domain'].nunique()} domains")
            
#             if not overdue_tasks.empty:
#                 logger.info(f"Domains with overdue tasks: {overdue_tasks['Domain'].unique().tolist()}")
#                 logger.info(f"Max days overdue: {overdue_tasks['Days Overdue'].max()}")
            
#             return overdue_tasks
            
#         except Exception as e:
#             logger.error(f"Error finding overdue tasks: {e}")
#             return pd.DataFrame()

#     def get_department_head_email(self, domain: str) -> str:
#         """Get department head email for a given domain"""
#         domain_clean = domain.strip()
        
#         # Try exact match first (case-sensitive)
#         if domain_clean in self.department_heads:
#             return self.department_heads[domain_clean]
        
#         # Try case-insensitive exact match
#         domain_lower = domain_clean.lower()
#         for dept_domain, email in self.department_heads.items():
#             if dept_domain.lower() == domain_lower:
#                 return email
        
#         # Try partial matching for domains that might have variations
#         for dept_domain, email in self.department_heads.items():
#             dept_lower = dept_domain.lower()
#             if (dept_lower in domain_lower or 
#                 domain_lower in dept_lower or
#                 dept_lower.replace('-', ' ').replace('_', ' ') in domain_lower.replace('-', ' ').replace('_', ' ') or
#                 domain_lower.replace('-', ' ').replace('_', ' ') in dept_lower.replace('-', ' ').replace('_', ' ')):
#                 return email
        
#         # Default fallback - send to IT governance for unknown domains
#         logger.warning(f"No department head found for domain '{domain}', using IT-Governance as fallback")
#         return self.department_heads['IT-Governance']

#     def create_escalation_email_content(self, department_tasks: pd.DataFrame, department_head: str, domain: str) -> str:
#         """Create HTML email content for escalation reports"""
#         task_count = len(department_tasks)
#         max_days_overdue = department_tasks['Days Overdue'].max()
        
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
#                 .header {{ background-color: #fff3cd; padding: 20px; text-align: center; border-radius: 5px; border-left: 6px solid #ffc107; }}
#                 .urgent-section {{ margin: 20px 0; padding: 15px; background-color: #f8d7da; border-radius: 5px; border-left: 6px solid #dc3545; }}
#                 .task-table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
#                 .task-table th, .task-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
#                 .task-table th {{ background-color: #dc3545; color: white; }}
#                 .task-table tr:nth-child(even) {{ background-color: #f2f2f2; }}
#                 .critical {{ color: #dc3545; font-weight: bold; }}
#                 .footer {{ margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
#                 .summary {{ background-color: #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }}
#             </style>
#         </head>
#         <body>
#             <div class="header">
#                 <h2>Compliance Task  Report</h2>
#                 <p>Domain: <strong>{domain}</strong> | Department Head: <strong></strong></p>
#             </div>
            
#             <div class="urgent-section">
#                 <h3>📋 Escalation Summary</h3>
#                 <p><strong>{task_count} tasks</strong> are overdue by <strong>15+ days</strong> in your department.</p>
#                 <p>Maximum days overdue: <strong>{max_days_overdue} days</strong></p>
#             </div>

#             <table class="task-table">
#                 <thead>
#                     <tr>
#                         <th>Task</th>
#                         <th>Assigned To</th>
#                         <th>Task Description</th>
#                         <th>Original Due Date</th>
#                         <th>Days Overdue</th>
#                         <th>Frequency</th>
#                         <th>Attachment Link</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#         """
        
#         for _, task in department_tasks.iterrows():
#             critical_class = "critical" if task['Days Overdue'] > 30 else ""
            
#             html_content += f"""
#                     <tr>
#                         <td><strong>{task['Task']}</strong></td>
#                         <td>{task['User Name']} ({task['Email']})</td>
#                         <td>{task['Task Description']}</td>
#                         <td class="{critical_class}">{task['Due Date'].strftime('%Y-%m-%d')}</td>
#                         <td class="{critical_class}">{task['Days Overdue']} days</td>
#                         <td>{task['Frequency']}</td>
#                         <td><a href="{task['Attachment Link']}" target="_blank">Upload Document</a></td>
#                     </tr>
#             """
        
#         html_content += f"""
#                 </tbody>
#             </table>
            
#             <div class="footer">
#                 <h3>🎯 Required Actions:</h3>
#                 <ul>
#                     <li>Follow up with the assigned team members immediately</li>
#                     <li>Ensure completion of these overdue compliance tasks</li>
#                     <li>Update task status in the system once completed</li>
#                 </ul>
                
#                 <p><strong>Note:</strong> This is an automated escalation report generated for tasks overdue by 15+ days.</p>
#                 <p><strong>Domain:</strong> {domain}</p>
#                 <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
#             </div>
#         </body>
#         </html>
#         """
        
#         return html_content

#     def send_escalation_reports(self, dry_run: bool = False) -> Dict[str, Any]:
#         """Send escalation reports to department heads for overdue tasks"""
#         if not self.load_database_data():
#             return {"success": False, "error": "Failed to load database data"}
        
#         # Get tasks overdue by 15+ days
#         overdue_tasks = self.get_overdue_tasks(days_overdue=15)
        
#         if overdue_tasks.empty:
#             logger.info("No tasks overdue by 15+ days - no escalation reports to send")
#             return {"success": True, "escalation_emails_sent": 0, "total_overdue_tasks": 0}
        
#         # Group overdue tasks by domain and find department heads
#         domain_escalations = {}
        
#         for domain in overdue_tasks['Domain'].unique():
#             domain_tasks = overdue_tasks[overdue_tasks['Domain'] == domain]
#             department_head_email = self.get_department_head_email(domain)
            
#             if domain not in domain_escalations:
#                 domain_escalations[domain] = {
#                     'email': department_head_email,
#                     'tasks': domain_tasks
#                 }
#             else:
#                 # Merge tasks for the same department head
#                 domain_escalations[domain]['tasks'] = pd.concat([domain_escalations[domain]['tasks'], domain_tasks])
        
#         # Dry run mode
#         if dry_run:
#             logger.info("🚀 DRY RUN MODE - No escalation emails will be actually sent")
#             print(f"\n📋 ESCALATION DRY RUN RESULTS:")
#             print(f"📧 Would send escalation reports to {len(domain_escalations)} department heads")
#             print(f"📊 Total overdue tasks: {len(overdue_tasks)}")
            
#             for domain, escalation in domain_escalations.items():
#                 dept_head = escalation['email']
#                 task_count = len(escalation['tasks'])
#                 print(f"   📨 To: {dept_head} (Domain: {domain}), Overdue Tasks: {task_count}")
                
#             return {
#                 "success": True,
#                 "dry_run": True,
#                 "would_send_escalations": len(domain_escalations),
#                 "total_overdue_tasks": len(overdue_tasks),
#                 "domains_affected": list(domain_escalations.keys())
#             }
        
#         # Actual escalation email sending
#         escalation_emails_sent = 0
#         escalation_emails_failed = 0
        
#         for domain, escalation in domain_escalations.items():
#             department_head_email = escalation['email']
#             domain_tasks = escalation['tasks']
            
#             # Create escalation email content
#             html_content = self.create_escalation_email_content(domain_tasks, department_head_email, domain)
#             subject = f"{domain} Department - {len(domain_tasks)} Tasks Overdue by 15+ Days"
            
#             # Send escalation email
#             if self.send_email(department_head_email, subject, html_content):
#                 escalation_emails_sent += 1
#                 logger.info(f"Escalation email sent to {department_head_email} for {len(domain_tasks)} tasks in {domain} domain")
#             else:
#                 escalation_emails_failed += 1
#                 logger.error(f"Failed to send escalation email to {department_head_email} for {domain} domain")
        
#         result = {
#             "success": True,
#             "escalation_emails_sent": escalation_emails_sent,
#             "escalation_emails_failed": escalation_emails_failed,
#             "total_overdue_tasks": len(overdue_tasks),
#             "domains_affected": list(domain_escalations.keys()),
#             "department_heads_contacted": list(set(escalation['email'] for escalation in domain_escalations.values()))
#         }
        
#         logger.info(f"Escalation processing complete: {escalation_emails_sent} emails sent, {escalation_emails_failed} failed")
#         return result

#     # === EXISTING METHODS (KEEP THESE FROM YOUR ORIGINAL CODE) ===
    
#     def filter_tasks_by_schedule(self, schedule_type: str) -> pd.DataFrame:
#         """Filter tasks based on schedule type (monthly, quarterly, reminder, daily)"""
#         today = datetime.now().date()
        
#         if schedule_type == "monthly":
#             # Monthly tasks - send on 1st of month
#             if today.day != 1:
#                 logger.info("Not the 1st of month - skipping monthly tasks")
#                 return pd.DataFrame()
            
#             monthly_tasks = self.data[
#                 (self.data['Frequency'].str.lower().str.contains('monthly', na=False)) &
#                 (self.data['Status'].str.lower() == 'pending')
#             ]
#             logger.info(f"Found {len(monthly_tasks)} monthly tasks across {monthly_tasks['Domain'].nunique()} domains")
#             return monthly_tasks
            
#         elif schedule_type == "quarterly":
#             # Quarterly tasks - send on 25th of the last month of each quarter
#             quarter_months = [3, 6, 9, 12]
#             current_month = today.month
#             current_day = today.day
            
#             if current_month not in quarter_months or current_day != 25:
#                 logger.info(f"Not 25th of a quarter-end month (current: {today}) - skipping quarterly tasks")
#                 return pd.DataFrame()
            
#             quarterly_tasks = self.data[
#                 (self.data['Frequency'].str.lower().str.contains('quarterly', na=False)) &
#                 (self.data['Status'].str.lower() == 'pending')
#             ]
#             logger.info(f"Found {len(quarterly_tasks)} quarterly tasks across {quarterly_tasks['Domain'].nunique()} domains")
#             return quarterly_tasks
            
#         elif schedule_type == "daily":
#             # Daily tasks - send every day
#             daily_tasks = self.data[
#                 (self.data['Status'].str.lower() == 'pending') &
#                 (self.data['Due Date'] >= today)
#             ]
#             logger.info(f"Found {len(daily_tasks)} tasks for daily reminders across {daily_tasks['Domain'].nunique()} domains")
#             return daily_tasks
            
#         elif schedule_type == "reminder":
#             # Weekly reminders - send every Monday for pending tasks
#             if today.weekday() != 0:
#                 logger.info("Not Monday - skipping weekly reminders")
#                 return pd.DataFrame()
            
#             reminder_tasks = self.data[
#                 (self.data['Status'].str.lower() == 'pending') &
#                 (self.data['Due Date'] >= today)
#             ]
#             logger.info(f"Found {len(reminder_tasks)} tasks for reminders across {reminder_tasks['Domain'].nunique()} domains")
#             return reminder_tasks
            
#         else:
#             logger.error(f"Unknown schedule type: {schedule_type}")
#             return pd.DataFrame()
    
#     def create_email_content(self, user_tasks: pd.DataFrame, schedule_type: str) -> str:
#         """Create HTML email content for user tasks"""
#         user_email = user_tasks['Email'].iloc[0]
#         user_name = user_tasks['User Name'].iloc[0] if 'User Name' in user_tasks.columns and pd.notna(user_tasks['User Name'].iloc[0]) else 'User'
#         task_count = len(user_tasks)
        
#         email_type = schedule_type.capitalize()
#         if schedule_type == "reminder":
#             email_type = "Weekly Reminder"
#         elif schedule_type == "daily":
#             email_type = "Daily Reminder"
        
#         # Group tasks by domain for better organization
#         tasks_by_domain = user_tasks.groupby('Domain')
        
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
#                 .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 5px; }}
#                 .domain-section {{ margin: 20px 0; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
#                 .domain-title {{ font-size: 1.2em; font-weight: bold; color: #495057; margin-bottom: 10px; }}
#                 .task-table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
#                 .task-table th, .task-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
#                 .task-table th {{ background-color: #4CAF50; color: white; }}
#                 .task-table tr:nth-child(even) {{ background-color: #f2f2f2; }}
#                 .urgent {{ color: #ff6b6b; font-weight: bold; }}
#                 .footer {{ margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
#                 .summary {{ background-color: #d4edda; padding: 10px; border-radius: 5px; margin: 10px 0; }}
#                 .quarter-notice {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ffc107; }}
#             </style>
#         </head>
#         <body>
#             <div class="header">
#                 <h2>Compliance Task {email_type}</h2>
#                 <p>Hello {user_name}, you have {task_count} pending compliance task(s) across {len(tasks_by_domain)} domain(s)</p>
#             </div>
#         """
        
#         # Add quarterly notice if applicable
#         if schedule_type == "quarterly":
#             html_content += """
#             <div class="quarter-notice">
#                 <h3>📅 Quarterly Compliance Notice</h3>
#                 <p><strong>This is your quarterly compliance reminder.</strong> Please ensure all quarterly tasks are completed before the end of the current quarter.</p>
#             </div>
#             """
        
#         html_content += f"""
#             <div class="summary">
#                 <h3>📊 Task Summary by Domain:</h3>
#                 <ul>
#         """
        
#         # Add domain summary
#         for domain, domain_tasks in tasks_by_domain:
#             html_content += f'<li><strong>{domain}</strong>: {len(domain_tasks)} task(s)</li>'
        
#         html_content += """
#                 </ul>
#             </div>
#         """
        
#         # Add tasks organized by domain
#         for domain, domain_tasks in tasks_by_domain:
#             html_content += f"""
#             <div class="domain-section">
#                 <div class="domain-title">🏢 Domain: {domain}</div>
#                 <table class="task-table">
#                     <thead>
#                         <tr>
#                             <th>Task</th>
#                             <th>Task Description</th>
#                             <th>Deadline</th>
#                             <th>Frequency</th>
#                             <th>Attachment Link</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#             """
            
#             for _, task in domain_tasks.iterrows():
#                 days_remaining = (task['Due Date'] - datetime.now().date()).days
#                 urgent_class = "urgent" if days_remaining <= 3 else ""
                
#                 html_content += f"""
#                         <tr>
#                             <td><strong>{task['Task']}</strong></td>
#                             <td>{task['Task Description']}</td>
#                             <td class="{urgent_class}">{task['Due Date'].strftime('%Y-%m-%d')} ({days_remaining} days remaining)</td>
#                             <td>{task['Frequency']}</td>
#                             <td><a href="{task['Attachment Link']}" target="_blank">Upload Files</a></td>
#                         </tr>
#                 """
            
#             html_content += """
#                     </tbody>
#                 </table>
#             </div>
#             """
        
#         html_content += f"""
#             <div class="footer">
#                 <p><strong>Action Required:</strong> Please complete these tasks by their respective deadlines.</p>
#                 <p><strong>Note:</strong> This is an automated message. Please do not reply to this email.</p>
#                 <p><strong>Domains Affected:</strong> {", ".join(tasks_by_domain.groups.keys())}</p>
#             </div>
#         </body>
#         </html>
#         """
        
#         return html_content
    
#     def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
#         """Send email via SMTP"""
#         try:
#             if not all([self.smtp_username, self.smtp_password]):
#                 logger.error("SMTP credentials are incomplete")
#                 return False
            
#             # Create message
#             msg = MIMEMultipart('alternative')
#             msg['Subject'] = subject
#             msg['From'] = self.smtp_username
#             msg['To'] = to_email
            
#             # Attach HTML content
#             msg.attach(MIMEText(html_content, 'html'))
            
#             # Send email with better error handling
#             logger.info(f"Attempting to send email to {to_email}")
#             with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
#                 server.starttls()
#                 server.login(self.smtp_username, self.smtp_password)
#                 server.send_message(msg)
            
#             logger.info(f"Email sent successfully to {to_email}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error sending email to {to_email}: {e}")
#             return False
    
#     def process_tasks(self, schedule_type: str, dry_run: bool = False) -> Dict[str, Any]:
#         """Main processing function with dry run option"""
#         if not self.load_database_data():
#             return {"success": False, "error": "Failed to load database data"}
        
#         # Filter tasks based on schedule
#         filtered_tasks = self.filter_tasks_by_schedule(schedule_type)
        
#         if filtered_tasks.empty:
#             logger.info(f"No tasks to process for {schedule_type}")
#             return {"success": True, "emails_sent": 0, "total_tasks": 0, "unique_users": 0, "domains_affected": 0}
        
#         # Group tasks by email
#         grouped_tasks = filtered_tasks.groupby('Email')
#         emails_sent = 0
#         emails_failed = 0
        
#         email_subject = f"Compliance Task {schedule_type.capitalize()}"
#         if schedule_type == "reminder":
#             email_subject = "Weekly Compliance Task Reminder"
#         elif schedule_type == "daily":
#             email_subject = "Daily Compliance Task Reminder"
#         elif schedule_type == "quarterly":
#             email_subject = "Quarterly Compliance Task Reminder - Action Required"
        
#         # Dry run mode
#         if dry_run:
#             logger.info("🚀 DRY RUN MODE - No emails will be actually sent")
#             print(f"\n📋 DRY RUN RESULTS for {schedule_type}:")
#             print(f"📧 Would send emails to {len(grouped_tasks)} users")
#             print(f"📊 Would process {len(filtered_tasks)} tasks")
#             print(f"🏢 Domains affected: {filtered_tasks['Domain'].nunique()}")
            
#             for email, tasks in grouped_tasks:
#                 user_name = tasks['User Name'].iloc[0] if 'User Name' in tasks.columns and pd.notna(tasks['User Name'].iloc[0]) else 'Unknown'
#                 print(f"   📨 To: {user_name} ({email}), Tasks: {len(tasks)}")
                
#             return {
#                 "success": True,
#                 "dry_run": True,
#                 "would_send_emails": len(grouped_tasks),
#                 "total_tasks": len(filtered_tasks),
#                 "domains_affected": filtered_tasks['Domain'].nunique()
#             }
        
#         # Actual email sending
#         for email, tasks in grouped_tasks:
#             # Create email content
#             html_content = self.create_email_content(tasks, schedule_type)
            
#             # Send email
#             if self.send_email(email, email_subject, html_content):
#                 emails_sent += 1
#             else:
#                 emails_failed += 1
        
#         result = {
#             "success": True,
#             "emails_sent": emails_sent,
#             "emails_failed": emails_failed,
#             "total_tasks": len(filtered_tasks),
#             "unique_users": len(grouped_tasks),
#             "domains_affected": filtered_tasks['Domain'].nunique()
#         }
        
#         logger.info(f"Processing complete: {emails_sent} emails sent, {emails_failed} failed, {result['domains_affected']} domains affected")
#         return result


# def main():
#     dry_run = "--dry-run" in sys.argv
#     args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

#     if len(args) != 1:
#         print("Usage: python script.py <schedule_type> [--dry-run]")
#         print("Valid schedule types: daily, monthly, quarterly, reminder, escalation")
#         sys.exit(1)

#     schedule_type = args[0].lower()
#     valid_types = ["daily", "monthly", "quarterly", "reminder", "escalation"]

#     if schedule_type not in valid_types:
#         print(f"Invalid schedule type. Must be one of {valid_types}")
#         sys.exit(1)

#     db_file = "task_management.db"
#     if not os.path.exists(db_file):
#         logger.error(f"Database file not found: {db_file}")
#         sys.exit(1)

#     system = ComplianceEmailSystem(db_file)
    
#     if schedule_type == "escalation":
#         result = system.send_escalation_reports(dry_run=dry_run)
#     else:
#         result = system.process_tasks(schedule_type, dry_run=dry_run)

#     if result.get("success"):
#         if dry_run:
#             print(f"✅ DRY RUN completed for {schedule_type} tasks")
#         else:
#             print(f"✅ Successfully processed {schedule_type} tasks")
#     else:
#         print(f"❌ Failed: {result.get('error', 'Unknown error')}")
#         sys.exit(1)


# if __name__ == "__main__":
#     main()



import os
import sys
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId

# ✅ Conditional dotenv loading
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file for local testing")
else:
    print("🌀 No .env file found - using system environment variables")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ComplianceEmailSystem:
    def __init__(self):
        # MongoDB connection
        try:
            # Use st.secrets for MongoDB
            mongo_uri = st.secrets["mongodb"]["uri"]
            self.client = MongoClient(mongo_uri)
            self.client.admin.command('ping')
            self.db = self.client['task_management_db']
            logger.info("✅ Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            self.db = None
        
        # Keep using os.environ for SMTP (since they're set in GitHub Actions env)
        self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        
        # Handle empty or invalid SMTP_PORT values
        smtp_port_str = os.environ.get("SMTP_PORT", "587")
        try:
            self.smtp_port = int(smtp_port_str) if smtp_port_str else 587
        except ValueError:
            logger.warning(f"Invalid SMTP_PORT value '{smtp_port_str}', using default 587")
            self.smtp_port = 587
            
        self.smtp_username = os.environ.get("SMTP_USERNAME")
        self.smtp_password = os.environ.get("SMTP_PASSWORD")  

        self.department_heads = {
            'SAP': 'yashal.ali@nfoods.com',
            'SalesFlo': 'haniyamaqsood18@gmail.com',
            'NFlo': 'haniyamaqsood18@gmail.com',
            'EC': 'yashal.ali@nfoods.com',
            'Network': 'yashal.ali@nfoods.com',
            'Help Desk': 'farooqui4408609@cloud.neduet.edu.pk',
            'IT-Governance': 'yasir.sarwar@nfoods.com'
        }
    def load_database_data(self) -> bool:
        """Load and validate data from MongoDB database"""
        try:
            if self.db is None:
                logger.error("Database connection not available")
                return False
            
            # Get all pending tasks with user information
            tasks = list(self.db['tasks'].find({'status': 'Pending'}))
            
            if not tasks:
                logger.info("No pending tasks found")
                self.data = pd.DataFrame()
                return True
            
            # Enrich tasks with user information
            enriched_tasks = []
            for task in tasks:
                user = self.db['users'].find_one({'_id': ObjectId(task['assigned_to'])})
                
                if user:
                    # Convert due_date to date object if it's datetime
                    due_date = task.get('due_date')
                    if isinstance(due_date, datetime):
                        due_date = due_date.date()
                    
                    enriched_tasks.append({
                        'Domain': task.get('domain', 'General'),
                        'Task': task.get('title', ''),
                        'Task Description': task.get('description', ''),
                        'Email': user.get('email', ''),
                        'User Name': user.get('name', 'Unknown'),
                        'Attachment Link': task.get('attachment', ''),
                        'Status': task.get('status', 'Pending'),
                        'Due Date': due_date,
                        'Frequency': task.get('frequency', 'One-time')
                    })
            
            self.data = pd.DataFrame(enriched_tasks)
            
            # Validate required columns
            required_columns = ['Domain', 'Task', 'Task Description', 'Email', 'Attachment Link', 
                              'Status', 'Due Date', 'Frequency']
            missing_columns = [col for col in required_columns if col not in self.data.columns]
            
            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                return False
            
            # Filter out tasks without valid email addresses
            original_count = len(self.data)
            self.data = self.data[self.data['Email'].notna() & (self.data['Email'] != '')]
            if len(self.data) < original_count:
                logger.warning(f"Filtered out {original_count - len(self.data)} tasks without valid email addresses")
            
            logger.info(f"Successfully loaded {len(self.data)} tasks across {self.data['Domain'].nunique()} domains")
            if len(self.data) > 0:
                logger.info(f"Users with tasks: {self.data['Email'].unique().tolist()}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return False

    def get_overdue_tasks(self, days_overdue: int = 15) -> pd.DataFrame:
        """Get tasks that are overdue by specified number of days"""
        today = datetime.now().date()
        
        # FIXED: Better date filtering with error handling
        try:
            # Ensure we only work with valid dates
            valid_dates_data = self.data[self.data['Due Date'].notna()].copy()
            
            overdue_tasks = valid_dates_data[
                (valid_dates_data['Status'].str.lower() == 'pending') &
                (valid_dates_data['Due Date'] < today)
            ].copy()
            
            if overdue_tasks.empty:
                logger.info(f"No overdue tasks found")
                return overdue_tasks
            
            # FIXED: Calculate days overdue safely
            overdue_tasks['Days Overdue'] = overdue_tasks['Due Date'].apply(
                lambda x: (today - x).days if pd.notna(x) else 0
            )
            
            # Filter for tasks overdue by specified days or more
            overdue_tasks = overdue_tasks[overdue_tasks['Days Overdue'] >= days_overdue]
            
            logger.info(f"Found {len(overdue_tasks)} tasks overdue by {days_overdue}+ days across {overdue_tasks['Domain'].nunique()} domains")
            
            if not overdue_tasks.empty:
                logger.info(f"Domains with overdue tasks: {overdue_tasks['Domain'].unique().tolist()}")
                logger.info(f"Max days overdue: {overdue_tasks['Days Overdue'].max()}")
            
            return overdue_tasks
            
        except Exception as e:
            logger.error(f"Error finding overdue tasks: {e}")
            return pd.DataFrame()

    def get_department_head_email(self, domain: str) -> str:
        """Get department head email for a given domain"""
        domain_clean = domain.strip()
        
        # Try exact match first (case-sensitive)
        if domain_clean in self.department_heads:
            return self.department_heads[domain_clean]
        
        # Try case-insensitive exact match
        domain_lower = domain_clean.lower()
        for dept_domain, email in self.department_heads.items():
            if dept_domain.lower() == domain_lower:
                return email
        
        # Try partial matching for domains that might have variations
        for dept_domain, email in self.department_heads.items():
            dept_lower = dept_domain.lower()
            if (dept_lower in domain_lower or 
                domain_lower in dept_lower or
                dept_lower.replace('-', ' ').replace('_', ' ') in domain_lower.replace('-', ' ').replace('_', ' ') or
                domain_lower.replace('-', ' ').replace('_', ' ') in dept_lower.replace('-', ' ').replace('_', ' ')):
                return email
        
        # Default fallback - send to IT governance for unknown domains
        logger.warning(f"No department head found for domain '{domain}', using IT-Governance as fallback")
        return self.department_heads['IT-Governance']

    def create_escalation_email_content(self, department_tasks: pd.DataFrame, department_head: str, domain: str) -> str:
        """Create HTML email content for escalation reports"""
        task_count = len(department_tasks)
        max_days_overdue = department_tasks['Days Overdue'].max()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                .header {{ background-color: #fff3cd; padding: 20px; text-align: center; border-radius: 5px; border-left: 6px solid #ffc107; }}
                .urgent-section {{ margin: 20px 0; padding: 15px; background-color: #f8d7da; border-radius: 5px; border-left: 6px solid #dc3545; }}
                .task-table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                .task-table th, .task-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                .task-table th {{ background-color: #dc3545; color: white; }}
                .task-table tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .critical {{ color: #dc3545; font-weight: bold; }}
                .footer {{ margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
                .summary {{ background-color: #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Compliance Task  Report</h2>
                <p>Domain: <strong>{domain}</strong> | Department Head: <strong></strong></p>
            </div>
            
            <div class="urgent-section">
                <h3>📋 Escalation Summary</h3>
                <p><strong>{task_count} tasks</strong> are overdue by <strong>15+ days</strong> in your department.</p>
                <p>Maximum days overdue: <strong>{max_days_overdue} days</strong></p>
            </div>

            <table class="task-table">
                <thead>
                    <tr>
                        <th>Task</th>
                        <th>Assigned To</th>
                        <th>Task Description</th>
                        <th>Original Due Date</th>
                        <th>Days Overdue</th>
                        <th>Frequency</th>
                        <th>Attachment Link</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for _, task in department_tasks.iterrows():
            critical_class = "critical" if task['Days Overdue'] > 30 else ""
            
            html_content += f"""
                    <tr>
                        <td><strong>{task['Task']}</strong></td>
                        <td>{task['User Name']} ({task['Email']})</td>
                        <td>{task['Task Description']}</td>
                        <td class="{critical_class}">{task['Due Date'].strftime('%Y-%m-%d')}</td>
                        <td class="{critical_class}">{task['Days Overdue']} days</td>
                        <td>{task['Frequency']}</td>
                        <td><a href="{task['Attachment Link']}" target="_blank">Upload Document</a></td>
                    </tr>
            """
        
        html_content += f"""
                </tbody>
            </table>
            
            <div class="footer">
                <h3>🎯 Required Actions:</h3>
                <ul>
                    <li>Follow up with the assigned team members immediately</li>
                    <li>Ensure completion of these overdue compliance tasks</li>
                    <li>Update task status in the system once completed</li>
                </ul>
                
                <p><strong>Note:</strong> This is an automated escalation report generated for tasks overdue by 15+ days.</p>
                <p><strong>Domain:</strong> {domain}</p>
                <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html_content

    def send_escalation_reports(self, dry_run: bool = False) -> Dict[str, Any]:
        """Send escalation reports to department heads for overdue tasks"""
        if not self.load_database_data():
            return {"success": False, "error": "Failed to load database data"}
        
        # Get tasks overdue by 15+ days
        overdue_tasks = self.get_overdue_tasks(days_overdue=15)
        
        if overdue_tasks.empty:
            logger.info("No tasks overdue by 15+ days - no escalation reports to send")
            return {"success": True, "escalation_emails_sent": 0, "total_overdue_tasks": 0}
        
        # Group overdue tasks by domain and find department heads
        domain_escalations = {}
        
        for domain in overdue_tasks['Domain'].unique():
            domain_tasks = overdue_tasks[overdue_tasks['Domain'] == domain]
            department_head_email = self.get_department_head_email(domain)
            
            if domain not in domain_escalations:
                domain_escalations[domain] = {
                    'email': department_head_email,
                    'tasks': domain_tasks
                }
            else:
                # Merge tasks for the same department head
                domain_escalations[domain]['tasks'] = pd.concat([domain_escalations[domain]['tasks'], domain_tasks])
        
        # Dry run mode
        if dry_run:
            logger.info("🚀 DRY RUN MODE - No escalation emails will be actually sent")
            print(f"\n📋 ESCALATION DRY RUN RESULTS:")
            print(f"📧 Would send escalation reports to {len(domain_escalations)} department heads")
            print(f"📊 Total overdue tasks: {len(overdue_tasks)}")
            
            for domain, escalation in domain_escalations.items():
                dept_head = escalation['email']
                task_count = len(escalation['tasks'])
                print(f"   📨 To: {dept_head} (Domain: {domain}), Overdue Tasks: {task_count}")
                
            return {
                "success": True,
                "dry_run": True,
                "would_send_escalations": len(domain_escalations),
                "total_overdue_tasks": len(overdue_tasks),
                "domains_affected": list(domain_escalations.keys())
            }
        
        # Actual escalation email sending
        escalation_emails_sent = 0
        escalation_emails_failed = 0
        
        for domain, escalation in domain_escalations.items():
            department_head_email = escalation['email']
            domain_tasks = escalation['tasks']
            
            # Create escalation email content
            html_content = self.create_escalation_email_content(domain_tasks, department_head_email, domain)
            subject = f"{domain} Department - {len(domain_tasks)} Tasks Overdue by 15+ Days"
            
            # Send escalation email
            if self.send_email(department_head_email, subject, html_content):
                escalation_emails_sent += 1
                logger.info(f"Escalation email sent to {department_head_email} for {len(domain_tasks)} tasks in {domain} domain")
            else:
                escalation_emails_failed += 1
                logger.error(f"Failed to send escalation email to {department_head_email} for {domain} domain")
        
        result = {
            "success": True,
            "escalation_emails_sent": escalation_emails_sent,
            "escalation_emails_failed": escalation_emails_failed,
            "total_overdue_tasks": len(overdue_tasks),
            "domains_affected": list(domain_escalations.keys()),
            "department_heads_contacted": list(set(escalation['email'] for escalation in domain_escalations.values()))
        }
        
        logger.info(f"Escalation processing complete: {escalation_emails_sent} emails sent, {escalation_emails_failed} failed")
        return result

    # === EXISTING METHODS (KEEP THESE FROM YOUR ORIGINAL CODE) ===
    
    def filter_tasks_by_schedule(self, schedule_type: str) -> pd.DataFrame:
        """Filter tasks based on schedule type (monthly, quarterly, reminder, daily)"""
        today = datetime.now().date()
        
        if schedule_type == "monthly":
            # Monthly tasks - send on 1st of month
            if today.day != 1:
                logger.info("Not the 1st of month - skipping monthly tasks")
                return pd.DataFrame()
            
            monthly_tasks = self.data[
                (self.data['Frequency'].str.lower().str.contains('monthly', na=False)) &
                (self.data['Status'].str.lower() == 'pending')
            ]
            logger.info(f"Found {len(monthly_tasks)} monthly tasks across {monthly_tasks['Domain'].nunique()} domains")
            return monthly_tasks
            
        elif schedule_type == "quarterly":
            # Quarterly tasks - send on 25th of the last month of each quarter
            quarter_months = [3, 6, 9, 12]
            current_month = today.month
            current_day = today.day
            
            if current_month not in quarter_months or current_day != 25:
                logger.info(f"Not 25th of a quarter-end month (current: {today}) - skipping quarterly tasks")
                return pd.DataFrame()
            
            quarterly_tasks = self.data[
                (self.data['Frequency'].str.lower().str.contains('quarterly', na=False)) &
                (self.data['Status'].str.lower() == 'pending')
            ]
            logger.info(f"Found {len(quarterly_tasks)} quarterly tasks across {quarterly_tasks['Domain'].nunique()} domains")
            return quarterly_tasks
            
        elif schedule_type == "daily":
            # Daily tasks - send every day
            daily_tasks = self.data[
                (self.data['Status'].str.lower() == 'pending') &
                (self.data['Due Date'] >= today)
            ]
            logger.info(f"Found {len(daily_tasks)} tasks for daily reminders across {daily_tasks['Domain'].nunique()} domains")
            return daily_tasks
            
        elif schedule_type == "reminder":
            # Weekly reminders - send every Monday for pending tasks
            if today.weekday() != 0:
                logger.info("Not Monday - skipping weekly reminders")
                return pd.DataFrame()
            
            reminder_tasks = self.data[
                (self.data['Status'].str.lower() == 'pending') &
                (self.data['Due Date'] >= today)
            ]
            logger.info(f"Found {len(reminder_tasks)} tasks for reminders across {reminder_tasks['Domain'].nunique()} domains")
            return reminder_tasks
            
        else:
            logger.error(f"Unknown schedule type: {schedule_type}")
            return pd.DataFrame()
    
    def create_email_content(self, user_tasks: pd.DataFrame, schedule_type: str) -> str:
        """Create HTML email content for user tasks"""
        user_email = user_tasks['Email'].iloc[0]
        user_name = user_tasks['User Name'].iloc[0] if 'User Name' in user_tasks.columns and pd.notna(user_tasks['User Name'].iloc[0]) else 'User'
        task_count = len(user_tasks)
        
        email_type = schedule_type.capitalize()
        if schedule_type == "reminder":
            email_type = "Weekly Reminder"
        elif schedule_type == "daily":
            email_type = "Daily Reminder"
        
        # Group tasks by domain for better organization
        tasks_by_domain = user_tasks.groupby('Domain')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 5px; }}
                .domain-section {{ margin: 20px 0; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
                .domain-title {{ font-size: 1.2em; font-weight: bold; color: #495057; margin-bottom: 10px; }}
                .task-table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                .task-table th, .task-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                .task-table th {{ background-color: #4CAF50; color: white; }}
                .task-table tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .urgent {{ color: #ff6b6b; font-weight: bold; }}
                .footer {{ margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
                .summary {{ background-color: #d4edda; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .quarter-notice {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Compliance Task {email_type}</h2>
                <p>Hello {user_name}, you have {task_count} pending compliance task(s) across {len(tasks_by_domain)} domain(s)</p>
            </div>
        """
        
        # Add quarterly notice if applicable
        if schedule_type == "quarterly":
            html_content += """
            <div class="quarter-notice">
                <h3>📅 Quarterly Compliance Notice</h3>
                <p><strong>This is your quarterly compliance reminder.</strong> Please ensure all quarterly tasks are completed before the end of the current quarter.</p>
            </div>
            """
        
        html_content += f"""
            <div class="summary">
                <h3>📊 Task Summary by Domain:</h3>
                <ul>
        """
        
        # Add domain summary
        for domain, domain_tasks in tasks_by_domain:
            html_content += f'<li><strong>{domain}</strong>: {len(domain_tasks)} task(s)</li>'
        
        html_content += """
                </ul>
            </div>
        """
        
        # Add tasks organized by domain
        for domain, domain_tasks in tasks_by_domain:
            html_content += f"""
            <div class="domain-section">
                <div class="domain-title">🏢 Domain: {domain}</div>
                <table class="task-table">
                    <thead>
                        <tr>
                            <th>Task</th>
                            <th>Task Description</th>
                            <th>Deadline</th>
                            <th>Frequency</th>
                            <th>Attachment Link</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for _, task in domain_tasks.iterrows():
                days_remaining = (task['Due Date'] - datetime.now().date()).days
                urgent_class = "urgent" if days_remaining <= 3 else ""
                
                html_content += f"""
                        <tr>
                            <td><strong>{task['Task']}</strong></td>
                            <td>{task['Task Description']}</td>
                            <td class="{urgent_class}">{task['Due Date'].strftime('%Y-%m-%d')} ({days_remaining} days remaining)</td>
                            <td>{task['Frequency']}</td>
                            <td><a href="{task['Attachment Link']}" target="_blank">Upload Files</a></td>
                        </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
            </div>
            """
        
        html_content += f"""
            <div class="footer">
                <p><strong>Action Required:</strong> Please complete these tasks by their respective deadlines.</p>
                <p><strong>Note:</strong> This is an automated message. Please do not reply to this email.</p>
                <p><strong>Domains Affected:</strong> {", ".join(tasks_by_domain.groups.keys())}</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via SMTP"""
        try:
            if not all([self.smtp_username, self.smtp_password]):
                logger.error("SMTP credentials are incomplete")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email with better error handling
            logger.info(f"Attempting to send email to {to_email}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False
    
    def process_tasks(self, schedule_type: str, dry_run: bool = False) -> Dict[str, Any]:
        """Main processing function with dry run option"""
        if not self.load_database_data():
            return {"success": False, "error": "Failed to load database data"}
        
        # Filter tasks based on schedule
        filtered_tasks = self.filter_tasks_by_schedule(schedule_type)
        
        if filtered_tasks.empty:
            logger.info(f"No tasks to process for {schedule_type}")
            return {"success": True, "emails_sent": 0, "total_tasks": 0, "unique_users": 0, "domains_affected": 0}
        
        # Group tasks by email
        grouped_tasks = filtered_tasks.groupby('Email')
        emails_sent = 0
        emails_failed = 0
        
        email_subject = f"Compliance Task {schedule_type.capitalize()}"
        if schedule_type == "reminder":
            email_subject = "Weekly Compliance Task Reminder"
        elif schedule_type == "daily":
            email_subject = "Daily Compliance Task Reminder"
        elif schedule_type == "quarterly":
            email_subject = "Quarterly Compliance Task Reminder - Action Required"
        
        # Dry run mode
        if dry_run:
            logger.info("🚀 DRY RUN MODE - No emails will be actually sent")
            print(f"\n📋 DRY RUN RESULTS for {schedule_type}:")
            print(f"📧 Would send emails to {len(grouped_tasks)} users")
            print(f"📊 Would process {len(filtered_tasks)} tasks")
            print(f"🏢 Domains affected: {filtered_tasks['Domain'].nunique()}")
            
            for email, tasks in grouped_tasks:
                user_name = tasks['User Name'].iloc[0] if 'User Name' in tasks.columns and pd.notna(tasks['User Name'].iloc[0]) else 'Unknown'
                print(f"   📨 To: {user_name} ({email}), Tasks: {len(tasks)}")
                
            return {
                "success": True,
                "dry_run": True,
                "would_send_emails": len(grouped_tasks),
                "total_tasks": len(filtered_tasks),
                "domains_affected": filtered_tasks['Domain'].nunique()
            }
        
        # Actual email sending
        for email, tasks in grouped_tasks:
            # Create email content
            html_content = self.create_email_content(tasks, schedule_type)
            
            # Send email
            if self.send_email(email, email_subject, html_content):
                emails_sent += 1
            else:
                emails_failed += 1
        
        result = {
            "success": True,
            "emails_sent": emails_sent,
            "emails_failed": emails_failed,
            "total_tasks": len(filtered_tasks),
            "unique_users": len(grouped_tasks),
            "domains_affected": filtered_tasks['Domain'].nunique()
        }
        
        logger.info(f"Processing complete: {emails_sent} emails sent, {emails_failed} failed, {result['domains_affected']} domains affected")
        return result


def main():
    dry_run = "--dry-run" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if len(args) != 1:
        print("Usage: python script.py <schedule_type> [--dry-run]")
        print("Valid schedule types: daily, monthly, quarterly, reminder, escalation")
        sys.exit(1)

    schedule_type = args[0].lower()
    valid_types = ["daily", "monthly", "quarterly", "reminder", "escalation"]

    if schedule_type not in valid_types:
        print(f"Invalid schedule type. Must be one of {valid_types}")
        sys.exit(1)

    db_file = "task_management.db"
    if not os.path.exists(db_file):
        logger.error(f"Database file not found: {db_file}")
        sys.exit(1)

    system = ComplianceEmailSystem()
    
    if schedule_type == "escalation":
        result = system.send_escalation_reports(dry_run=dry_run)
    else:
        result = system.process_tasks(schedule_type, dry_run=dry_run)

    if result.get("success"):
        if dry_run:
            print(f"✅ DRY RUN completed for {schedule_type} tasks")
        else:
            print(f"✅ Successfully processed {schedule_type} tasks")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
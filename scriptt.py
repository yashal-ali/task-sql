import os
import sys
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import streamlit as st
import pyodbc
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ComplianceEmailSystem:
    def __init__(self):
        """Initialize the Compliance Email System"""
        logger.info("✅ Initializing Compliance Email System with MSSQL database")
        
        # SMTP configuration
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
        
        # Load department heads from database
        self.department_heads = self.load_department_heads_from_db()
        
        if not self.department_heads:
            logger.warning("⚠️ No department heads loaded from database!")

    def load_department_heads_from_db(self) -> Dict[str, str]:
        """Load department heads from the domains table in database"""
        conn = get_db_connection()
        if conn is None:
            logger.error("Failed to connect to database for loading department heads")
            return {}
        
        try:
            # Updated query to match database.py structure
            query = """
                SELECT domain_name, mancom_member_email 
                FROM domains 
                WHERE mancom_member_email IS NOT NULL 
                AND mancom_member_email != ''
                AND (is_active = 1 OR is_active IS NULL)
            """
            
            df = pd.read_sql(query, conn)
            
            if df.empty:
                logger.warning("No department heads found in domains table")
                return {}
            
            # Convert to dictionary (domain_name -> mancom_member_email)
            dept_heads = dict(zip(df['domain_name'], df['mancom_member_email']))
            
            logger.info(f"✅ Loaded {len(dept_heads)} department heads from database")
            logger.info(f"Domains loaded: {list(dept_heads.keys())}")
            
            return dept_heads
            
        except Exception as e:
            logger.error(f"Error loading department heads from database: {e}")
            return {}
        finally:
            conn.close()

    def get_department_head_email(self, domain: str) -> Optional[str]:
        """Get department head email for a given domain from database"""
        if not self.department_heads:
            logger.error(f"No department heads available for domain '{domain}'")
            return None
        
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
        
        # No match found
        logger.warning(f"No department head found for domain '{domain}' in database")
        return None

    def load_database_data(self) -> bool:
        """Load and validate data from MSSQL database"""
        try:
            # Get all pending tasks
            tasks_df = get_tasks(role='admin', include_closed=False)
            
            if tasks_df.empty:
                logger.info("No pending tasks found")
                self.data = pd.DataFrame()
                return True
            
            # Filter only pending tasks
            pending_tasks = tasks_df[tasks_df['status'].isin(['open', 'in_progress'])]
            
            if pending_tasks.empty:
                logger.info("No pending tasks found")
                self.data = pd.DataFrame()
                return True
            
            # Enrich tasks with user information
            enriched_tasks = []
            for _, task in pending_tasks.iterrows():
                # Convert due_date to date object if it's datetime
                due_date = task.get('due_date')
                if isinstance(due_date, (datetime, pd.Timestamp)):
                    due_date = due_date.date()
                elif due_date is None:
                    due_date = None
                
                # Get assigned user details
                assigned_username = task.get('assigned_username', 'Unknown')
                assigned_email = task.get('assigned_email', '')
                
                enriched_tasks.append({
                    'Domain': task.get('domain', 'General'),
                    'Task': task.get('title', ''),
                    'Task Description': task.get('description', ''),
                    'Email': assigned_email,
                    'User Name': assigned_username,
                    'Attachment Link': task.get('attachment', ''),
                    'Status': task.get('status', 'open'),
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
        
        try:
            # Ensure we only work with valid dates
            valid_dates_data = self.data[self.data['Due Date'].notna()].copy()
            
            overdue_tasks = valid_dates_data[
                (valid_dates_data['Status'].str.lower().isin(['open', 'in_progress'])) &
                (valid_dates_data['Due Date'] < today)
            ].copy()
            
            if overdue_tasks.empty:
                logger.info(f"No overdue tasks found")
                return overdue_tasks
            
            # Calculate days overdue safely
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
                <h2>Compliance Task Escalation Report</h2>
                <p>Domain: <strong>{domain}</strong></p>
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
        domains_without_heads = []
        
        for domain in overdue_tasks['Domain'].unique():
            domain_tasks = overdue_tasks[overdue_tasks['Domain'] == domain]
            department_head_email = self.get_department_head_email(domain)
            
            if department_head_email is None:
                logger.warning(f"Skipping domain '{domain}' - no department head found in database")
                domains_without_heads.append(domain)
                continue
            
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
            
            if domains_without_heads:
                print(f"⚠️ Domains without department heads (SKIPPED): {domains_without_heads}")
            
            for domain, escalation in domain_escalations.items():
                dept_head = escalation['email']
                task_count = len(escalation['tasks'])
                print(f"   📨 To: {dept_head} (Domain: {domain}), Overdue Tasks: {task_count}")
                
            return {
                "success": True,
                "dry_run": True,
                "would_send_escalations": len(domain_escalations),
                "total_overdue_tasks": len(overdue_tasks),
                "domains_affected": list(domain_escalations.keys()),
                "domains_without_heads": domains_without_heads
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
            "domains_without_heads": domains_without_heads,
            "department_heads_contacted": list(set(escalation['email'] for escalation in domain_escalations.values()))
        }
        
        logger.info(f"Escalation processing complete: {escalation_emails_sent} emails sent, {escalation_emails_failed} failed")
        if domains_without_heads:
            logger.warning(f"Domains without department heads: {domains_without_heads}")
        
        return result

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
                (self.data['Status'].str.lower().isin(['open', 'in_progress']))
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
                (self.data['Status'].str.lower().isin(['open', 'in_progress']))
            ]
            logger.info(f"Found {len(quarterly_tasks)} quarterly tasks across {quarterly_tasks['Domain'].nunique()} domains")
            return quarterly_tasks
            
        elif schedule_type == "daily":
            # Daily tasks - send every day
            daily_tasks = self.data[
                (self.data['Status'].str.lower().isin(['open', 'in_progress'])) &
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
                (self.data['Status'].str.lower().isin(['open', 'in_progress'])) &
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
        elif schedule_type == "quarterly":
            email_type = "Quarterly Reminder"
        
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


# Database helper functions
@st.cache_resource
def get_db_connection():
    """Creates a MSSQL connection"""
    try:
        drivers = pyodbc.drivers()
        
        # Try each driver until one works
        for driver in drivers:
            try:
                conn = pyodbc.connect(
                    f"DRIVER={{{driver}}};"
                    "SERVER=localhost,1433;"
                    "DATABASE=Task_flo_Database;"
                    "UID=sa;"
                    "PWD=Yashal309;"
                    "Encrypt=yes;"
                    "TrustServerCertificate=yes;"
                )
                return conn
            except Exception:
                continue
        
        logger.error("All ODBC drivers failed to connect")
        return None
        
    except Exception as e:
        logger.error(f"Failed to connect to SQL Server: {str(e)}")
        return None


def get_tasks(user_id: int = None, role: str = 'user', include_closed: bool = True) -> pd.DataFrame:
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
        logger.error(f"Error fetching tasks: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()


def main():
    """Main function to run the compliance email system"""
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
        
        # Print summary
        if schedule_type == "escalation":
            print(f"   Escalation emails sent: {result.get('escalation_emails_sent', 0)}")
            print(f"   Total overdue tasks: {result.get('total_overdue_tasks', 0)}")
            if result.get('domains_without_heads'):
                print(f"   ⚠️ Domains without department heads: {result.get('domains_without_heads')}")
        else:
            print(f"   Emails sent: {result.get('emails_sent', 0)}")
            print(f"   Total tasks: {result.get('total_tasks', 0)}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()

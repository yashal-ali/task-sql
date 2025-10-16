# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date
# import smtplib
# import io
# from database import *
# import os
# import plotly.express as px
# import plotly.graph_objects as go
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.lib import colors
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER, TA_LEFT
# import tempfile


# os.environ['PATH'] += os.pathsep + ':/usr/bin'
# def set_page_styling():
#     st.markdown("""
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
#     * {
#         font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
#     }
    
#     .stApp {
#         background-color: #f8fafc;
#     }
    
#     .main .block-container {
#         background-color: #ffffff;
#         padding: 2.5rem;
#         max-width: 1400px;
#         box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
#     }
    
#     [data-testid="stSidebar"] {
#         background-color: #ffffff;
#         border-right: 1px solid #e2e8f0;
#     }
    
#     h1 {
#         color: #0f172a;
#         font-weight: 700;
#         font-size: 2rem;
#         margin-bottom: 0.5rem;
#         letter-spacing: -0.025em;
#         border-bottom: 2px solid #2563eb;
#         padding-bottom: 0.75rem;
#     }
    
#     h2 {
#         color: #1e293b;
#         font-weight: 600;
#         font-size: 1.5rem;
#         margin-bottom: 1rem;
#     }
    
#     h3 {
#         color: #334155;
#         font-weight: 600;
#         font-size: 1.125rem;
#     }
    
#     .stButton>button {
#         background-color: #2563eb;
#         color: white;
#         border: none;
#         border-radius: 6px;
#         padding: 0.625rem 1.5rem;
#         font-weight: 600;
#         font-size: 0.875rem;
#         transition: all 0.2s ease;
#         letter-spacing: 0.015em;
#     }
    
#     .stButton>button:hover {
#         background-color: #1e40af;
#         box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
#     }
    
#     .stButton>button:active {
#         background-color: #1e3a8a;
#     }
    
#     .stTextInput>div>div>input,
#     .stTextArea>div>div>textarea,
#     .stSelectbox>div>div>div,
#     .stDateInput>div>div>input {
#         border: 1px solid #cbd5e1;
#         border-radius: 6px;
#         padding: 0.625rem 0.875rem;
#         font-size: 14px;
#         transition: all 0.2s ease;
#         background-color: #ffffff;
#     }
    
#     .stTextInput>div>div>input:focus,
#     .stTextArea>div>div>textarea:focus,
#     .stSelectbox>div>div>div:focus,
#     .stDateInput>div>div>input:focus {
#         border-color: #2563eb;
#         box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
#         outline: none;
#     }
    
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 0.25rem;
#         background-color: transparent;
#         border-bottom: 1px solid #e2e8f0;
#     }
    
#     .stTabs [data-baseweb="tab"] {
#         background-color: transparent;
#         padding: 0.75rem 1.25rem;
#         font-weight: 600;
#         color: #64748b;
#         border-bottom: 2px solid transparent;
#         transition: all 0.2s ease;
#     }
    
#     .stTabs [data-baseweb="tab"]:hover {
#         color: #334155;
#     }
    
#     .stTabs [aria-selected="true"] {
#         background-color: transparent;
#         color: #2563eb;
#         border-bottom: 2px solid #2563eb;
#     }
    
#     .stExpander {
#         border: 1px solid #e2e8f0;
#         border-radius: 6px;
#         overflow: hidden;
#         margin-bottom: 0.75rem;
#         background-color: #ffffff;
#     }
    
#     .streamlit-expanderHeader {
#         background-color: #f8fafc;
#         font-weight: 600;
#         padding: 1rem 1.25rem;
#         transition: background-color 0.2s ease;
#         color: #334155;
#     }
    
#     .streamlit-expanderHeader:hover {
#         background-color: #f1f5f9;
#     }
    
#     div[data-testid="stMetricValue"] {
#         font-size: 1.875rem;
#         font-weight: 700;
#         color: #0f172a;
#     }
    
#     div[data-testid="stMetricLabel"] {
#         font-size: 0.75rem;
#         font-weight: 600;
#         color: #64748b;
#         text-transform: uppercase;
#         letter-spacing: 0.05em;
#     }
    
#     .stAlert {
#         border-radius: 6px;
#         padding: 1rem 1.25rem;
#         border-left-width: 3px;
#     }
    
#     [data-testid="stSidebar"] .stRadio > label {
#         color: #334155;
#         font-weight: 600;
#         font-size: 0.75rem;
#         text-transform: uppercase;
#         letter-spacing: 0.05em;
#         margin-left: 0.75rem;
#     }
    
#     [data-testid="stSidebar"] .stRadio > div > label {
#         color: #475569;
#         padding: 0.625rem 1rem;
#         border-radius: 6px;
#         transition: all 0.2s ease;
#         font-weight: 500;
#     }
    
#     [data-testid="stSidebar"] .stRadio > div > label:hover {
#         background-color: #f8fafc;
#         color: #1e293b;
#     }
    
#     [data-testid="stSidebar"] .stRadio input:checked + div {
#         background-color: #eff6ff;
#         border-left: 3px solid #2563eb;
#     }
    
#     [data-testid="stSidebar"] .stRadio input:checked + div > label {
#         color: #2563eb;
#         font-weight: 600;
#     }
    
#     .stDataFrame {
#         border: 1px solid #e2e8f0;
#         border-radius: 6px;
#         overflow: hidden;
#     }
    
#     hr {
#         margin: 2rem 0;
#         border: none;
#         border-top: 1px solid #e2e8f0;
#     }
    
#     .stProgress > div > div > div > div {
#         background-color: #2563eb;
#     }
    
#     </style>
#     """, unsafe_allow_html=True)

# def create_metric_card(value, label, border_color="#2563eb"):
#     st.markdown(f"""
#     <div style="
#         margin: 0.75rem;
#         background-color: #ffffff;
#         border: 1px solid #e2e8f0;
#         border-left: 3px solid {border_color};
#         border-radius: 8px;
#         padding: 1.5rem;
#         text-align: center;
#         box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
#     ">
#         <div style="font-size: 2rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem;">{value}</div>
#         <div style="font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
#     </div>
#     """, unsafe_allow_html=True)

# def create_task_card(task):
#     status_class = "status-completed" if task['status'] == 'Completed' else "status-pending"
#     border_color = "#10b981" if task['status'] == 'Completed' else "#f59e0b"
#     status_bg = "#d1fae5" if task['status'] == 'Completed' else "#fef3c7"
#     status_text = "#065f46" if task['status'] == 'Completed' else "#92400e"
    
#     attachment_html = ""
#     if task['attachment'] and str(task['attachment']).strip() and str(task['attachment']) != 'nan':
#         attachment_html = f'<a href="{task["attachment"]}" target="_blank" style="color: #2563eb; text-decoration: none; font-size: 0.8125rem; font-weight: 500;">View Attachment</a>'
    
#     st.markdown(f"""
#     <div style='
#         background-color: #ffffff;
#         border: 1px solid #e2e8f0;
#         border-left: 3px solid {border_color};
#         border-radius: 8px;
#         padding: 1.25rem;
#         margin: 0.75rem 0;
#         box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
#     '>
#         <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;'>
#             <div style='flex: 1;'>
#                 <h3 style='margin: 0 0 0.5rem 0; color: #0f172a; font-size: 1.125rem; font-weight: 600;'>{task['title']}</h3>
#                 <p style='color: #64748b; margin: 0 0 0.5rem 0; font-size: 0.875rem; line-height: 1.5;'>{task['description']}</p>
#                 {attachment_html}
#             </div>
#             <div style='display: flex; align-items: center; gap: 0.75rem; margin-left: 1rem;'>
#                 <span style='background-color: {status_bg}; color: {status_text}; padding: 0.375rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;'>
#                     {task['status']}
#                 </span>
#                 <span style='background-color: #dbeafe; color: #1e40af; padding: 0.375rem 0.625rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; min-width: 2rem; text-align: center;'>
#                     {task['comment_count']}
#                 </span>
#             </div>
#         </div>
        
#         <div style='display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.8125rem;'>
#             <span style='background-color: #f1f5f9; color: #334155; padding: 0.25rem 0.625rem; border-radius: 4px; font-weight: 500;'>
#                 {task['domain']}
#             </span>
#             <span style='background-color: #f1f5f9; color: #334155; padding: 0.25rem 0.625rem; border-radius: 4px; font-weight: 500;'>
#                 Due: {task['due_date']}
#             </span>
#             <span style='background-color: #f1f5f9; color: #334155; padding: 0.25rem 0.625rem; border-radius: 4px; font-weight: 500;'>
#                 {task['frequency']}
#             </span>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

# def show_login():
#     st.markdown("""
#     <div style='text-align: center; padding: 3rem 1rem 2rem;'>
#         <h1 style='color: #0f172a; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 800; border: none;'>TaskFlow Pro</h1>
#         <p style='color: #64748b; font-size: 1.125rem; font-weight: 500;'>Task Management System</p>
#     </div>
#     """, unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns([1, 2, 1])
    
#     with col2:
#         st.markdown("""
#         """, unsafe_allow_html=True)
        
#         st.markdown("<h2 style='text-align: center; color: #0f172a; margin-bottom: 0.5rem; border: none;'>Sign In</h2>", unsafe_allow_html=True)
#         st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem; font-size: 0.875rem;'>Enter your email to access your account</p>", unsafe_allow_html=True)
        
#         email = st.text_input("Email Address", placeholder="your.email@company.com", label_visibility="collapsed")
        
#         st.markdown("<br>", unsafe_allow_html=True)
#         if st.button("Sign In", use_container_width=True):
#             user = get_user_by_email(email)
#             if user:
#                 # get_user_by_email returns a MongoDB document (dictionary)
#                 st.session_state.user_id = str(user['_id'])
#                 st.session_state.user_name = user['name']
#                 st.session_state.user_email = user['email']
#                 st.session_state.user_role = user['role']
#                 st.session_state.logged_in = True
#                 st.rerun()
#             else:
#                st.error("User not found. Please check your email address.")
        
#         # if st.button("Sign In", use_container_width=True):
#         #     user = get_user_by_email(email)
#         #     if user:
#         #         st.session_state.user_id = user[0]
#         #         st.session_state.user_name = user[1]
#         #         st.session_state.user_email = user[2]
#         #         st.session_state.user_role = user[3]
#         #         st.session_state.logged_in = True
#         #         st.rerun()
#         #     else:
#         #         st.error("User not found. Please check your email address.")
        
#         st.markdown("</div>", unsafe_allow_html=True)

# def show_comment_modal(task_id, task_title):
#     st.markdown(f"<h3 style='color: #0f172a; margin-bottom: 1.5rem; border: none;'>Discussion: {task_title}</h3>", unsafe_allow_html=True)
    
#     comments_df = get_comments(task_id)
    
#     if not comments_df.empty:
#         for _, comment in comments_df.iterrows():
#             st.markdown(f"""
#             <div style='
#                 background-color: #f8fafc;
#                 padding: 1rem;
#                 border-radius: 6px;
#                 margin: 0.75rem 0;
#                 border-left: 3px solid #2563eb;
#             '>
#                 <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
#                     <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
#                     <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
#                 </div>
#                 <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
#             </div>
#             """, unsafe_allow_html=True)
#     else:
#         st.info("No comments yet. Be the first to comment.")
    
#     st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
#     st.subheader("Add Comment")
#     new_comment = st.text_area("Your comment", key=f"comment_{task_id}", height=100, label_visibility="collapsed", placeholder="Write your comment here...")
    
#     if st.button("Post Comment", key=f"submit_{task_id}", use_container_width=True):
#         if new_comment.strip():
#             add_comment(task_id, st.session_state.user_id, new_comment)
#             st.success("Comment posted successfully")
#             st.rerun()
#         else:
#             st.warning("Please enter a comment before posting")

# def show_admin_dashboard():
#     with st.sidebar:
#         st.markdown(f"""
#         <div style='
#             background-color: #f8fafc;
#             padding: 1.5rem;
#             border-radius: 8px;
#             border: 1px solid #e2e8f0;
#             text-align: center;
#             margin-bottom: 1.5rem;
#         '>
#             <div style='width: 64px; height: 64px; background-color: #2563eb; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem; color: white; font-size: 1.5rem; font-weight: 700;'>
#                 {st.session_state.user_name[0]}
#             </div>
#             <h3 style='color: #0f172a; margin: 0 0 0.25rem 0; font-size: 1.125rem;'>{st.session_state.user_name}</h3>
#             <p style='color: #64748b; margin: 0; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Administrator</p>
#         </div>
#         """, unsafe_allow_html=True)
        
#         st.markdown("<div style='color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;'>Navigation</div>", unsafe_allow_html=True)
        
#         menu = st.radio("", 
#                        ["Task Management", "Analytics", "Comments", "Email Center", "Team"],
#                        label_visibility="collapsed")
        
#         st.markdown("<hr style='border-color: #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
#         if st.button("Logout", use_container_width=True):
#             for key in list(st.session_state.keys()):
#                 del st.session_state[key]
#             st.rerun()
    
#     if menu == "Task Management":
#         show_task_management()
#     elif menu == "Analytics":
#         show_analytics_dashboard('admin')
#     elif menu == "Comments":
#         show_comments_page()
#     elif menu == "Email Center":
#         show_email_page()
#     elif menu == "Team":
#         show_user_management()

# def show_task_management():
#     st.title("Task Management")
    
#     tab1, tab2, tab3, tab4, tab5 = st.tabs(["Create Task", "View & Edit", "Delete Task", "Bulk Upload", "All Tasks"])
    
#     with tab1:
#         st.subheader("Create New Task")
#         with st.form("create_task_form"):
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 title = st.text_input("Task Title", placeholder="Enter task title...")
#                 description = st.text_area("Description", placeholder="Describe the task...", height=100)
#                 domain = st.selectbox("Domain", ["SAP", "Network", "EC", "SalesFlo", "NFlo", "Help Desk", "IT-Governance"])
            
#             with col2:
#                 users_df = get_all_users()
#                 user_options = {f"{row['name']} ({row['email']})": row['user_id'] 
#                               for _, row in users_df.iterrows()}
#                 assigned = st.selectbox("Assign To", list(user_options.keys()))
                
#                 attachment = st.text_input("Attachment Link", placeholder="https://...")
#                 status = st.selectbox("Status", ["Pending", "Completed"])
#                 due_date = st.date_input("Due Date")
#                 frequency = st.selectbox("Frequency", ["Monthly", "Quarterly", "Yearly", "One-time"])
            
#             submit = st.form_submit_button("Create Task", use_container_width=True)
            
#             if submit:
#                 if title and description:
#                     create_task(title, description, domain, user_options[assigned], 
#                               attachment, status, due_date, frequency)
#                     st.success("Task created successfully")
#                     st.rerun()
#                 else:
#                     st.error("Title and Description are required")
    
#     with tab2:
#         st.subheader("View & Edit Tasks")
#         tasks_df = get_tasks(role='admin')
        
#         if not tasks_df.empty:
#             st.info("Click status dropdown to update task status directly")
            
#             for idx, row in tasks_df.iterrows():
#                 with st.expander(f"{row['title']} - ID: {row['task_id']} ({row['assigned_name']})", expanded=False):
#                     # Display task info using Streamlit components instead of HTML
#                     st.markdown(f"**Description:** {row['description']}")
                    
#                     col1, col2, col3 = st.columns(3)
#                     with col1:
#                         st.markdown(f"**Domain:** {row['domain']}")
#                     with col2:
#                         st.markdown(f"**Due Date:** {row['due_date']}")
#                     with col3:
#                         st.markdown(f"**Frequency:** {row['frequency']}")
                    
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.markdown(f"**Status:** {row['status']}")
#                     with col2:
#                         st.markdown(f"**Comments:** {row['comment_count']}")
                    
#                     if row['attachment'] and str(row['attachment']).strip() and str(row['attachment']) != 'nan':
#                         st.markdown(f"**Attachment:** [View Attachment]({row['attachment']})")
                    
#                     st.markdown("---")
#                     st.markdown("#### Quick Status Update")
#                     col1, col2 = st.columns([3, 1])
#                     with col1:
#                         new_status = st.selectbox(
#                             "Update Status",
#                             ["Pending", "Completed"],
#                             index=0 if row['status'] == "Pending" else 1,
#                             key=f"admin_status_{row['task_id']}"
#                         )
#                     with col2:
#                         if st.button("Update Status", key=f"update_btn_{row['task_id']}"):
#                             if new_status != row['status']:
#                                 update_task_status(row['task_id'], new_status)
#                                 st.success("Status updated")
#                                 st.rerun()
                    
#                     st.markdown("---")
                    
#                     # Comments section
#                     st.markdown(f"#### Comments ({row['comment_count']})")
#                     comments_df = get_comments(row['task_id'])
                    
#                     if not comments_df.empty:
#                         for _, comment in comments_df.iterrows():
#                             st.markdown(f"""
#                             <div style='
#                                 background-color: #f8fafc;
#                                 padding: 1rem;
#                                 border-radius: 6px;
#                                 margin: 0.75rem 0;
#                                 border-left: 3px solid #2563eb;
#                             '>
#                                 <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
#                                     <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
#                                     <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
#                                 </div>
#                                 <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
#                             </div>
#                             """, unsafe_allow_html=True)
#                     else:
#                         st.info("No comments yet")
                    
#                     new_comment = st.text_area("Add a comment", key=f"edit_comment_{row['task_id']}", height=80, placeholder="Write your comment here...")
                    
#                     if st.button("Post Comment", key=f"edit_post_{row['task_id']}", use_container_width=True):
#                         if new_comment.strip():
#                             add_comment(row['task_id'], st.session_state.user_id, new_comment)
#                             st.success("Comment posted")
#                             st.rerun()
#                         else:
#                             st.warning("Please enter a comment")
#     with tab3:
#         st.subheader("Delete Task")
#         tasks_df = get_tasks(role='admin')
        
#         if not tasks_df.empty:
#             task_options = {f"{row['task_id']}: {row['title']} - {row['assigned_name']}": row['task_id'] 
#                           for _, row in tasks_df.iterrows()}
#             selected_task = st.selectbox("Select Task to Delete", list(task_options.keys()))
            
#             col1, col2, col3 = st.columns([1, 1, 1])
#             with col2:
#                 if st.button("Delete Task", type="primary", use_container_width=True):
#                     delete_task(task_options[selected_task])
#                     st.success("Task deleted successfully")
#                     st.rerun()
#         else:
#             st.info("No tasks available to delete")
    
#     with tab4:
#         st.subheader("Bulk Upload Tasks")
#         st.markdown("""
#         <div style='
#             background-color: #eff6ff;
#             padding: 1.25rem;
#             border-radius: 6px;
#             border-left: 3px solid #2563eb;
#             margin-bottom: 1.5rem;
#         '>
#         <h4 style='color: #1e3a8a; margin-top: 0; font-size: 1rem;'>Upload Instructions</h4>
#         <ul style='color: #1e40af; margin-bottom: 0; font-size: 0.875rem;'>
#             <li><strong>Required columns:</strong> Domain, Title, Description, Email, Status, Due_Date, Frequency</li>
#             <li><strong>Date Format:</strong> DD-MM-YYYY or YYYY-MM-DD</li>
#             <li><strong>Valid Domains:</strong> SAP, Network, EC, SalesFlo, NFlo, Help Desk, IT-Governance</li>
#         </ul>
#         </div>
#         """, unsafe_allow_html=True)
        
#         excel_template = download_excel_template()
#         st.download_button(
#             label="Download Excel Template",
#             data=excel_template,
#             file_name="task_upload_template.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             use_container_width=True
#         )
        
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         uploaded_file = st.file_uploader("Choose Excel File", type=['xlsx', 'xls'], key="bulk_upload_file")
        
#         if uploaded_file:
#             try:
#                 df = pd.read_excel(uploaded_file)
#                 st.success("File loaded successfully")
#                 st.write("Preview:")
#                 st.dataframe(df.head(), use_container_width=True)
                
#                 if st.button("Upload Tasks", use_container_width=True):
#                     users_df = get_all_users()
#                     email_to_id = {row['email']: row['user_id'] for _, row in users_df.iterrows()}
                    
#                     success_count = 0
#                     error_count = 0
#                     error_messages = []
                    
#                     progress_bar = st.progress(0)
#                     status_text = st.empty()
                    
#                     for idx, row in df.iterrows():
#                         status_text.text(f"Processing task {idx + 1} of {len(df)}...")
                        
#                         try:
#                             email = str(row['Email']).strip()
                            
#                             if email not in email_to_id:
#                                 error_messages.append(f"Row {idx+2}: Email {email} not found")
#                                 error_count += 1
#                                 continue
                            
#                             due_date_str = str(row['Due_Date'])
#                             try:
#                                 if '-' in due_date_str and len(due_date_str.split('-')[0]) <= 2:
#                                     due_date = pd.to_datetime(due_date_str, format='%d-%m-%Y').date()
#                                 else:
#                                     due_date = pd.to_datetime(due_date_str).date()
#                             except:
#                                 error_messages.append(f"Row {idx+2}: Invalid date format")
#                                 error_count += 1
#                                 continue
                            
#                             attachment = str(row.get('Attachment Link', ''))
#                             if attachment == 'nan' or attachment == 'None':
#                                 attachment = ''
                            
#                             create_task(
#                                 str(row['Title']).strip(),
#                                 str(row['Description']).strip(),
#                                 str(row['Domain']).strip(),
#                                 email_to_id[email],
#                                 attachment,
#                                 str(row['Status']).strip(),
#                                 due_date,
#                                 str(row['Frequency']).strip()
#                             )
#                             success_count += 1
#                         except Exception as e:
#                             error_messages.append(f"Row {idx+2}: {str(e)}")
#                             error_count += 1
                        
#                         progress_bar.progress((idx + 1) / len(df))
                    
#                     progress_bar.empty()
#                     status_text.empty()
                    
#                     if success_count > 0:
#                         st.success(f"{success_count} tasks uploaded successfully")
                    
#                     if error_count > 0:
#                         st.warning(f"{error_count} tasks failed to upload")
#                         with st.expander("View Error Details"):
#                             for msg in error_messages:
#                                 st.error(msg)
                    
#                     if success_count > 0:
#                         st.rerun()
#             except Exception as e:
#                 st.error(f"Error reading file: {e}")
    
#     with tab5:
#         st.subheader("All Tasks Overview")
#         tasks_df = get_tasks(role='admin')
        
#         if not tasks_df.empty:
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])
#             with col2:
#                 domain_filter = st.selectbox(
#                     "Filter by Domain", 
#                     ["All", "SAP", "Network", "EC", "SalesFlo", "NFlo", "Help Desk", "IT-Governance"]
#                 )
#             with col3:
#                 user_filter = st.selectbox(
#                     "Filter by User", 
#                     ["All"] + tasks_df['assigned_name'].unique().tolist()
#                 )
            
#             # Apply filters
#             filtered_df = tasks_df.copy()
#             if status_filter != "All":
#                 filtered_df = filtered_df[filtered_df['status'] == status_filter]
#             if domain_filter != "All":
#                 filtered_df = filtered_df[filtered_df['domain'] == domain_filter]
#             if user_filter != "All":
#                 filtered_df = filtered_df[filtered_df['assigned_name'] == user_filter]
            
#             st.markdown(f"**Showing {len(filtered_df)} tasks**")
            
#             for idx, row in filtered_df.iterrows():
#                 with st.expander(f"{row['title']} - Status-({row['status']})- ({row['assigned_name']})", expanded=False):
#                     # Task info
#                     st.markdown(f"**Description:** {row['description']}")
                    
#                     col1, col2, col3 = st.columns(3)
#                     with col1:
#                         st.markdown(f"**Domain:** {row['domain']}")
#                     with col2:
#                         st.markdown(f"**Due Date:** {row['due_date']}")
#                     with col3:
#                         st.markdown(f"**Frequency:** {row['frequency']}")
                    
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.markdown(f"**Status:** {row['status']}")
#                     with col2:
#                         st.markdown(f"**Comments:** {row['comment_count']}")
                    
#                     if row['attachment'] and str(row['attachment']).strip() and str(row['attachment']) != 'nan':
#                         st.markdown(f"**Attachment:** [View Attachment]({row['attachment']})")
                    
#                     st.markdown("---")
#                     st.markdown("#### Quick Status Update")
#                     col1, col2 = st.columns([3, 1])
#                     with col1:
#                         new_status = st.selectbox(
#                             "Update Status",
#                             ["Pending", "Completed"],
#                             index=0 if row['status'] == "Pending" else 1,
#                             key=f"all_status_{row['task_id']}"
#                         )
#                     with col2:
#                         if st.button("Update Status", key=f"quick_update_{row['task_id']}"):
#                             if new_status != row['status']:
#                                 update_task_status(row['task_id'], new_status)
#                                 st.success("Status updated")
#                                 st.rerun()
                    
#                     st.markdown("---")
                    
#                     # Comments section
#                     st.markdown(f"#### Comments ({row['comment_count']})")
#                     comments_df = get_comments(row['task_id'])
                    
#                     if not comments_df.empty:
#                         for _, comment in comments_df.iterrows():
#                             st.markdown(f"""
#                             <div style='
#                                 background-color: #f8fafc;
#                                 padding: 1rem;
#                                 border-radius: 6px;
#                                 margin: 0.75rem 0;
#                                 border-left: 3px solid #2563eb;
#                             '>
#                                 <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
#                                     <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
#                                     <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
#                                 </div>
#                                 <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
#                             </div>
#                             """, unsafe_allow_html=True)
#                     else:
#                         st.info("No comments yet")
                    
#                     new_comment = st.text_area(
#                         "Add a comment",
#                         key=f"all_comment_{row['task_id']}",
#                         height=80,
#                         placeholder="Write your comment here..."
#                     )
                    
#                     if st.button("Post Comment", key=f"all_post_{row['task_id']}", use_container_width=True):
#                         if new_comment.strip():
#                             add_comment(row['task_id'], st.session_state.user_id, new_comment)
#                             st.success("Comment posted")
#                             st.rerun()
#                         else:
#                             st.warning("Please enter a comment")
#         else:
#             st.info("No tasks available")


# def save_plotly_as_image(fig, width=800, height=500):
#     """Convert plotly figure to image and return as Image object"""
#     img_bytes = fig.to_image(format="png", width=width, height=height)
#     img_buffer = io.BytesIO(img_bytes)
#     img_buffer.seek(0)
    
#     # Save to temporary file
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
#         tmp.write(img_bytes)
#         tmp_path = tmp.name
    
#     return tmp_path

# def generate_pdf_report(tasks_df, role):
#     """Generate a comprehensive PDF report of the analytics dashboard"""
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
#     story = []
#     styles = getSampleStyleSheet()
#     temp_files = []  # Track temporary files for cleanup
    
#     # Custom styles
#     title_style = ParagraphStyle(
#         'CustomTitle',
#         parent=styles['Heading1'],
#         fontSize=24,
#         textColor=colors.HexColor('#2563eb'),
#         spaceAfter=30,
#         alignment=TA_CENTER
#     )
    
#     heading_style = ParagraphStyle(
#         'CustomHeading',
#         parent=styles['Heading2'],
#         fontSize=16,
#         textColor=colors.HexColor('#1e40af'),
#         spaceAfter=12,
#         spaceBefore=12
#     )
    
#     # Title
#     title = Paragraph("Analytics Dashboard Report", title_style)
#     story.append(title)
    
#     # Date
#     date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal'])
#     story.append(date_text)
#     story.append(Spacer(1, 0.3*inch))
    
#     # Summary Metrics
#     story.append(Paragraph("Summary Metrics", heading_style))
    
#     metrics_data = [
#         ['Metric', 'Value'],
#         ['Total Tasks', str(len(tasks_df))],
#         ['Pending Tasks', str(len(tasks_df[tasks_df['status'] == 'Pending']))],
#         ['Completed Tasks', str(len(tasks_df[tasks_df['status'] == 'Completed']))],
#         ['Total Comments', str(int(tasks_df['comment_count'].sum()))]
#     ]
    
#     metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
#     metrics_table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 12),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.grey),
#         ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 1), (-1, -1), 10),
#         ('TOPPADDING', (0, 1), (-1, -1), 8),
#         ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
#     ]))
#     story.append(metrics_table)
#     story.append(Spacer(1, 0.3*inch))
    
#     # Status Distribution
#     story.append(Paragraph("Status Distribution", heading_style))
#     status_counts = tasks_df['status'].value_counts()
#     status_data = [['Status', 'Count', 'Percentage']]
#     for status, count in status_counts.items():
#         percentage = f"{(count/len(tasks_df)*100):.1f}%"
#         status_data.append([status, str(count), percentage])
    
#     status_table = Table(status_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
#     status_table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 12),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
#         ('GRID', (0, 0), (-1, -1), 1, colors.grey),
#         ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 1), (-1, -1), 10),
#         ('TOPPADDING', (0, 1), (-1, -1), 8),
#         ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
#     ]))
#     story.append(status_table)
#     story.append(Spacer(1, 0.3*inch))
    
#     # Add Status Distribution Pie Chart
#     try:
#         status_data = tasks_df['status'].value_counts().reset_index()
#         status_data.columns = ['status', 'count']
#         fig = px.pie(status_data, values='count', names='status',
#                     color_discrete_sequence=['#f59e0b', '#10b981'],
#                     title='Status Distribution')
#         fig.update_layout(
#             font=dict(family="Inter, sans-serif", size=12),
#             showlegend=True
#         )
#         img_path = save_plotly_as_image(fig, width=600, height=400)
#         temp_files.append(img_path)
#         img = Image(img_path, width=5*inch, height=3.3*inch)
#         story.append(img)
#         story.append(Spacer(1, 0.2*inch))
#     except Exception as e:
#         story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
    
#     story.append(PageBreak())
    
#     # Domain Distribution (if domain column exists)
#     if 'domain' in tasks_df.columns:
#         story.append(Paragraph("Tasks by Domain", heading_style))
#         domain_status = tasks_df.groupby(['domain', 'status']).size().unstack(fill_value=0)
#         domain_data = [['Domain', 'Pending', 'Completed', 'Total']]
#         for domain in domain_status.index:
#             pending = domain_status.loc[domain].get('Pending', 0)
#             completed = domain_status.loc[domain].get('Completed', 0)
#             total = pending + completed
#             domain_data.append([domain, str(pending), str(completed), str(total)])
        
#         domain_table = Table(domain_data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.4*inch])
#         domain_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, 0), 12),
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#             ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
#             ('GRID', (0, 0), (-1, -1), 1, colors.grey),
#             ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#             ('FONTSIZE', (0, 1), (-1, -1), 10),
#             ('TOPPADDING', (0, 1), (-1, -1), 8),
#             ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
#         ]))
#         story.append(domain_table)
#         story.append(Spacer(1, 0.2*inch))
        
#         # Add Domain Stacked Bar Chart
#         try:
#             fig = go.Figure()
            
#             if 'Pending' in domain_status.columns:
#                 fig.add_trace(go.Bar(
#                     name='Pending',
#                     x=domain_status.index,
#                     y=domain_status['Pending'],
#                     marker_color='#f59e0b',
#                     text=domain_status['Pending'],
#                     textposition='inside'
#                 ))
            
#             if 'Completed' in domain_status.columns:
#                 fig.add_trace(go.Bar(
#                     name='Completed',
#                     x=domain_status.index,
#                     y=domain_status['Completed'],
#                     marker_color='#10b981',
#                     text=domain_status['Completed'],
#                     textposition='inside'
#                 ))
            
#             fig.update_layout(
#                 barmode='stack',
#                 title='Tasks by Domain (Stacked)',
#                 xaxis_title="Domain",
#                 yaxis_title="Number of Tasks",
#                 font=dict(family="Inter, sans-serif", size=12),
#                 showlegend=True,
#                 legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#             )
            
#             img_path = save_plotly_as_image(fig, width=700, height=450)
#             temp_files.append(img_path)
#             img = Image(img_path, width=6*inch, height=3.8*inch)
#             story.append(img)
#             story.append(Spacer(1, 0.2*inch))
#         except Exception as e:
#             story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
    
#     # Monthly breakdown
#     if 'month' in tasks_df.columns:
#         story.append(PageBreak())
#         story.append(Paragraph("Monthly Task Distribution", heading_style))
#         month_data = tasks_df.groupby('month').size().reset_index(name='count')
#         month_table_data = [['Month', 'Task Count']]
#         for _, row in month_data.iterrows():
#             month_table_data.append([row['month'], str(row['count'])])
        
#         month_table = Table(month_table_data, colWidths=[3*inch, 2*inch])
#         month_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, 0), 12),
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#             ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
#             ('GRID', (0, 0), (-1, -1), 1, colors.grey),
#             ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#             ('FONTSIZE', (0, 1), (-1, -1), 10),
#             ('TOPPADDING', (0, 1), (-1, -1), 8),
#             ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
#         ]))
#         story.append(month_table)
#         story.append(Spacer(1, 0.2*inch))
        
#         # Add Monthly Bar Chart
#         try:
#             fig = px.bar(month_data, x='month', y='count',
#                         color_discrete_sequence=['#2563eb'],
#                         title='Tasks by Month')
#             fig.update_layout(
#                 xaxis_title="Month",
#                 yaxis_title="Tasks",
#                 font=dict(family="Inter, sans-serif", size=12)
#             )
#             img_path = save_plotly_as_image(fig, width=700, height=400)
#             temp_files.append(img_path)
#             img = Image(img_path, width=6*inch, height=3.4*inch)
#             story.append(img)
#             story.append(Spacer(1, 0.2*inch))
#         except Exception as e:
#             story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
        
#         # Add Quarterly Chart
#         if 'quarter' in tasks_df.columns:
#             quarter_data = tasks_df.groupby('quarter').size().reset_index(name='count')
#             try:
#                 fig = px.bar(quarter_data, x='quarter', y='count',
#                             color_discrete_sequence=['#8b5cf6'],
#                             title='Tasks by Quarter')
#                 fig.update_layout(
#                     xaxis_title="Quarter",
#                     yaxis_title="Tasks",
#                     font=dict(family="Inter, sans-serif", size=12)
#                 )
#                 img_path = save_plotly_as_image(fig, width=700, height=400)
#                 temp_files.append(img_path)
#                 img = Image(img_path, width=6*inch, height=3.4*inch)
#                 story.append(img)
#                 story.append(Spacer(1, 0.2*inch))
#             except Exception as e:
#                 story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
    
#     # Team member distribution (for admin)
#     if role == 'admin' and 'assigned_name' in tasks_df.columns:
#         story.append(Spacer(1, 0.3*inch))
#         story.append(Paragraph("Tasks by Team Member", heading_style))
#         user_data = tasks_df.groupby('assigned_name').size().reset_index(name='count')
#         user_table_data = [['Team Member', 'Task Count']]
#         for _, row in user_data.iterrows():
#             user_table_data.append([row['assigned_name'], str(row['count'])])
        
#         user_table = Table(user_table_data, colWidths=[3*inch, 2*inch])
#         user_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, 0), 12),
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#             ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
#             ('GRID', (0, 0), (-1, -1), 1, colors.grey),
#             ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#             ('FONTSIZE', (0, 1), (-1, -1), 10),
#             ('TOPPADDING', (0, 1), (-1, -1), 8),
#             ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
#         ]))
#         story.append(user_table)
#         story.append(Spacer(1, 0.2*inch))
        
#         # Add Team Member Bar Chart
#         try:
#             fig = px.bar(user_data, x='assigned_name', y='count',
#                         color_discrete_sequence=['#8b5cf6'],
#                         title='Tasks by Team Member')
#             fig.update_layout(
#                 xaxis_title="Team Member",
#                 yaxis_title="Tasks",
#                 font=dict(family="Inter, sans-serif", size=12)
#             )
#             img_path = save_plotly_as_image(fig, width=700, height=400)
#             temp_files.append(img_path)
#             img = Image(img_path, width=6*inch, height=3.4*inch)
#             story.append(img)
#         except Exception as e:
#             story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
    
#     # Build PDF
#     doc.build(story)
    
#     # Clean up temporary files
#     for temp_file in temp_files:
#         try:
#             os.unlink(temp_file)
#         except:
#             pass
    
#     buffer.seek(0)
#     return buffer

# def show_analytics_dashboard(role):
#     st.title("Analytics Dashboard")
    
#     if role == 'admin':
#         tasks_df = get_tasks(role='admin')
#     else:
#         tasks_df = get_tasks(st.session_state.user_id, role='user')
    
#     if tasks_df.empty:
#         st.info("No tasks available for analysis")
#         return
    
#     tasks_df['due_date'] = pd.to_datetime(tasks_df['due_date'])
#     tasks_df['month'] = tasks_df['due_date'].dt.to_period('M').astype(str)
#     tasks_df['quarter'] = tasks_df['due_date'].dt.to_period('Q').astype(str)
    
#     # Download PDF Button at the top
#     st.markdown("<br>", unsafe_allow_html=True)
#     col_pdf, col_spacer = st.columns([1, 3])
#     with col_pdf:
#         pdf_buffer = generate_pdf_report(tasks_df, role)
#         st.download_button(
#             label="📥 Download Analytical Report",
#             data=pdf_buffer,
#             file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
#             mime="application/pdf",
#             use_container_width=True
#         )
    
#     st.markdown("<br>", unsafe_allow_html=True)
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         create_metric_card(len(tasks_df), "Total Tasks", "#2563eb")
#     with col2:
#         create_metric_card(len(tasks_df[tasks_df['status'] == 'Pending']), "Pending", "#f59e0b")
#     with col3:
#         create_metric_card(len(tasks_df[tasks_df['status'] == 'Completed']), "Completed", "#10b981")
#     with col4:
#         create_metric_card(int(tasks_df['comment_count'].sum()), "Comments", "#8b5cf6")
    
#     st.markdown("<br>", unsafe_allow_html=True)
    
#     col1, col2 = st.columns(2)
#     with col1:
#         if 'domain' in tasks_df.columns:
#             st.subheader(" Tasks by Domain ")
#             domain_status = tasks_df.groupby(['domain', 'status']).size().unstack(fill_value=0)
            
#             fig = go.Figure()
            
#             if 'Pending' in domain_status.columns:
#                 fig.add_trace(go.Bar(
#                     name='Pending',
#                     x=domain_status.index,
#                     y=domain_status['Pending'],
#                     marker_color='#f59e0b',
#                     text=domain_status['Pending'],
#                     textposition='inside'
#                 ))
            
#             if 'Completed' in domain_status.columns:
#                 fig.add_trace(go.Bar(
#                     name='Completed',
#                     x=domain_status.index,
#                     y=domain_status['Completed'],
#                     marker_color='#10b981',
#                     text=domain_status['Completed'],
#                     textposition='inside'
#                 ))
            
#             fig.update_layout(
#                 barmode='stack',
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 xaxis_title="Domain",
#                 yaxis_title="Number of Tasks",
#                 font=dict(family="Inter, sans-serif"),
#                 legend=dict(
#                     orientation="h",
#                     yanchor="bottom",
#                     y=1.02,
#                     xanchor="right",
#                     x=1
#                 ),
#                 xaxis={'categoryorder': 'total descending'}
#             )
            
#             st.plotly_chart(fig, use_container_width=True)
#             st.markdown("<br>", unsafe_allow_html=True)
#     with col2:
#         if role == 'admin':
#             st.subheader("Tasks by Team Member")
#             user_data = tasks_df.groupby('assigned_name').size().reset_index(name='count')
#             fig = px.bar(user_data, x='assigned_name', y='count',
#                         color_discrete_sequence=['#8b5cf6'])
#             fig.update_layout(
#                 plot_bgcolor='white',
#                 paper_bgcolor='white',
#                 xaxis_title="Team Member",
#                 yaxis_title="Tasks",
#                 font=dict(family="Inter, sans-serif")
#             )
#             st.plotly_chart(fig, use_container_width=True)



#     # Monthly and Quarterly Charts
#     col1, col2 = st.columns(2)

    
#     with col1:
#         st.subheader("Tasks by Month")
#         month_data = tasks_df.groupby('month').size().reset_index(name='count')
#         fig = px.bar(month_data, x='month', y='count',
#                     color_discrete_sequence=['#2563eb'])
#         fig.update_layout(
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             xaxis_title="Month",
#             yaxis_title="Tasks",
#             font=dict(family="Inter, sans-serif")
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         st.subheader("Tasks by Quarter")
#         quarter_data = tasks_df.groupby('quarter').size().reset_index(name='count')
#         fig = px.bar(quarter_data, x='quarter', y='count',
#                     color_discrete_sequence=['#8b5cf6'])
#         fig.update_layout(
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             xaxis_title="Quarter",
#             yaxis_title="Tasks",
#             font=dict(family="Inter, sans-serif")
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Status and Comments Charts
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Status Distribution")
#         status_data = tasks_df['status'].value_counts().reset_index()
#         status_data.columns = ['status', 'count']
#         fig = px.pie(status_data, values='count', names='status',
#                     color_discrete_sequence=['#f59e0b', '#10b981'])
#         fig.update_layout(
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             font=dict(family="Inter, sans-serif")
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         st.subheader("Tasks by Comments")
#         comment_data = tasks_df.groupby('comment_count').size().reset_index(name='task_count')
#         fig = px.bar(comment_data, x='comment_count', y='task_count',
#                     color_discrete_sequence=['#06b6d4'])
#         fig.update_layout(
#             plot_bgcolor='white',
#             paper_bgcolor='white',
#             xaxis_title="Comments",
#             yaxis_title="Tasks",
#             font=dict(family="Inter, sans-serif")
#         )
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Team Member Chart (Admin only)
    

# # def show_comments_page():
# #     st.title("All Comments")
    
# #     conn = get_db_connection()
# #     query = '''SELECT c.*, u.name, u.email, t.title as task_title
# #                FROM comments c
# #                JOIN users u ON c.user_id = u.user_id
# #                JOIN tasks t ON c.task_id = t.task_id
# #                ORDER BY c.created_at DESC'''
# #     comments_df = pd.read_sql_query(query, conn)
# #     conn.close()
    
# #     if not comments_df.empty:
# #         for _, comment in comments_df.iterrows():
# #             st.markdown(f"""
# #             <div style='
# #                 background-color: #ffffff;
# #                 padding: 1.25rem;
# #                 border-radius: 6px;
# #                 margin: 0.75rem 0;
# #                 border: 1px solid #e2e8f0;
# #                 border-left: 3px solid #2563eb;
# #             '>
# #                 <div style='margin-bottom: 0.75rem;'>
# #                     <span style='background-color: #dbeafe; color: #1e40af; padding: 0.25rem 0.625rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;'>{comment['task_title']}</span>
# #                 </div>
# #                 <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;'>
# #                     <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
# #                     <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
# #                 </div>
# #                 <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
# #             </div>
# #             """, unsafe_allow_html=True)
# #     else:
# #         st.info("No comments yet")


# def show_comments_page():
#     st.title("All Comments")
    
#     db = get_db_connection()
#     if db is None:
#         st.error("Database connection failed")
#         return
    
#     # Get all comments with user and task info
#     comments = list(db['comments'].find().sort('created_at', -1))
    
#     # Enrich comments with user and task information
#     enriched_comments = []
#     for comment in comments:
#         # Get user info
#         user = db['users'].find_one({'_id': ObjectId(comment['user_id'])})
#         # Get task info
#         task = db['tasks'].find_one({'_id': ObjectId(comment['task_id'])})
        
#         if user and task:
#             enriched_comments.append({
#                 'comment_id': str(comment['_id']),
#                 'comment_text': comment['comment_text'],
#                 'created_at': comment['created_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(comment['created_at'], datetime) else str(comment['created_at']),
#                 'name': user['name'],
#                 'email': user['email'],
#                 'task_title': task['title']
#             })
    
#     if enriched_comments:
#         for comment in enriched_comments:
#             st.markdown(f"""
#             <div style='
#                 background-color: #ffffff;
#                 padding: 1.25rem;
#                 border-radius: 6px;
#                 margin: 0.75rem 0;
#                 border: 1px solid #e2e8f0;
#                 border-left: 3px solid #2563eb;
#             '>
#                 <div style='margin-bottom: 0.75rem;'>
#                     <span style='background-color: #dbeafe; color: #1e40af; padding: 0.25rem 0.625rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;'>{comment['task_title']}</span>
#                 </div>
#                 <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;'>
#                     <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
#                     <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
#                 </div>
#                 <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
#             </div>
#             """, unsafe_allow_html=True)
#     else:
#         st.info("No comments yet")
# def show_email_page():
#     st.title("Email Center")
      
#     sender_email=st.secrets.get("SENDER_EMAIL")
#     sender_password=st.secrets.get("SENDER_PASSWORD")
#     st.markdown("<br>", unsafe_allow_html=True)
    
#     email_mode = st.radio("Select Mode", ["Send to All Users", "Send to Individual"], horizontal=True)
    
#     st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
#     tasks_df = get_tasks(role='admin')
#     pending_tasks = tasks_df[tasks_df['status'] == 'Pending']
    
#     if pending_tasks.empty:
#         st.success("No pending tasks")
#         return
    
#     users_with_pending = pending_tasks.groupby(['assigned_email', 'assigned_name']).size().reset_index(name='count')
    
#     if email_mode == "Send to All Users":
#         st.subheader("Pending Tasks Summary")
#         st.dataframe(users_with_pending, use_container_width=True)
        
#         if st.button("Send Emails to All", type="primary", use_container_width=True):
#             if not sender_email or not sender_password:
#                 st.error("Please provide email credentials")
#                 return
            
#             progress_bar = st.progress(0)
#             status_text = st.empty()
            
#             total = len(users_with_pending)
#             success = 0
            
#             for idx, (_, user) in enumerate(users_with_pending.iterrows()):
#                 status_text.text(f"Sending to {user['assigned_name']}...")
                
#                 user_tasks = pending_tasks[pending_tasks['assigned_email'] == user['assigned_email']]
                
#                 if send_email_summary(user['assigned_email'], user['assigned_name'], 
#                                     user_tasks, sender_email, sender_password):
#                     success += 1
                
#                 progress_bar.progress((idx + 1) / total)
            
#             status_text.empty()
#             progress_bar.empty()
            
#             st.success(f"Sent {success}/{total} emails successfully")
    
#     else:
#         st.subheader("Send to Individual User")
        
#         user_options = {f"{row['assigned_name']} ({row['assigned_email']}) - {row['count']} pending": 
#                        row['assigned_email'] for _, row in users_with_pending.iterrows()}
        
#         selected = st.selectbox("Select User", list(user_options.keys()))
#         selected_email = user_options[selected]
        
#         user_tasks = pending_tasks[pending_tasks['assigned_email'] == selected_email]
#         user_name = users_with_pending[users_with_pending['assigned_email'] == selected_email]['assigned_name'].iloc[0]
        
#         st.markdown(f"**User:** {user_name}")
#         st.markdown(f"**Email:** {selected_email}")
#         st.markdown(f"**Pending Tasks:** {len(user_tasks)}")
        
#         st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
#         st.dataframe(user_tasks[['task_id', 'title', 'domain', 'due_date']], use_container_width=True)
        
#         if st.button(f"Send Email to {user_name}", type="primary", use_container_width=True):
#             if not sender_email or not sender_password:
#                 st.error("Please provide email credentials")
#                 return
            
#             with st.spinner(f"Sending to {user_name}..."):
#                 if send_email_summary(selected_email, user_name, user_tasks, sender_email, sender_password):
#                     st.success(f"Email sent to {user_name}")
#                 else:
#                     st.error(f"Failed to send email")

# def show_user_management():
#     st.title("Team Management")
    
#     tab1, tab2 = st.tabs(["Add User", "View Users"])
    
#     with tab1:
#         st.subheader("Add New User")
#         with st.form("add_user_form"):
#             name = st.text_input("Full Name", placeholder="John Doe")
#             email = st.text_input("Email", placeholder="john.doe@company.com")
#             role = st.selectbox("Role", ["user", "admin"])
            
#             submit = st.form_submit_button("Add User", use_container_width=True)
            
#             if submit:
#                 if name and email:
#                     if add_user(name, email, role):
#                         st.success("User added successfully")
#                         st.rerun()
#                     else:
#                         st.error("User with this email already exists")
#                 else:
#                     st.error("Please fill in all fields")
    
#     with tab2:
#         st.subheader("All Users")
#         users_df = get_all_users()
        
#         for _, user in users_df.iterrows():
#             role_color = "#2563eb" if user['role'] == "admin" else "#10b981"
#             st.markdown(f"""
#             <div style='
#                 background-color: #ffffff;
#                 padding: 1.25rem;
#                 border-radius: 6px;
#                 margin: 0.75rem 0;
#                 border: 1px solid #e2e8f0;
#                 display: flex;
#                 justify-content: space-between;
#                 align-items: center;
#             '>
#                 <div>
#                     <h4 style='margin: 0 0 0.25rem 0; color: #0f172a; font-size: 1rem;'>{user['name']}</h4>
#                     <p style='margin: 0; color: #64748b; font-size: 0.875rem;'>{user['email']}</p>
#                 </div>
#                 <span style='background-color: {role_color}; color: white; padding: 0.375rem 0.875rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;'>
#                     {user['role'].upper()}
#                 </span>
#             </div>
#             """, unsafe_allow_html=True)

# def show_user_dashboard():
#     with st.sidebar:
#         st.markdown(f"""
#         <div style='
#             background-color: #f8fafc;
#             padding: 1.5rem;
#             border-radius: 8px;
#             border-left: 3px solid #2563eb;
#             text-align: center;
#             margin-bottom: 1.5rem;
#         '>
#             <div style='width: 64px; height: 64px; background-color: #10b981; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem; color: white; font-size: 1.5rem; font-weight: 700;'>
#                 {st.session_state.user_name[0]}
#             </div>
#             <h3 style='color: #0f172a; margin: 0 0 0.25rem 0; font-size: 1.125rem;'>{st.session_state.user_name}</h3>
#             <p style='color: #64748b; margin: 0; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Team Member</p>
#         </div>
#         """, unsafe_allow_html=True)
        
#         st.markdown("<div style='color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;'>Navigation</div>", unsafe_allow_html=True)
        
#         menu = st.radio("", 
#                        ["My Tasks", "Analytics"],
#                        label_visibility="collapsed")
        
#         st.markdown("<hr style='border-color: #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
#         if st.button("Logout", use_container_width=True):
#             for key in list(st.session_state.keys()):
#                 del st.session_state[key]
#             st.rerun()
    
#     if menu == "My Tasks":
#         show_my_tasks()
#     elif menu == "Analytics":
#         show_analytics_dashboard('user')

# def show_my_tasks():
#     st.title("My Tasks")
    
#     tasks_df = get_tasks(st.session_state.user_id, 'user')
    
#     if tasks_df.empty:
#         st.info("No tasks assigned to you")
#         return
    
#     tasks_df['month'] = pd.to_datetime(tasks_df['due_date']).dt.to_period('M').astype(str)
#     tasks_df['quarter'] = pd.to_datetime(tasks_df['due_date']).dt.to_period('Q').astype(str)
    
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         create_metric_card(len(tasks_df), "Total", "#2563eb")
#     with col2:
#         create_metric_card(len(tasks_df[tasks_df['status'] == 'Pending']), "Pending", "#f59e0b")
#     with col3:
#         create_metric_card(len(tasks_df[tasks_df['status'] == 'Completed']), "Completed", "#10b981")
    
#     st.markdown("<br><br>", unsafe_allow_html=True)
    
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])
#     with col2:
#         months = ["All"] + sorted(tasks_df['month'].unique().tolist())
#         month_filter = st.selectbox("Filter by Month", months)
#     with col3:
#         quarters = ["All"] + sorted(tasks_df['quarter'].unique().tolist())
#         quarter_filter = st.selectbox("Filter by Quarter", quarters)
    
#     filtered_df = tasks_df.copy()
    
#     if status_filter != "All":
#         filtered_df = filtered_df[filtered_df['status'] == status_filter]
#     if month_filter != "All":
#         filtered_df = filtered_df[filtered_df['month'] == month_filter]
#     if quarter_filter != "All":
#         filtered_df = filtered_df[filtered_df['quarter'] == quarter_filter]
    
#     st.subheader(f"Your Tasks ({len(filtered_df)})")
    
#     if not tasks_df.empty:
#             st.info("Click status dropdown to update task status directly")
            
#             for idx, row in tasks_df.iterrows():
#                 with st.expander(f"{row['title']} -  ({row['due_date']} {row['status']})", expanded=False):
#                     # Display task info using Streamlit components instead of HTML
#                     st.markdown(f"**Description:** {row['description']}")
                    
#                     col1, col2, col3 = st.columns(3)
#                     with col1:
#                         st.markdown(f"**Domain:** {row['domain']}")
#                     with col2:
#                         st.markdown(f"**Due Date:** {row['due_date']}")
#                     with col3:
#                         st.markdown(f"**Frequency:** {row['frequency']}")
                    
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.markdown(f"**Status:** {row['status']}")
#                     with col2:
#                         st.markdown(f"**Comments:** {row['comment_count']}")
                    
#                     if row['attachment'] and str(row['attachment']).strip() and str(row['attachment']) != 'nan':
#                         st.markdown(f"**Attachment:** [View Attachment]({row['attachment']})")
                    
#                     st.markdown("---")
#                     st.markdown("#### Quick Status Update")
#                     col1, col2 = st.columns([3, 1])
#                     with col1:
#                         new_status = st.selectbox(
#                             "Update Status",
#                             ["Pending", "Completed"],
#                             index=0 if row['status'] == "Pending" else 1,
#                             key=f"admin_status_{row['task_id']}"
#                         )
#                     with col2:
#                         if st.button("Update Status", key=f"update_btn_{row['task_id']}"):
#                             if new_status != row['status']:
#                                 update_task_status(row['task_id'], new_status)
#                                 st.success("Status updated")
#                                 st.rerun()
                    
#                     st.markdown("---")
                    
#                     # Comments section
#                     st.markdown(f"#### Comments ({row['comment_count']})")
#                     comments_df = get_comments(row['task_id'])
                    
#                     if not comments_df.empty:
#                         for _, comment in comments_df.iterrows():
#                             st.markdown(f"""
#                             <div style='
#                                 background-color: #f8fafc;
#                                 padding: 1rem;
#                                 border-radius: 6px;
#                                 margin: 0.75rem 0;
#                                 border-left: 3px solid #2563eb;
#                             '>
#                                 <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
#                                     <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
#                                     <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
#                                 </div>
#                                 <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
#                             </div>
#                             """, unsafe_allow_html=True)
#                     else:
#                         st.info("No comments yet")
                    
#                     new_comment = st.text_area("Add a comment", key=f"edit_comment_{row['task_id']}", height=80, placeholder="Write your comment here...")
                    
#                     if st.button("Post Comment", key=f"edit_post_{row['task_id']}", use_container_width=True):
#                         if new_comment.strip():
#                             add_comment(row['task_id'], st.session_state.user_id, new_comment)
#                             st.success("Comment posted")
#                             st.rerun()
#                         else:
#                             st.warning("Please enter a comment")
# def download_excel_template():
#     template_data = {
#         'Domain': ['SAP', 'Network', 'EC'],
#         'Title': ['Sample Task 1', 'Sample Task 2', 'Sample Task 3'],
#         'Description': ['Description 1', 'Description 2', 'Description 3'],
#         'Email': ['aliyashal309@gmail.com', 'farooquiyashal@gmail.com', 'yashalalifarooqui30@gmail.com'],
#         'Attachment Link': ['https://example.com/file1', '', 'https://example.com/file3'],
#         'Status': ['Pending', 'Completed', 'Pending'],
#         'Due_Date': ['15-10-2025', '20-10-2025', '25-10-2025'],
#         'Frequency': ['Monthly', 'Quarterly', 'Monthly']
#     }
    
#     df = pd.DataFrame(template_data)
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name='Tasks')
    
#     return output.getvalue()

# def main():
#     st.set_page_config(
#         page_title="TaskFlow Pro",
#         page_icon="📊",
#         layout="wide",
#         initial_sidebar_state="expanded"
#     )
    
#     set_page_styling()
#     init_database()
    
#     if 'logged_in' not in st.session_state:
#         st.session_state.logged_in = False
    
#     if not st.session_state.logged_in:
#         show_login()
#     else:
#         if st.session_state.user_role == 'admin':
#             show_admin_dashboard()
#         else:
#             show_user_dashboard()

# if __name__ == "__main__":
#     main()



import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import smtplib
import io
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import tempfile

# Import database functions
from database import *

# sender_email = st.secrets.get("SENDER_EMAIL")
# sender_password = st.secrets.get("SENDER_PASSWORD")

os.environ['PATH'] += os.pathsep + ':/usr/bin'

sender_email= os.environ.get("SMTP_USERNAME")
sender_password = os.environ.get("SMTP_PASSWORD") 

def update_task_status_with_notification(task_id, new_status, old_status, user_name):
    """Update task status and send notification if completed"""
    update_task_status(task_id, new_status)
    
    # Send notification if status changed to "Completed"
    if new_status == "Completed" and old_status != "Completed":
        task = get_task_by_id(task_id)
        st.write(sender_email, sender_password)
        if task:           
            if sender_email and sender_password:
                with st.spinner("Sending completion notification..."):
                    if send_task_completion_notification(task, user_name, sender_email, sender_password):

                        st.success("Status updated and admins notified!")
                        st.write(f"Task '{task['title']}' marked as Completed")
                        st.write(sender_email, sender_password)
                    else:
                        st.error("Status updated, but failed to send notifications to admins")
            else:
                st.error("Status updated! (Email credentials not configured)")
        else:
            st.success("Status updated!")
    else:
        st.success("Status updated!")

def set_page_styling():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
    }
    
    .main .block-container {
        background-color: #ffffff;
        padding: 2.5rem;
        max-width: 1400px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    h1 {
        color: #0f172a;
        font-weight: 700;
        font-size: 2rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
        border-bottom: 2px solid #2563eb;
        padding-bottom: 0.75rem;
    }
    
    h2 {
        color: #1e293b;
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #334155;
        font-weight: 600;
        font-size: 1.125rem;
    }
    
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.625rem 1.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        letter-spacing: 0.015em;
    }
    
    .stButton>button:hover {
        background-color: #1e40af;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .stButton>button:active {
        background-color: #1e3a8a;
    }
    
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div,
    .stDateInput>div>div>input {
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 0.625rem 0.875rem;
        font-size: 14px;
        transition: all 0.2s ease;
        background-color: #ffffff;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>div:focus,
    .stDateInput>div>div>input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background-color: transparent;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        padding: 0.75rem 1.25rem;
        font-weight: 600;
        color: #64748b;
        border-bottom: 2px solid transparent;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #334155;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #2563eb;
        border-bottom: 2px solid #2563eb;
    }
    
    .stExpander {
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        overflow: hidden;
        margin-bottom: 0.75rem;
        background-color: #ffffff;
    }
    
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        font-weight: 600;
        padding: 1rem 1.25rem;
        transition: background-color 0.2s ease;
        color: #334155;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #f1f5f9;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.875rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stAlert {
        border-radius: 6px;
        padding: 1rem 1.25rem;
        border-left-width: 3px;
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        color: #334155;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-left: 0.75rem;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label {
        color: #475569;
        padding: 0.625rem 1rem;
        border-radius: 6px;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    [data-testid="stSidebar"] .stRadio input:checked + div {
        background-color: #eff6ff;
        border-left: 3px solid #2563eb;
    }
    
    [data-testid="stSidebar"] .stRadio input:checked + div > label {
        color: #2563eb;
        font-weight: 600;
    }
    
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        overflow: hidden;
    }
    
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
    
    .stProgress > div > div > div > div {
        background-color: #2563eb;
    }
    
    </style>
    """, unsafe_allow_html=True)

def create_metric_card(value, label, border_color="#2563eb"):
    st.markdown(f"""
    <div style="
        margin: 0.75rem;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 3px solid {border_color};
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    ">
        <div style="font-size: 2rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem;">{value}</div>
        <div style="font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def create_task_card(task, show_actions=True):
    """Create a professional task card with due date status"""
    import streamlit as st
    import pandas as pd
    from datetime import date, datetime
    
    # Get task status
    task_status = task.get('status', 'Open')
    
    # Calculate due date status with proper type handling
    if pd.notna(task['due_date']):
        # Convert due_date to date object if it's a Timestamp
        if isinstance(task['due_date'], pd.Timestamp):
            due_date = task['due_date'].date()
        elif isinstance(task['due_date'], datetime):
            due_date = task['due_date'].date()
        else:
            due_date = task['due_date']
        
        today = date.today()
        
        # Ensure both are date objects for comparison
        if isinstance(due_date, date):
            days_remaining = (due_date - today).days
        else:
            # If due_date is still not a date object, try to convert it
            try:
                due_date = pd.to_datetime(due_date).date()
                days_remaining = (due_date - today).days
            except:
                days_remaining = 0  # Fallback if conversion fails
        
        # If task is completed, show completed status regardless of due date
        if task_status == 'Completed':
            status_color = "#10b981"
            status_bg = "#f0fdf4"
            status_icon = "✅"
            status_text = "Completed"
            priority_level = "low"
        elif days_remaining < 0:
            # Overdue
            status_color = "#dc2626"
            status_bg = "#fef2f2"
            status_icon = "⏰"
            status_text = f"Overdue by {abs(days_remaining)} days"
            priority_level = "high"
        elif days_remaining <= 3:
            # Due very soon
            status_color = "#f59e0b"
            status_bg = "#fffbeb"
            status_icon = "⚠️"
            status_text = f"Due in {days_remaining} days"
            priority_level = "high"
        elif days_remaining <= 7:
            # Due soon
            status_color = "#f59e0b"
            status_bg = "#fffbeb"
            status_icon = "📅"
            status_text = f"Due in {days_remaining} days"
            priority_level = "medium"
        else:
            # On track
            status_color = "#10b981"
            status_bg = "#f0fdf4"
            status_icon = "✅"
            status_text = f"Due in {days_remaining} days"
            priority_level = "low"
    else:
        # No due date
        if task_status == 'Completed':
            status_color = "#10b981"
            status_bg = "#f0fdf4"
            status_icon = "✅"
            status_text = "Completed"
        else:
            status_color = "#6b7280"
            status_bg = "#f3f4f6"
            status_icon = "📅"
            status_text = "No due date"
        priority_level = "low"
        days_remaining = None
    
    # Status badge colors
    status_badge_colors = {
        'Open': {'bg': '#fef3c7', 'text': '#92400e', 'icon': '🟡'},
        'In Progress': {'bg': '#dbeafe', 'text': '#1e40af', 'icon': '🔵'},
        'Completed': {'bg': '#d1fae5', 'text': '#065f46', 'icon': '✅'},
        'Pending': {'bg': '#fef3c7', 'text': '#92400e', 'icon': '🟡'}
    }
    
    # Priority badge colors
    priority_badge_colors = {
        'High': {'bg': '#fef2f2', 'text': '#dc2626', 'icon': '🔴'},
        'Medium': {'bg': '#fffbeb', 'text': '#f59e0b', 'icon': '🟡'},
        'Low': {'bg': '#f0fdf4', 'text': '#10b981', 'icon': '🟢'}
    }
    
    status_style = status_badge_colors.get(task_status, {'bg': '#f3f4f6', 'text': '#374151', 'icon': '⚪'})
    priority_style = priority_badge_colors.get(task.get('priority', 'Medium'), {'bg': '#f3f4f6', 'text': '#374151', 'icon': '⚪'})
    
    # Escape HTML in user content to prevent injection
    title = str(task.get('title', 'Untitled Task')).replace('<', '&lt;').replace('>', '&gt;')
    description = str(task.get('description', 'No description')).replace('<', '&lt;').replace('>', '&gt;')
    domain = str(task.get('domain', 'No domain')).replace('<', '&lt;').replace('>', '&gt;')
    frequency = str(task.get('frequency', 'One-time')).replace('<', '&lt;').replace('>', '&gt;')
    
    attachment_html = ""
    if task.get('attachment') and str(task['attachment']).strip() and str(task['attachment']) != 'nan' and task['attachment'] != 'Link':
        attachment_url = str(task["attachment"]).replace('"', '&quot;')
        attachment_html = f'''
        <div style="margin-top: 0.5rem;">
            <a href="{attachment_url}" target="_blank" style="color: #2563eb; text-decoration: none; font-size: 0.8125rem; font-weight: 500; display: inline-flex; align-items: center; gap: 0.25rem;">
                📎 View Attachment
            </a>
        </div>
        '''
    
    actions_html = ""
    if show_actions:
        actions_html = '''
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e2e8f0;">
            <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
                <button style="background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.75rem; font-weight: 500; cursor: pointer;">
                    Quick Update
                </button>
            </div>
        </div>
        '''
    
    # Format due date for display
    due_date_display = "No due date"
    if pd.notna(task['due_date']):
        try:
            if isinstance(task['due_date'], (pd.Timestamp, datetime)):
                due_date_display = task['due_date'].strftime("%b %d, %Y")
            else:
                due_date_display = str(task['due_date'])
        except:
            due_date_display = "Invalid date"
    
    html_content = f"""
    <div style='
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-left: 4px solid {status_color};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    '>
        <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;'>
            <div style='flex: 1;'>
                <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;'>
                    <h3 style='margin: 0; color: #1a202c; font-size: 1.125rem; font-weight: 600;'>{title}</h3>
                    <span style='background-color: {status_style["bg"]}; color: {status_style["text"]}; padding: 0.25rem 0.5rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; display: inline-flex; align-items: center; gap: 0.25rem;'>
                        {status_style["icon"]} {task_status}
                    </span>
                    <span style='background-color: {priority_style["bg"]}; color: {priority_style["text"]}; padding: 0.25rem 0.5rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; display: inline-flex; align-items: center; gap: 0.25rem;'>
                        {priority_style["icon"]} {task.get('priority', 'Medium')}
                    </span>
                </div>
                <p style='color: #64748b; margin: 0 0 0.75rem 0; font-size: 0.875rem; line-height: 1.5;'>{description}</p>
                {attachment_html}
            </div>
            <div style='display: flex; align-items: center; gap: 0.75rem; margin-left: 1rem;'>
                <span style='background-color: #dbeafe; color: #1e40af; padding: 0.5rem 0.75rem; border-radius: 8px; font-size: 0.875rem; font-weight: 700; min-width: 2rem; text-align: center; display: inline-flex; align-items: center; gap: 0.25rem;'>
                    💬 {task.get('comment_count', 0)}
                </span>
            </div>
        </div>
        
        <div style='display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.8125rem; margin-bottom: 0.75rem;'>
            <span style='background-color: #f1f5f9; color: #334155; padding: 0.375rem 0.75rem; border-radius: 6px; font-weight: 500; display: inline-flex; align-items: center; gap: 0.25rem;'>
                🏷️ {domain}
            </span>
            <span style='background-color: #f1f5f9; color: #334155; padding: 0.375rem 0.75rem; border-radius: 6px; font-weight: 500; display: inline-flex; align-items: center; gap: 0.25rem;'>
                📅 {due_date_display}
            </span>
            <span style='background-color: #f1f5f9; color: #334155; padding: 0.375rem 0.75rem; border-radius: 6px; font-weight: 500; display: inline-flex; align-items: center; gap: 0.25rem;'>
                🔄 {frequency}
            </span>
        </div>
        
        <div style='background-color: {status_bg}; color: {status_color}; padding: 0.75rem; border-radius: 8px; font-size: 0.8125rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;'>
            {status_icon} {status_text}
        </div>
        {actions_html}
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)
def show_login():
    st.markdown("""
    <div style='text-align: center; padding: 3rem 1rem 2rem;'>
        <h1 style='color: #0f172a; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 800; border: none;'>TaskFlow Pro</h1>
        <p style='color: #64748b; font-size: 1.125rem; font-weight: 500;'>Task Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #0f172a; margin-bottom: 0.5rem; border: none;'>Sign In</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem; font-size: 0.875rem;'>Enter your email to access your account</p>", unsafe_allow_html=True)
        
        email = st.text_input("Email Address", placeholder="your.email@company.com", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign In", use_container_width=True):
            user = get_user_by_email(email)
            if user:
                # FIXED: Use SQL Server user_id instead of MongoDB _id
                st.session_state.user_id = user['user_id']
                st.session_state.user_name = user['name']
                st.session_state.user_email = user['email']
                st.session_state.user_role = user['role']
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("User not found. Please check your email address.")
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_comment_modal(task_id, task_title):
    st.markdown(f"<h3 style='color: #0f172a; margin-bottom: 1.5rem; border: none;'>Discussion: {task_title}</h3>", unsafe_allow_html=True)
    
    comments_df = get_comments(task_id)
    
    if not comments_df.empty:
        for _, comment in comments_df.iterrows():
            st.markdown(f"""
            <div style='
                background-color: #f8fafc;
                padding: 1rem;
                border-radius: 6px;
                margin: 0.75rem 0;
                border-left: 3px solid #2563eb;
            '>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                    <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
                    <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
                </div>
                <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No comments yet. Be the first to comment.")
    
    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    st.subheader("Add Comment")
    new_comment = st.text_area("Your comment", key=f"comment_{task_id}", height=100, label_visibility="collapsed", placeholder="Write your comment here...")
    
    if st.button("Post Comment", key=f"submit_{task_id}", use_container_width=True):
        if new_comment.strip():
            add_comment(task_id, st.session_state.user_id, new_comment)
            st.success("Comment posted successfully")
            st.rerun()
        else:
            st.warning("Please enter a comment before posting")

def show_admin_dashboard():
    with st.sidebar:
        st.markdown(f"""
        <div style='
            background-color: #f8fafc;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            text-align: center;
            margin-bottom: 1.5rem;
        '>
            <div style='width: 64px; height: 64px; background-color: #2563eb; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem; color: white; font-size: 1.5rem; font-weight: 700;'>
                {st.session_state.user_name[0]}
            </div>
            <h3 style='color: #0f172a; margin: 0 0 0.25rem 0; font-size: 1.125rem;'>{st.session_state.user_name}</h3>
            <p style='color: #64748b; margin: 0; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Administrator</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;'>Navigation</div>", unsafe_allow_html=True)
        
        menu = st.radio("", 
                       ["Task Management", "Analytics", "Comments", "Email Center", "Team"],
                       label_visibility="collapsed")
        
        st.markdown("<hr style='border-color: #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    if menu == "Task Management":
        show_task_management()
    elif menu == "Analytics":
        show_analytics_dashboard('admin')
    elif menu == "Comments":
        show_comments_page()
    elif menu == "Email Center":
        show_email_page()
    elif menu == "Team":
        show_user_management()

def show_task_management():
    st.title("Task Management")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Create Task", "View & Edit", "Delete Task", "Bulk Upload", "All Tasks"])
    
    with tab1:
        st.subheader("Create New Task")
        with st.form("create_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Task Title", placeholder="Enter task title...")
                description = st.text_area("Description", placeholder="Describe the task...", height=100)
                domain = st.selectbox("Domain", ["SAP", "Network", "EC", "SalesFlo", "NFlo", "Help Desk", "IT-Governance"])
            
            with col2:
                users_df = get_all_users()
                user_options = {f"{row['name']} ({row['email']})": row['user_id'] 
                              for _, row in users_df.iterrows()}
                assigned = st.selectbox("Assign To", list(user_options.keys()))
                
                attachment = st.text_input("Attachment Link", placeholder="https://...")
                status = st.selectbox("Status", ["Pending", "Completed"])
                due_date = st.date_input("Due Date")
                frequency = st.selectbox("Frequency", ["Monthly", "Quarterly", "Yearly", "One-time"])
            
            submit = st.form_submit_button("Create Task", use_container_width=True)
            
            if submit:
                if title and description:
                    create_task(title, description, domain, user_options[assigned], 
                              attachment, status, due_date, frequency)
                    st.success("Task created successfully")
                    st.rerun()
                else:
                    st.error("Title and Description are required")
    
    with tab2:
        st.subheader("View & Edit Tasks")
        tasks_df = get_tasks(role='admin')
        
        if not tasks_df.empty:
            st.info("Click status dropdown to update task status directly")
            
            for idx, row in tasks_df.iterrows():
                with st.expander(f"{row['title']} - ID: {row['task_id']} ({row['assigned_name']})", expanded=False):
                    # Display task info using Streamlit components instead of HTML
                    st.markdown(f"**Description:** {row['description']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Domain:** {row['domain']}")
                    with col2:
                        st.markdown(f"**Due Date:** {row['due_date']}")
                    with col3:
                        st.markdown(f"**Frequency:** {row['frequency']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Status:** {row['status']}")
                    with col2:
                        st.markdown(f"**Comments:** {row['comment_count']}")
                    
                    if row['attachment'] and str(row['attachment']).strip() and str(row['attachment']) != 'nan':
                        st.markdown(f"**Attachment:** [View Attachment]({row['attachment']})")
                    
                    st.markdown("---")
                    st.markdown("#### Quick Status Update")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        new_status = st.selectbox(
                            "Update Status",
                            ["Pending", "Completed"],
                            index=0 if row['status'] == "Pending" else 1,
                            key=f"admin_status_{row['task_id']}"
                        )
                    with col2:
                        if st.button("Update Status", key=f"update_btn_{row['task_id']}"):
                            if new_status != row['status']:
                                update_task_status_with_notification(
                                    row['task_id'], 
                                    new_status, 
                                    row['status'],
                                    st.session_state.user_name
                                )
                                st.rerun()
                    
                    st.markdown("---")
                    
                    # Comments section
                    st.markdown(f"#### Comments ({row['comment_count']})")
                    comments_df = get_comments(row['task_id'])
                    
                    if not comments_df.empty:
                        for _, comment in comments_df.iterrows():
                            st.markdown(f"""
                            <div style='
                                background-color: #f8fafc;
                                padding: 1rem;
                                border-radius: 6px;
                                margin: 0.75rem 0;
                                border-left: 3px solid #2563eb;
                            '>
                                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                                    <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
                                    <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
                                </div>
                                <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No comments yet")
                    
                    new_comment = st.text_area("Add a comment", key=f"edit_comment_{row['task_id']}", height=80, placeholder="Write your comment here...")
                    
                    if st.button("Post Comment", key=f"edit_post_{row['task_id']}", use_container_width=True):
                        if new_comment.strip():
                            add_comment(row['task_id'], st.session_state.user_id, new_comment)
                            st.success("Comment posted")
                            st.rerun()
                        else:
                            st.warning("Please enter a comment")
    
    with tab3:
        st.subheader("Delete Task")
        tasks_df = get_tasks(role='admin')
        
        if not tasks_df.empty:
            task_options = {f"{row['task_id']}: {row['title']} - {row['assigned_name']}": row['task_id'] 
                          for _, row in tasks_df.iterrows()}
            selected_task = st.selectbox("Select Task to Delete", list(task_options.keys()))
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Delete Task", type="primary", use_container_width=True):
                    delete_task(task_options[selected_task])
                    st.success("Task deleted successfully")
                    st.rerun()
        else:
            st.info("No tasks available to delete")
    
    with tab4:
        st.subheader("Bulk Upload Tasks")
        st.markdown("""
        <div style='
            background-color: #eff6ff;
            padding: 1.25rem;
            border-radius: 6px;
            border-left: 3px solid #2563eb;
            margin-bottom: 1.5rem;
        '>
        <h4 style='color: #1e3a8a; margin-top: 0; font-size: 1rem;'>Upload Instructions</h4>
        <ul style='color: #1e40af; margin-bottom: 0; font-size: 0.875rem;'>
            <li><strong>Required columns:</strong> Domain, Title, Description, Email, Status, Due_Date, Frequency</li>
            <li><strong>Date Format:</strong> DD-MM-YYYY or YYYY-MM-DD</li>
            <li><strong>Valid Domains:</strong> SAP, Network, EC, SalesFlo, NFlo, Help Desk, IT-Governance</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        excel_template = download_excel_template()
        st.download_button(
            label="Download Excel Template",
            data=excel_template,
            file_name="task_upload_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose Excel File", type=['xlsx', 'xls'], key="bulk_upload_file")
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.success("File loaded successfully")
                st.write("Preview:")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("Upload Tasks", use_container_width=True):
                    users_df = get_all_users()
                    email_to_id = {row['email']: row['user_id'] for _, row in users_df.iterrows()}
                    
                    success_count = 0
                    error_count = 0
                    error_messages = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, row in df.iterrows():
                        status_text.text(f"Processing task {idx + 1} of {len(df)}...")
                        
                        try:
                            email = str(row['Email']).strip()
                            
                            if email not in email_to_id:
                                error_messages.append(f"Row {idx+2}: Email {email} not found")
                                error_count += 1
                                continue
                            
                            due_date_str = str(row['Due_Date'])
                            try:
                                if '-' in due_date_str and len(due_date_str.split('-')[0]) <= 2:
                                    due_date = pd.to_datetime(due_date_str, format='%d-%m-%Y').date()
                                else:
                                    due_date = pd.to_datetime(due_date_str).date()
                            except:
                                error_messages.append(f"Row {idx+2}: Invalid date format")
                                error_count += 1
                                continue
                            
                            attachment = str(row.get('Attachment Link', ''))
                            if attachment == 'nan' or attachment == 'None':
                                attachment = ''
                            
                            create_task(
                                str(row['Title']).strip(),
                                str(row['Description']).strip(),
                                str(row['Domain']).strip(),
                                email_to_id[email],
                                attachment,
                                str(row['Status']).strip(),
                                due_date,
                                str(row['Frequency']).strip()
                            )
                            success_count += 1
                        except Exception as e:
                            error_messages.append(f"Row {idx+2}: {str(e)}")
                            error_count += 1
                        
                        progress_bar.progress((idx + 1) / len(df))
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    if success_count > 0:
                        st.success(f"{success_count} tasks uploaded successfully")
                    
                    if error_count > 0:
                        st.warning(f"{error_count} tasks failed to upload")
                        with st.expander("View Error Details"):
                            for msg in error_messages:
                                st.error(msg)
                    
                    if success_count > 0:
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    with tab5:
        st.subheader("All Tasks Overview")
        tasks_df = get_tasks(role='admin')
        
        if not tasks_df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])
            with col2:
                domain_filter = st.selectbox(
                    "Filter by Domain", 
                    ["All", "SAP", "Network", "EC", "SalesFlo", "NFlo", "Help Desk", "IT-Governance"]
                )
            with col3:
                user_filter = st.selectbox(
                    "Filter by User", 
                    ["All"] + tasks_df['assigned_name'].unique().tolist()
                )
            
            # Apply filters
            filtered_df = tasks_df.copy()
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            if domain_filter != "All":
                filtered_df = filtered_df[filtered_df['domain'] == domain_filter]
            if user_filter != "All":
                filtered_df = filtered_df[filtered_df['assigned_name'] == user_filter]
            
            st.markdown(f"**Showing {len(filtered_df)} tasks**")
            
            for idx, row in filtered_df.iterrows():
                with st.expander(f"{row['title']} - Status-({row['status']})- ({row['assigned_name']})", expanded=False):
                    # Task info
                    st.markdown(f"**Description:** {row['description']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Domain:** {row['domain']}")
                    with col2:
                        st.markdown(f"**Due Date:** {row['due_date']}")
                    with col3:
                        st.markdown(f"**Frequency:** {row['frequency']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Status:** {row['status']}")
                    with col2:
                        st.markdown(f"**Comments:** {row['comment_count']}")
                    
                    if row['attachment'] and str(row['attachment']).strip() and str(row['attachment']) != 'nan':
                        st.markdown(f"**Attachment:** [View Attachment]({row['attachment']})")
                    
                    st.markdown("---")
                    st.markdown("#### Quick Status Update")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        new_status = st.selectbox(
                            "Update Status",
                            ["Pending", "Completed"],
                            index=0 if row['status'] == "Pending" else 1,
                            key=f"all_status_{row['task_id']}"
                        )
                    with col2:
                        if st.button("Update Status", key=f"quick_update_{row['task_id']}"):
                            if new_status != row['status']:
                                update_task_status_with_notification(
                                    row['task_id'], 
                                    new_status, 
                                    row['status'],
                                    st.session_state.user_name
                                )
                                st.rerun()
                    
                    st.markdown("---")
                    
                    # Comments section
                    st.markdown(f"#### Comments ({row['comment_count']})")
                    comments_df = get_comments(row['task_id'])
                    
                    if not comments_df.empty:
                        for _, comment in comments_df.iterrows():
                            st.markdown(f"""
                            <div style='
                                background-color: #f8fafc;
                                padding: 1rem;
                                border-radius: 6px;
                                margin: 0.75rem 0;
                                border-left: 3px solid #2563eb;
                            '>
                                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                                    <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
                                    <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
                                </div>
                                <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No comments yet")
                    
                    new_comment = st.text_area(
                        "Add a comment",
                        key=f"all_comment_{row['task_id']}",
                        height=80,
                        placeholder="Write your comment here..."
                    )
                    
                    if st.button("Post Comment", key=f"all_post_{row['task_id']}", use_container_width=True):
                        if new_comment.strip():
                            add_comment(row['task_id'], st.session_state.user_id, new_comment)
                            st.success("Comment posted")
                            st.rerun()
                        else:
                            st.warning("Please enter a comment")
        else:
            st.info("No tasks available")

def save_plotly_as_image(fig, width=800, height=500):
    """Convert plotly figure to image and return as Image object"""
    img_bytes = fig.to_image(format="png", width=width, height=height)
    img_buffer = io.BytesIO(img_bytes)
    img_buffer.seek(0)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        tmp.write(img_bytes)
        tmp_path = tmp.name
    
    return tmp_path

def generate_pdf_report(tasks_df, role):
    """Generate a comprehensive PDF report of the analytics dashboard"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    temp_files = []  # Track temporary files for cleanup
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph("Analytics Dashboard Report", title_style)
    story.append(title)
    
    # Date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal'])
    story.append(date_text)
    story.append(Spacer(1, 0.3*inch))
    
    # Summary Metrics
    story.append(Paragraph("Summary Metrics", heading_style))
    
    metrics_data = [
        ['Metric', 'Value'],
        ['Total Tasks', str(len(tasks_df))],
        ['Pending Tasks', str(len(tasks_df[tasks_df['status'] == 'Pending']))],
        ['Completed Tasks', str(len(tasks_df[tasks_df['status'] == 'Completed']))],
        ['Total Comments', str(int(tasks_df['comment_count'].sum()))]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Status Distribution
    story.append(Paragraph("Status Distribution", heading_style))
    status_counts = tasks_df['status'].value_counts()
    status_data = [['Status', 'Count', 'Percentage']]
    for status, count in status_counts.items():
        percentage = f"{(count/len(tasks_df)*100):.1f}%"
        status_data.append([status, str(count), percentage])
    
    status_table = Table(status_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Add Status Distribution Pie Chart
    try:
        status_data = tasks_df['status'].value_counts().reset_index()
        status_data.columns = ['status', 'count']
        fig = px.pie(status_data, values='count', names='status',
                    color_discrete_sequence=['#f59e0b', '#10b981'],
                    title='Status Distribution')
        fig.update_layout(
            font=dict(family="Inter, sans-serif", size=12),
            showlegend=True
        )
        img_path = save_plotly_as_image(fig, width=600, height=400)
        temp_files.append(img_path)
        img = Image(img_path, width=5*inch, height=3.3*inch)
        story.append(img)
        story.append(Spacer(1, 0.2*inch))
    except Exception as e:
        story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
    
    story.append(PageBreak())
    
    # Domain Distribution (if domain column exists)
    if 'domain' in tasks_df.columns:
        story.append(Paragraph("Tasks by Domain", heading_style))
        domain_status = tasks_df.groupby(['domain', 'status']).size().unstack(fill_value=0)
        domain_data = [['Domain', 'Pending', 'Completed', 'Total']]
        for domain in domain_status.index:
            pending = domain_status.loc[domain].get('Pending', 0)
            completed = domain_status.loc[domain].get('Completed', 0)
            total = pending + completed
            domain_data.append([domain, str(pending), str(completed), str(total)])
        
        domain_table = Table(domain_data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.4*inch])
        domain_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(domain_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Add Domain Stacked Bar Chart
        try:
            fig = go.Figure()
            
            if 'Pending' in domain_status.columns:
                fig.add_trace(go.Bar(
                    name='Pending',
                    x=domain_status.index,
                    y=domain_status['Pending'],
                    marker_color='#f59e0b',
                    text=domain_status['Pending'],
                    textposition='inside'
                ))
            
            if 'Completed' in domain_status.columns:
                fig.add_trace(go.Bar(
                    name='Completed',
                    x=domain_status.index,
                    y=domain_status['Completed'],
                    marker_color='#10b981',
                    text=domain_status['Completed'],
                    textposition='inside'
                ))
            
            fig.update_layout(
                barmode='stack',
                title='Tasks by Domain (Stacked)',
                xaxis_title="Domain",
                yaxis_title="Number of Tasks",
                font=dict(family="Inter, sans-serif", size=12),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            img_path = save_plotly_as_image(fig, width=700, height=450)
            temp_files.append(img_path)
            img = Image(img_path, width=6*inch, height=3.8*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
    
    # Monthly breakdown
    if 'month' in tasks_df.columns:
        story.append(PageBreak())
        story.append(Paragraph("Monthly Task Distribution", heading_style))
        month_data = tasks_df.groupby('month').size().reset_index(name='count')
        month_table_data = [['Month', 'Task Count']]
        for _, row in month_data.iterrows():
            month_table_data.append([row['month'], str(row['count'])])
        
        month_table = Table(month_table_data, colWidths=[3*inch, 2*inch])
        month_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(month_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Add Monthly Bar Chart
        try:
            fig = px.bar(month_data, x='month', y='count',
                        color_discrete_sequence=['#2563eb'],
                        title='Tasks by Month')
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Tasks",
                font=dict(family="Inter, sans-serif", size=12)
            )
            img_path = save_plotly_as_image(fig, width=700, height=400)
            temp_files.append(img_path)
            img = Image(img_path, width=6*inch, height=3.4*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
        
        # Add Quarterly Chart
        if 'quarter' in tasks_df.columns:
            quarter_data = tasks_df.groupby('quarter').size().reset_index(name='count')
            try:
                fig = px.bar(quarter_data, x='quarter', y='count',
                            color_discrete_sequence=['#8b5cf6'],
                            title='Tasks by Quarter')
                fig.update_layout(
                    xaxis_title="Quarter",
                    yaxis_title="Tasks",
                    font=dict(family="Inter, sans-serif", size=12)
                )
                img_path = save_plotly_as_image(fig, width=700, height=400)
                temp_files.append(img_path)
                img = Image(img_path, width=6*inch, height=3.4*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
    
    # Team member distribution (for admin)
    if role == 'admin' and 'assigned_name' in tasks_df.columns:
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Tasks by Team Member", heading_style))
        user_data = tasks_df.groupby('assigned_name').size().reset_index(name='count')
        user_table_data = [['Team Member', 'Task Count']]
        for _, row in user_data.iterrows():
            user_table_data.append([row['assigned_name'], str(row['count'])])
        
        user_table = Table(user_table_data, colWidths=[3*inch, 2*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(user_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Add Team Member Bar Chart
        try:
            fig = px.bar(user_data, x='assigned_name', y='count',
                        color_discrete_sequence=['#8b5cf6'],
                        title='Tasks by Team Member')
            fig.update_layout(
                xaxis_title="Team Member",
                yaxis_title="Tasks",
                font=dict(family="Inter, sans-serif", size=12)
            )
            img_path = save_plotly_as_image(fig, width=700, height=400)
            temp_files.append(img_path)
            img = Image(img_path, width=6*inch, height=3.4*inch)
            story.append(img)
        except Exception as e:
            story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    # Clean up temporary files
    for temp_file in temp_files:
        try:
            os.unlink(temp_file)
        except:
            pass
    
    buffer.seek(0)
    return buffer

def show_analytics_dashboard(role):
    st.title("Analytics Dashboard")
    
    if role == 'admin':
        tasks_df = get_tasks(role='admin')
    else:
        tasks_df = get_tasks(st.session_state.user_id, role='user')
    
    if tasks_df.empty:
        st.info("No tasks available for analysis")
        return
    
    tasks_df['due_date'] = pd.to_datetime(tasks_df['due_date'])
    tasks_df['month'] = tasks_df['due_date'].dt.to_period('M').astype(str)
    tasks_df['quarter'] = tasks_df['due_date'].dt.to_period('Q').astype(str)
    
    # Download PDF Button at the top
    st.markdown("<br>", unsafe_allow_html=True)
    col_pdf, col_spacer = st.columns([1, 3])
    with col_pdf:
        pdf_buffer = generate_pdf_report(tasks_df, role)
        st.download_button(
            label="📥 Download Analytical Report",
            data=pdf_buffer,
            file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card(len(tasks_df), "Total Tasks", "#2563eb")
    with col2:
        create_metric_card(len(tasks_df[tasks_df['status'] == 'Pending']), "Pending", "#f59e0b")
    with col3:
        create_metric_card(len(tasks_df[tasks_df['status'] == 'Completed']), "Completed", "#10b981")
    with col4:
        create_metric_card(int(tasks_df['comment_count'].sum()), "Comments", "#8b5cf6")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if 'domain' in tasks_df.columns:
            st.subheader(" Tasks by Domain ")
            domain_status = tasks_df.groupby(['domain', 'status']).size().unstack(fill_value=0)
            
            fig = go.Figure()
            
            if 'Pending' in domain_status.columns:
                fig.add_trace(go.Bar(
                    name='Pending',
                    x=domain_status.index,
                    y=domain_status['Pending'],
                    marker_color='#f59e0b',
                    text=domain_status['Pending'],
                    textposition='inside'
                ))
            
            if 'Completed' in domain_status.columns:
                fig.add_trace(go.Bar(
                    name='Completed',
                    x=domain_status.index,
                    y=domain_status['Completed'],
                    marker_color='#10b981',
                    text=domain_status['Completed'],
                    textposition='inside'
                ))
            
            fig.update_layout(
                barmode='stack',
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_title="Domain",
                yaxis_title="Number of Tasks",
                font=dict(family="Inter, sans-serif"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis={'categoryorder': 'total descending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
    with col2:
        if role == 'admin':
            st.subheader("Tasks by Team Member")
            user_data = tasks_df.groupby('assigned_name').size().reset_index(name='count')
            fig = px.bar(user_data, x='assigned_name', y='count',
                        color_discrete_sequence=['#8b5cf6'])
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_title="Team Member",
                yaxis_title="Tasks",
                font=dict(family="Inter, sans-serif")
            )
            st.plotly_chart(fig, use_container_width=True)

    # Monthly and Quarterly Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tasks by Month")
        month_data = tasks_df.groupby('month').size().reset_index(name='count')
        fig = px.bar(month_data, x='month', y='count',
                    color_discrete_sequence=['#2563eb'])
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="Month",
            yaxis_title="Tasks",
            font=dict(family="Inter, sans-serif")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Tasks by Quarter")
        quarter_data = tasks_df.groupby['quarter'].size().reset_index(name='count')
        fig = px.bar(quarter_data, x='quarter', y='count',
                    color_discrete_sequence=['#8b5cf6'])
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="Quarter",
            yaxis_title="Tasks",
            font=dict(family="Inter, sans-serif")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Status and Comments Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Status Distribution")
        status_data = tasks_df['status'].value_counts().reset_index()
        status_data.columns = ['status', 'count']
        fig = px.pie(status_data, values='count', names='status',
                    color_discrete_sequence=['#f59e0b', '#10b981'])
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Inter, sans-serif")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Tasks by Comments")
        comment_data = tasks_df.groupby('comment_count').size().reset_index(name='task_count')
        fig = px.bar(comment_data, x='comment_count', y='task_count',
                    color_discrete_sequence=['#06b6d4'])
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="Comments",
            yaxis_title="Tasks",
            font=dict(family="Inter, sans-serif")
        )
        st.plotly_chart(fig, use_container_width=True)

def show_comments_page():
    st.title("All Comments")
    
    conn = get_db_connection()
    if conn is None:
        st.error("Database connection failed")
        return
    
    try:
        query = '''
        SELECT c.comment_id, c.comment_text, c.created_at, 
               u.name, u.email, t.title as task_title
        FROM comments c
        JOIN users u ON c.user_id = u.user_id
        JOIN tasks t ON c.task_id = t.task_id
        ORDER BY c.created_at DESC
        '''
        comments_df = pd.read_sql_query(query, conn)
        
        if not comments_df.empty:
            for _, comment in comments_df.iterrows():
                st.markdown(f"""
                <div style='
                    background-color: #ffffff;
                    padding: 1.25rem;
                    border-radius: 6px;
                    margin: 0.75rem 0;
                    border: 1px solid #e2e8f0;
                    border-left: 3px solid #2563eb;
                '>
                    <div style='margin-bottom: 0.75rem;'>
                        <span style='background-color: #dbeafe; color: #1e40af; padding: 0.25rem 0.625rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;'>{comment['task_title']}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;'>
                        <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
                        <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
                    </div>
                    <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No comments yet")
    except Exception as e:
        st.error(f"Error fetching comments: {str(e)}")
    finally:
        conn.close()

def show_email_page():
    st.title("Email Center")
      
    # sender_email = st.secrets.get("SENDER_EMAIL")
    # sender_password = st.secrets.get("SENDER_PASSWORD")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    email_mode = st.radio("Select Mode", ["Send to All Users", "Send to Individual"], horizontal=True)
    
    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    tasks_df = get_tasks(role='admin')
    pending_tasks = tasks_df[tasks_df['status'] == 'Pending']
    
    if pending_tasks.empty:
        st.success("No pending tasks")
        return
    
    users_with_pending = pending_tasks.groupby(['assigned_email', 'assigned_name']).size().reset_index(name='count')
    
    if email_mode == "Send to All Users":
        st.subheader("Pending Tasks Summary")
        st.dataframe(users_with_pending, use_container_width=True)
        
        if st.button("Send Emails to All", type="primary", use_container_width=True):
            if not sender_email or not sender_password:
                st.error("Please provide email credentials")
                return
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total = len(users_with_pending)
            success = 0
            
            for idx, (_, user) in enumerate(users_with_pending.iterrows()):
                status_text.text(f"Sending to {user['assigned_name']}...")
                
                user_tasks = pending_tasks[pending_tasks['assigned_email'] == user['assigned_email']]
                
                if send_email_summary(user['assigned_email'], user['assigned_name'], 
                                    user_tasks, sender_email, sender_password):
                    success += 1
                
                progress_bar.progress((idx + 1) / total)
            
            status_text.empty()
            progress_bar.empty()
            
            st.success(f"Sent {success}/{total} emails successfully")
    
    else:
        st.subheader("Send to Individual User")
        
        user_options = {f"{row['assigned_name']} ({row['assigned_email']}) - {row['count']} pending": 
                       row['assigned_email'] for _, row in users_with_pending.iterrows()}
        
        selected = st.selectbox("Select User", list(user_options.keys()))
        selected_email = user_options[selected]
        
        user_tasks = pending_tasks[pending_tasks['assigned_email'] == selected_email]
        user_name = users_with_pending[users_with_pending['assigned_email'] == selected_email]['assigned_name'].iloc[0]
        
        st.markdown(f"**User:** {user_name}")
        st.markdown(f"**Email:** {selected_email}")
        st.markdown(f"**Pending Tasks:** {len(user_tasks)}")
        
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        st.dataframe(user_tasks[['task_id', 'title', 'domain', 'due_date']], use_container_width=True)
        
        if st.button(f"Send Email to {user_name}", type="primary", use_container_width=True):
            if not sender_email or not sender_password:
                st.error("Please provide email credentials")
                return
            
            with st.spinner(f"Sending to {user_name}..."):
                if send_email_summary(selected_email, user_name, user_tasks, sender_email, sender_password):
                    st.success(f"Email sent to {user_name}")
                else:
                    st.error(f"Failed to send email")

def show_user_management():
    st.title("Team Management")
    
    tab1, tab2 = st.tabs(["Add User", "View Users"])
    
    with tab1:
        st.subheader("Add New User")
        with st.form("add_user_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="john.doe@company.com")
            role = st.selectbox("Role", ["user", "admin"])
            
            submit = st.form_submit_button("Add User", use_container_width=True)
            
            if submit:
                if name and email:
                    if add_user(name, email, role):
                        st.success("User added successfully")
                        st.rerun()
                    else:
                        st.error("User with this email already exists")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("All Users")
        users_df = get_all_users()
        
        for _, user in users_df.iterrows():
            role_color = "#2563eb" if user['role'] == "admin" else "#10b981"
            st.markdown(f"""
            <div style='
                background-color: #ffffff;
                padding: 1.25rem;
                border-radius: 6px;
                margin: 0.75rem 0;
                border: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            '>
                <div>
                    <h4 style='margin: 0 0 0.25rem 0; color: #0f172a; font-size: 1rem;'>{user['name']}</h4>
                    <p style='margin: 0; color: #64748b; font-size: 0.875rem;'>{user['email']}</p>
                </div>
                <span style='background-color: {role_color}; color: white; padding: 0.375rem 0.875rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;'>
                    {user['role'].upper()}
                </span>
            </div>
            """, unsafe_allow_html=True)

def show_user_dashboard():
    with st.sidebar:
        st.markdown(f"""
        <div style='
            background-color: #f8fafc;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 3px solid #2563eb;
            text-align: center;
            margin-bottom: 1.5rem;
        '>
            <div style='width: 64px; height: 64px; background-color: #10b981; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem; color: white; font-size: 1.5rem; font-weight: 700;'>
                {st.session_state.user_name[0]}
            </div>
            <h3 style='color: #0f172a; margin: 0 0 0.25rem 0; font-size: 1.125rem;'>{st.session_state.user_name}</h3>
            <p style='color: #64748b; margin: 0; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Team Member</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;'>Navigation</div>", unsafe_allow_html=True)
        
        menu = st.radio("", 
                       ["My Tasks", "Analytics"],
                       label_visibility="collapsed")
        
        st.markdown("<hr style='border-color: #e2e8f0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    if menu == "My Tasks":
        show_my_tasks()
    elif menu == "Analytics":
        show_analytics_dashboard('user')

def show_my_tasks():
    st.title("My Tasks")
    
    tasks_df = get_tasks(st.session_state.user_id, 'user')
    
    if tasks_df.empty:
        st.info("No tasks assigned to you")
        return
    
    tasks_df['month'] = pd.to_datetime(tasks_df['due_date']).dt.to_period('M').astype(str)
    tasks_df['quarter'] = pd.to_datetime(tasks_df['due_date']).dt.to_period('Q').astype(str)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        create_metric_card(len(tasks_df), "Total", "#2563eb")
    with col2:
        create_metric_card(len(tasks_df[tasks_df['status'] == 'Pending']), "Pending", "#f59e0b")
    with col3:
        create_metric_card(len(tasks_df[tasks_df['status'] == 'Completed']), "Completed", "#10b981")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])
    with col2:
        months = ["All"] + sorted(tasks_df['month'].unique().tolist())
        month_filter = st.selectbox("Filter by Month", months)
    with col3:
        quarters = ["All"] + sorted(tasks_df['quarter'].unique().tolist())
        quarter_filter = st.selectbox("Filter by Quarter", quarters)
    
    filtered_df = tasks_df.copy()
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if month_filter != "All":
        filtered_df = filtered_df[filtered_df['month'] == month_filter]
    if quarter_filter != "All":
        filtered_df = filtered_df[filtered_df['quarter'] == quarter_filter]
    
    st.subheader(f"Your Tasks ({len(filtered_df)})")
    
    if not filtered_df.empty:
        for idx, row in filtered_df.iterrows():
            with st.expander(f"{row['title']} - ({row['due_date']} {row['status']})", expanded=False):
                st.markdown(f"**Description:** {row['description']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Domain:** {row['domain']}")
                with col2:
                    st.markdown(f"**Due Date:** {row['due_date']}")
                with col3:
                    st.markdown(f"**Frequency:** {row['frequency']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Status:** {row['status']}")
                with col2:
                    st.markdown(f"**Comments:** {row['comment_count']}")
                
                if row['attachment'] and str(row['attachment']).strip() and str(row['attachment']) != 'nan':
                    st.markdown(f"**Attachment:** [View Attachment]({row['attachment']})")
                
                st.markdown("---")
                st.markdown("#### Quick Status Update")
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_status = st.selectbox(
                        "Update Status",
                        ["Pending", "Completed"],
                        index=0 if row['status'] == "Pending" else 1,
                        key=f"user_status_{row['task_id']}"
                    )
                with col2:
                    if st.button("Update Status", key=f"user_update_{row['task_id']}"):
                        if new_status != row['status']:
                            update_task_status_with_notification(
                                row['task_id'], 
                                new_status, 
                                row['status'],
                                st.session_state.user_name
                            )
                            st.rerun()
                
                st.markdown("---")
                
                # Comments section
                st.markdown(f"#### Comments ({row['comment_count']})")
                comments_df = get_comments(row['task_id'])
                
                if not comments_df.empty:
                    for _, comment in comments_df.iterrows():
                        st.markdown(f"""
                        <div style='
                            background-color: #f8fafc;
                            padding: 1rem;
                            border-radius: 6px;
                            margin: 0.75rem 0;
                            border-left: 3px solid #2563eb;
                        '>
                            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                                <strong style='color: #0f172a; font-size: 0.875rem;'>{comment['name']}</strong>
                                <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
                            </div>
                            <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem;'>{comment['comment_text']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No comments yet")
                
                new_comment = st.text_area("Add a comment", key=f"user_comment_{row['task_id']}", height=80, placeholder="Write your comment here...")
                
                if st.button("Post Comment", key=f"user_post_{row['task_id']}", use_container_width=True):
                    if new_comment.strip():
                        add_comment(row['task_id'], st.session_state.user_id, new_comment)
                        st.success("Comment posted")
                        st.rerun()
                    else:
                        st.warning("Please enter a comment")
    else:
        st.info("No tasks match the selected filters")

def download_excel_template():
    template_data = {
        'Domain': ['SAP', 'Network', 'EC'],
        'Title': ['Sample Task 1', 'Sample Task 2', 'Sample Task 3'],
        'Description': ['Description 1', 'Description 2', 'Description 3'],
        'Email': ['aliyashal309@gmail.com', 'farooquiyashal@gmail.com', 'yashalalifarooqui30@gmail.com'],
        'Attachment Link': ['https://example.com/file1', '', 'https://example.com/file3'],
        'Status': ['Pending', 'Completed', 'Pending'],
        'Due_Date': ['15-10-2025', '20-10-2025', '25-10-2025'],
        'Frequency': ['Monthly', 'Quarterly', 'Monthly']
    }
    
    df = pd.DataFrame(template_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')
    
    return output.getvalue()

def main():
    st.set_page_config(
        page_title="TaskFlow Pro",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    set_page_styling()
    init_database()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        show_login()
    else:
        if st.session_state.user_role == 'admin':
            show_admin_dashboard()
        else:
            show_user_dashboard()

if __name__ == "__main__":
    main()
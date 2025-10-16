import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
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
import streamlit as st
import pandas as pd
from datetime import datetime, date
# Import database functions
from database import *

# Email configuration
os.environ['PATH'] += os.pathsep + ':/usr/bin'
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

os.environ['PATH'] += os.pathsep + ':/usr/bin'

sender_email= os.environ.get("SMTP_USERNAME")
sender_password = os.environ.get("SMTP_PASSWORD") 

import plotly.io as pio
import base64
from io import BytesIO
import tempfile
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader

def plotly_fig_to_image(fig, width=600, height=400):
    """Convert Plotly figure to ReportLab Image object using base64"""
    try:
        # Convert plot to base64 string
        img_bytes = fig.to_image(format="png", width=width, height=height, scale=2, engine="kaleido")
        
        # Create a BytesIO object from the image bytes
        img_buffer = BytesIO(img_bytes)
        
        # Create Image object directly from bytes
        img = Image(img_buffer, width=6*inch, height=4*inch)
        return img
        
    except Exception as e:
        print(f"Chart generation error: {e}")
        # Return a simple placeholder
        return None

def generate_pdf_report(tasks_df, role):
    """Generate comprehensive PDF report with analytics and charts"""
    buffer = io.BytesIO()
    
    try:
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#1a202c')
        )
        title = Paragraph("TaskFlow Pro Analytics Report", title_style)
        story.append(title)
        
        # Report metadata
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            textColor=colors.HexColor('#64748b'),
            fontSize=10
        )
        story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", meta_style))
        story.append(Paragraph(f"User Role: {role.capitalize()}", meta_style))
        story.append(Spacer(1, 20))
        
        # Key Metrics Section
        story.append(Paragraph("Key Performance Metrics", styles['Heading2']))
        
        # Calculate metrics
        total_tasks = len(tasks_df)
        completed_tasks = len(tasks_df[tasks_df['status'] == 'Completed'])
        pending_tasks = len(tasks_df[tasks_df['status'].isin(['Open', 'In Progress'])])
        overdue_tasks = len(tasks_df[
            (tasks_df['due_date'] < datetime.now()) & 
            (tasks_df['status'].isin(['Open', 'In Progress']))
        ])
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Tasks', str(total_tasks)],
            ['Completed Tasks', str(completed_tasks)],
            ['Pending Tasks', str(pending_tasks)],
            ['Overdue Tasks', str(overdue_tasks)],
            ['Completion Rate', f"{(completed_tasks/total_tasks*100):.1f}%" if total_tasks > 0 else "0%"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Status Distribution
        story.append(Paragraph("Task Status Distribution", styles['Heading2']))
        status_counts = tasks_df['status'].value_counts()
        
        # Create status chart only if we have data
        if not status_counts.empty and len(status_counts) > 0:
            try:
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="",
                    color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444', '#6b7280']
                )
                fig_status.update_layout(
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(family="Arial", size=10),
                    showlegend=True,
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                
                status_chart_img = plotly_fig_to_image(fig_status, width=400, height=300)
                if status_chart_img:
                    story.append(status_chart_img)
                    story.append(Spacer(1, 10))
            except Exception as e:
                print(f"Status chart error: {e}")
        
        # Status Distribution Table
        status_data = [['Status', 'Count', 'Percentage']]
        for status, count in status_counts.items():
            percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
            status_data.append([status, str(count), f"{percentage:.1f}%"])
        
        status_table = Table(status_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bbf7d0'))
        ]))
        story.append(status_table)
        story.append(Spacer(1, 20))
        
        # Domain-wise breakdown (if available)
        if 'domain' in tasks_df.columns and not tasks_df['domain'].isna().all():
            story.append(Paragraph("Tasks by Domain", styles['Heading2']))
            
            domain_counts = tasks_df['domain'].value_counts().head(6)  # Top 6 domains
            
            if not domain_counts.empty:
                try:
                    fig_domain = px.bar(
                        x=domain_counts.index,
                        y=domain_counts.values,
                        title="",
                        labels={'x': 'Domain', 'y': 'Task Count'},
                        color=domain_counts.values,
                        color_continuous_scale='blues'
                    )
                    fig_domain.update_layout(
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        font=dict(family="Arial", size=10),
                        showlegend=False,
                        margin=dict(l=20, r=20, t=30, b=20),
                        xaxis_tickangle=-45
                    )
                    
                    domain_chart_img = plotly_fig_to_image(fig_domain, width=400, height=300)
                    if domain_chart_img:
                        story.append(domain_chart_img)
                        story.append(Spacer(1, 10))
                except Exception as e:
                    print(f"Domain chart error: {e}")
            
            # Domain table
            domain_data = [['Domain', 'Task Count', 'Percentage']]
            for domain, count in domain_counts.items():
                percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
                domain_data.append([domain, str(count), f"{percentage:.1f}%"])
            
            domain_table = Table(domain_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            domain_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd6fe'))
            ]))
            story.append(domain_table)
            story.append(Spacer(1, 20))
        
        # Priority breakdown (if available)
        if 'priority' in tasks_df.columns and not tasks_df['priority'].isna().all():
            story.append(Paragraph("Tasks by Priority", styles['Heading2']))
            
            priority_counts = tasks_df['priority'].value_counts()
            
            if not priority_counts.empty:
                try:
                    fig_priority = px.bar(
                        x=priority_counts.index,
                        y=priority_counts.values,
                        title="",
                        labels={'x': 'Priority', 'y': 'Task Count'},
                        color=priority_counts.index,
                        color_discrete_map={
                            'High': '#ef4444',
                            'Medium': '#f59e0b',
                            'Low': '#10b981'
                        }
                    )
                    fig_priority.update_layout(
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        font=dict(family="Arial", size=10),
                        showlegend=False,
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    
                    priority_chart_img = plotly_fig_to_image(fig_priority, width=400, height=300)
                    if priority_chart_img:
                        story.append(priority_chart_img)
                        story.append(Spacer(1, 10))
                except Exception as e:
                    print(f"Priority chart error: {e}")
            
            # Priority table
            priority_data = [['Priority', 'Count', 'Percentage']]
            for priority, count in priority_counts.items():
                percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
                priority_data.append([priority, str(count), f"{percentage:.1f}%"])
            
            priority_table = Table(priority_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            priority_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fffbeb')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fed7aa'))
            ]))
            story.append(priority_table)
            story.append(Spacer(1, 20))
        

        # Summary
        story.append(Spacer(1, 20))
        story.append(Paragraph("Report Summary", styles['Heading2']))
        summary_text = f"""
        This comprehensive analytics report provides insights into task management performance.
        
        Key Findings:
        • Total tasks analyzed: {total_tasks}\n
        • Overall completion rate: {(completed_tasks/total_tasks*100):.1f}%{' ' if total_tasks > 0 else '0%'}\n
        • Active workload: {(pending_tasks/total_tasks*100):.1f}%{' ' if total_tasks > 0 else '0%'} of tasks are in progress\n
        • Overdue tasks requiring attention: {overdue_tasks}
        
        Generated by TaskFlow Pro Analytics System.
        Report Period: {datetime.now().strftime('%B %Y')}
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        # Fallback to simple PDF without charts
        return generate_simple_pdf_report(tasks_df, role)

def generate_simple_pdf_report(tasks_df, role):
    """Generate a simple PDF report without charts as fallback"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    try:
        # Simple title and basic info
        story.append(Paragraph("TaskFlow Pro Analytics Report", styles['Heading1']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Paragraph(f"Role: {role.capitalize()}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Basic metrics
        total_tasks = len(tasks_df)
        completed_tasks = len(tasks_df[tasks_df['status'] == 'Completed'])
        pending_tasks = len(tasks_df[tasks_df['status'].isin(['Open', 'In Progress'])])
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Tasks', str(total_tasks)],
            ['Completed Tasks', str(completed_tasks)],
            ['Pending Tasks', str(pending_tasks)],
            ['Completion Rate', f"{(completed_tasks/total_tasks*100):.1f}%" if total_tasks > 0 else "0%"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Status summary
        story.append(Paragraph("Status Summary", styles['Heading2']))
        status_counts = tasks_df['status'].value_counts()
        status_data = [['Status', 'Count', 'Percentage']]
        
        for status, count in status_counts.items():
            percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
            status_data.append([status, str(count), f"{percentage:.1f}%"])
        
        status_table = Table(status_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bbf7d0'))
        ]))
        story.append(status_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Simple PDF generation also failed: {e}")
        # Return a minimal PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = [Paragraph("TaskFlow Pro Report - Generation Failed", styles['Heading1'])]
        doc.build(story)
        buffer.seek(0)
        return buffer
     
def show_analytics_dashboard(role):
    st.title("📊 Analytics Dashboard")
    
    if role == 'admin':
        tasks_df = get_tasks(role='admin')
    else:
        tasks_df = get_tasks(st.session_state.user_id, role='user')
    
    if tasks_df.empty:
        st.info("No tasks available for analysis")
        return
    
    # Prepare data for analysis
    tasks_df['due_date'] = pd.to_datetime(tasks_df['due_date'])
    tasks_df['month'] = tasks_df['due_date'].dt.to_period('M').astype(str)
    tasks_df['quarter'] = tasks_df['due_date'].dt.to_period('Q').astype(str)
    
    # Download PDF Button at the top
    st.markdown("<br>", unsafe_allow_html=True)
    col_pdf, col_spacer = st.columns([1, 3])
    with col_pdf:
        pdf_buffer = generate_pdf_report(tasks_df, role)
        st.download_button(
            label="📥 Download Comprehensive Report (PDF)",
            data=pdf_buffer,
            file_name=f"taskflow_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="Download detailed analytics report with charts and insights"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = len(tasks_df)
    completed_tasks = len(tasks_df[tasks_df['status'] == 'Completed'])
    pending_tasks = len(tasks_df[tasks_df['status'].isin(['Open', 'In Progress'])])
    total_comments = int(tasks_df['comment_count'].sum())
    
    with col1:
        create_metric_card(total_tasks, "Total Tasks", "📊")
    with col2:
        create_metric_card(pending_tasks, "Pending", "⏳")
    with col3:
        create_metric_card(completed_tasks, "Completed", "✅")
    with col4:
        create_metric_card(total_comments, "Total Comments", "💬")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        # Status Distribution
        st.subheader("📊 Task Status Distribution")
        status_counts = tasks_df['status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444', '#6b7280']
        )
        fig_status.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=400
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Priority Distribution
        if 'priority' in tasks_df.columns:
            st.subheader("🎯 Tasks by Priority")
            priority_counts = tasks_df['priority'].value_counts()
            fig_priority = px.bar(
                x=priority_counts.index,
                y=priority_counts.values,
                color=priority_counts.index,
                color_discrete_map={
                    'High': '#ef4444',
                    'Medium': '#f59e0b',
                    'Low': '#10b981'
                },
                labels={'x': 'Priority', 'y': 'Task Count'}
            )
            fig_priority.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_priority, use_container_width=True)
    
    # Second Row of Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Domain Distribution
        if 'domain' in tasks_df.columns:
            st.subheader("🏷️ Tasks by Domain")
            domain_counts = tasks_df['domain'].value_counts().head(10)
            fig_domain = px.bar(
                x=domain_counts.index,
                y=domain_counts.values,
                color=domain_counts.values,
                color_continuous_scale='blues',
                labels={'x': 'Domain', 'y': 'Task Count'}
            )
            fig_domain.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                height=400,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_domain, use_container_width=True)
    
    with col2:
        # Monthly Trend
        if 'due_date' in tasks_df.columns:
            st.subheader("📅 Monthly Task Trend")
            try:
                monthly_data = tasks_df.copy()
                monthly_data['month'] = monthly_data['due_date'].dt.to_period('M').astype(str)
                monthly_counts = monthly_data.groupby('month').size().reset_index(name='count')
                
                fig_monthly = px.line(
                    monthly_counts,
                    x='month',
                    y='count',
                    markers=True,
                    labels={'x': 'Month', 'y': 'Task Count'}
                )
                fig_monthly.update_layout(
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    height=400
                )
                st.plotly_chart(fig_monthly, use_container_width=True)
            except Exception as e:
                st.info("Not enough date data for monthly trend")
    
    # Team Performance (Admin only)
    if role == 'admin':
        st.markdown("---")
        st.subheader("👥 Team Performance")
        
        users_df = get_all_users()
        user_performance = []
        
        for _, user in users_df.iterrows():
            user_tasks = tasks_df[tasks_df['assigned_to'] == user['user_id']]
            if not user_tasks.empty:
                completed = len(user_tasks[user_tasks['status'] == 'Completed'])
                total = len(user_tasks)
                completion_rate = (completed / total * 100) if total > 0 else 0
                
                user_performance.append({
                    'User': user['name'],
                    'Total Tasks': total,
                    'Completed': completed,
                    'Completion Rate': completion_rate
                })
        
        if user_performance:
            perf_df = pd.DataFrame(user_performance).sort_values('Completion Rate', ascending=False)
            
            fig_team = px.bar(
                perf_df.head(10),
                x='User',
                y='Completion Rate',
                color='Completion Rate',
                color_continuous_scale='viridis',
                labels={'x': 'Team Member', 'y': 'Completion Rate %'}
            )
            fig_team.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                height=400,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_team, use_container_width=True)
            
            # Performance table
            with st.expander("View Detailed Performance Table"):
                st.dataframe(
                    perf_df,
                    use_container_width=True,
                    column_config={
                        "User": "Team Member",
                        "Total Tasks": st.column_config.NumberColumn("Total Tasks"),
                        "Completed": st.column_config.NumberColumn("Completed"),
                        "Completion Rate": st.column_config.ProgressColumn(
                            "Completion Rate",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100
                        )
                    }
                )
def update_task_status_with_notification(task_id, new_status, old_status, user_name):
    """Update task status and send notification if completed"""
    update_task_status(task_id, new_status, st.session_state.user_id)
    
    # Send notification if status changed to "Completed"
    if new_status == "Completed" and old_status != "Completed":
        task = get_task_by_id(task_id)
        if task:           
            if sender_email and sender_password:
                with st.spinner("Sending completion notification..."):
                    if send_task_completion_notification(task, user_name, sender_email, sender_password):
                        st.success("Status updated and admins notified!")
                    else:
                        st.error("Status updated, but failed to send notifications to admins")
            else:
                st.success("Status updated! (Email credentials not configured)")
        else:
            st.success("Status updated!")
    else:
        st.success("Status updated!")

def show_task_comments(task_id):
    """Show comments for a specific task with ability to add new comments"""
    st.subheader("💬 Task Comments & Discussion")
    
    # Get existing comments
    comments_df = get_comments(task_id)
    
    # Display existing comments
    if not comments_df.empty:
        st.markdown("### 📝 Conversation History")
        for _, comment in comments_df.iterrows():
            # Determine background color based on user role
            bg_color = "#eff6ff" if comment['user_id'] == st.session_state.user_id else "#f8fafc"
            border_color = "#3b82f6" if comment['user_id'] == st.session_state.user_id else "#e2e8f0"
            
            st.markdown(f"""
            <div style='
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-left: 4px solid {border_color};
                border-radius: 8px;
                padding: 1rem;
                margin: 0.75rem 0;
            '>
                <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;'>
                    <div style='display: flex; align-items: center; gap: 0.5rem;'>
                        <strong style='color: #1e293b; font-size: 0.875rem;'>{comment['name']}</strong>
                        <span style='background: #{"#3b82f6" if comment["user_id"] == st.session_state.user_id else "#64748b"}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 600;'>
                            {"You" if comment["user_id"] == st.session_state.user_id else "Team Member"}
                        </span>
                    </div>
                    <small style='color: #64748b; font-size: 0.75rem;'>{comment['created_at']}</small>
                </div>
                <p style='margin: 0; color: #334155; line-height: 1.6; font-size: 0.875rem; white-space: pre-wrap;'>{comment['comment_text']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💭 No comments yet. Start the conversation!")
    
    # Add new comment
    st.markdown("---")
    st.markdown("### 💭 Add a Comment")
    
    with st.form(key=f"add_comment_{task_id}"):
        new_comment = st.text_area(
            "Your comment",
            placeholder="Type your message here...",
            height=100,
            key=f"comment_text_{task_id}"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submit_comment = st.form_submit_button(
                "💬 Post Comment",
                use_container_width=True,
                type="primary"
            )
        
        if submit_comment and new_comment.strip():
            if add_comment(task_id, st.session_state.user_id, new_comment.strip()):
                st.success("✅ Comment added successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to add comment")
        elif submit_comment:
            st.warning("⚠️ Please enter a comment before posting")

def show_comment_section_in_task(task):
    """Show comment section within task view"""
    with st.expander("💬 Comments & Discussion", expanded=False):
        show_task_comments(task['task_id'])

def set_page_styling():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem;
        max-width: 1400px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        margin: 1rem auto;
    }
    

    
    [data-testid="stSidebar"] .stRadio > div {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 4px;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label {
        color: #e2e8f0;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 2px 0;
    }
    
    [data-testid="stSidebar"] .stRadio input:checked + div {
        background-color: #4299e1;
    }
    
    [data-testid="stSidebar"] .stRadio input:checked + div > label {
        color: white;
        font-weight: 600;
    }
    
    h1 {
        color: #1a202c;
        font-weight: 700;
        font-size: 2.25rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        border-bottom: 3px solid;
        border-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) 1;
      
    }
    
    h2 {
        color: #2d3748;
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #4a5568;
        font-weight: 600;
        font-size: 1.125rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    .secondary-button>button {
        background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
        color: #4a5568;
        border: 1px solid #cbd5e0;
    }
    
    .danger-button>button {
        background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);
        color: white;
    }
    
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div,
    .stDateInput>div>div>input {
        border: 1px solid #cbd5e0;
        border-radius: 8px;
        font-size: 14px;
        transition: all 0.3s ease;
        background-color: #ffffff;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>div:focus,
    .stDateInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: transparent;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #718096;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
        border-radius: 6px 6px 0 0;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f7fafc;
        color: #4a5568;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #667eea;
        border-bottom: 2px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stExpander {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 1rem;
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .streamlit-expanderHeader {
        background-color: #f7fafc;
        font-weight: 600;
        padding: 1rem 1.5rem;
        transition: all 0.3s ease;
        color: #2d3748;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #edf2f7;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1a202c;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        font-weight: 600;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stAlert {
        border-radius: 8px;
        padding: 1rem 1.25rem;
        border-left-width: 4px;
    }
    
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
    }
    
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6b419c 100%);
    }
    
    </style>
    """, unsafe_allow_html=True)


def create_metric_card(value, label, icon="📊"):
    """Create a modern metric card with icon"""
    st.markdown(f"""
    <div style="
        margin: 0.75rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    ">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 2.25rem; font-weight: 700; color: #1a202c; margin-bottom: 0.25rem;">{value}</div>
        <div style="font-size: 0.875rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def create_task_card(task, show_actions=True):
    """Enhanced task card with comment count and quick actions"""
    
    # Get basic task info
    title = str(task.get('title', 'Untitled Task'))
    status = task.get('status', 'Open')
    priority = task.get('priority', 'Medium')
    description = str(task.get('description', 'No description'))
    domain = str(task.get('domain', 'No domain'))
    comment_count = task.get('comment_count', 0)
    
    # Status colors and icons
    status_config = {
        'Completed': {'icon': '🟢', 'color': '#10b981'},
        'In Progress': {'icon': '🟡', 'color': '#f59e0b'},
        'Open': {'icon': '⚪', 'color': '#6b7280'},
        'Pending': {'icon': '🟠', 'color': '#f97316'}
    }
    
    status_info = status_config.get(status, status_config['Open'])
    
    # Priority colors
    priority_colors = {
        'High': '#ef4444',
        'Medium': '#f59e0b',
        'Low': '#10b981'
    }
    
    priority_color = priority_colors.get(priority, '#6b7280')
    
    html = f"""
    <div style="
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin: 0.75rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="flex: 1;">
                <h3 style="margin: 0 0 0.5rem 0; color: #1a202c; font-size: 1.125rem;">{title}</h3>
                <p style="margin: 0 0 0.75rem 0; color: #64748b; font-size: 0.875rem; line-height: 1.5;">{description}</p>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.8rem;">
                    <span style="background: {status_info['color']}15; color: {status_info['color']}; padding: 0.3rem 0.6rem; border-radius: 6px; border: 1px solid {status_info['color']}30;">
                        {status_info['icon']} {status}
                    </span>
                    <span style="background: {priority_color}15; color: {priority_color}; padding: 0.3rem 0.6rem; border-radius: 6px; border: 1px solid {priority_color}30;">
        """
    
    # Add priority icon
    if priority == 'High':
        html += '🔴 '
    elif priority == 'Medium':
        html += '🟡 '
    else:
        html += '🟢 '
    
    html += f"""
                        {priority}
                    </span>
                    <span style="background: #6366f115; color: #6366f1; padding: 0.3rem 0.6rem; border-radius: 6px; border: 1px solid #6366f130;">
                        🏷️ {domain}
                    </span>
                    <span style="background: #8b5cf615; color: #8b5cf6; padding: 0.3rem 0.6rem; border-radius: 6px; border: 1px solid #8b5cf630;">
                        💬 {comment_count} comments
                    </span>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def show_login():
    """Show professional login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 3rem 2rem;'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>🚀</div>
            <h1 style='color: #1a202c; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 800;'>TaskFlow Pro</h1>
            <p style='color: #64748b; font-size: 1.125rem; font-weight: 500; margin-bottom: 3rem;'>Enterprise Task Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); 
                        border: 1px solid #e2e8f0; 
                        border-radius: 12px; 
                        padding: 2rem;
                        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);'>
            """, unsafe_allow_html=True)
            
            st.markdown("<h2 style='text-align: center; color: #1a202c; margin-bottom: 0.5rem;'>Welcome Back</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem; font-size: 0.875rem;'>Enter your corporate email to continue</p>", unsafe_allow_html=True)
            
            email = st.text_input("", placeholder="your.email@company.com", label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Sign In", use_container_width=True):
                    if email:
                        user = get_user_by_email(email)
                        if user:
                            st.session_state.user_id = user['user_id']
                            st.session_state.user_name = user['name']
                            st.session_state.user_email = user['email']
                            st.session_state.user_role = user['role']
                            st.session_state.logged_in = True
                            st.rerun()
                        else:
                            st.error("User not found. Please check your email address or contact your administrator.")
                    else:
                        st.warning("Please enter your email address")
            
            st.markdown("""
            <div style='text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0;'>
                <p style='color: #94a3b8; font-size: 0.75rem; margin: 0;'>
                    Secure access • Enterprise grade • SOC 2 Compliant
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

def show_domain_management():
    """Show comprehensive domain management interface"""
    st.title("🏷️ Domain Management")
    
    tab1, tab2, tab3 = st.tabs(["📋 All Domains", "➕ Add New Domain", "📊 Domain Usage Statistics"])
    
    with tab1:
        show_all_domains()
    
    with tab2:
        show_add_domain_form()
    
    with tab3:
        show_domain_bulk_operations()

def show_add_user_form():
    """Show form to add new user"""
    st.subheader("➕ Add New Team Member")
    
    with st.form("add_user_form"):
        st.markdown("""
        <div style='
            background: #f0f9ff; 
            border: 1px solid #bae6fd; 
            border-radius: 8px; 
            padding: 1rem; 
            margin-bottom: 1.5rem;
        '>
            <h4 style='color: #0369a1; margin: 0 0 0.5rem 0;'>💡 User Setup Guide</h4>
            <ul style='color: #0c4a6e; margin: 0; font-size: 0.875rem;'>
                <li><strong>Admin Users:</strong> Full access to all features, can manage tasks, users, and domains</li>
                <li><strong>Regular Users:</strong> Can only view and update their assigned tasks</li>
                <li>Users will receive email notifications for their tasks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Full Name *", 
                placeholder="John Smith",
                help="Full name of the team member"
            )
            
            email = st.text_input(
                "Email Address *", 
                placeholder="john.smith@company.com",
                help="Corporate email address for login and notifications"
            )
        
        with col2:
            role = st.selectbox(
                "Role *",
                ["user", "admin"],
                format_func=lambda x: "👑 Administrator" if x == "admin" else "👤 Team Member",
                help="Administrators have full system access"
            )
            
            # Show existing users for reference
            existing_users = get_all_users()
            if not existing_users.empty:
                with st.expander("📋 Existing Team Members", expanded=False):
                    st.dataframe(
                        existing_users[['name', 'email', 'role']], 
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "name": "Name",
                            "email": "Email",
                            "role": st.column_config.TextColumn("Role", help="User role")
                        }
                    )
        
        # Validation
        if email and not existing_users.empty:
            email_exists = email in existing_users['email'].values
            if email_exists:
                st.error(f"❌ User with email '{email}' already exists")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit = st.form_submit_button("👥 Add Team Member", use_container_width=True)
            
            if submit:
                if name and email:
                    if add_user(name, email, role):
                        st.success("🎉 Team member added successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to add user. Email might already exist.")
                else:
                    st.error("⚠️ Please fill all required fields (*)")

def show_user_statistics():
    """Show user statistics and performance metrics"""
    st.subheader("📊 User Performance & Statistics")
    
    users_df = get_all_users()
    tasks_df = get_tasks(role='admin')
    
    if users_df.empty or tasks_df.empty:
        st.info("No data available for user statistics.")
        return
    
    # Calculate user statistics
    user_stats = []
    for _, user in users_df.iterrows():
        user_tasks = tasks_df[tasks_df['assigned_to'] == user['user_id']]
        total_tasks = len(user_tasks)
        completed_tasks = len(user_tasks[user_tasks['status'] == 'Completed'])
        overdue_tasks = len(user_tasks[
            (user_tasks['due_date'] < datetime.now()) & 
            (user_tasks['status'].isin(['Open', 'In Progress']))
        ])
        in_progress_tasks = len(user_tasks[user_tasks['status'] == 'In Progress'])
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        user_stats.append({
            'user_id': user['user_id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completion_rate': completion_rate
        })
    
    user_stats_df = pd.DataFrame(user_stats)
    
    # Overall Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = len(users_df)
        admin_users = len(users_df[users_df['role'] == 'admin'])
        st.metric("Total Users", total_users, f"{admin_users} admins")
    
    with col2:
        avg_completion_rate = user_stats_df['completion_rate'].mean()
        st.metric("Avg Completion Rate", f"{avg_completion_rate:.1f}%")
    
    with col3:
        total_overdue = user_stats_df['overdue_tasks'].sum()
        st.metric("Total Overdue Tasks", total_overdue)
    
    with col4:
        most_tasks_user = user_stats_df.loc[user_stats_df['total_tasks'].idxmax()] if not user_stats_df.empty else None
        if most_tasks_user:
            st.metric("Most Tasks", most_tasks_user['name'], f"{most_tasks_user['total_tasks']} tasks")
    
    st.markdown("---")
    
    # User Performance Table
    st.subheader("👥 User Performance Overview")
    
    # Sort options
    col1, col2 = st.columns([2, 1])
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ["Total Tasks", "Completion Rate", "Overdue Tasks", "Name"],
            index=0
        )
    with col2:
        sort_order = st.selectbox("Order", ["Descending", "Ascending"])
    
    # Sort data
    sort_columns = {
        "Total Tasks": "total_tasks",
        "Completion Rate": "completion_rate",
        "Overdue Tasks": "overdue_tasks",
        "Name": "name"
    }
    
    sorted_df = user_stats_df.sort_values(
        sort_columns[sort_by],
        ascending=(sort_order == "Ascending")
    )
    
    # Display performance table
    for _, user_stat in sorted_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                role_icon = "👑" if user_stat['role'] == 'admin' else "👤"
                st.markdown(f"**{role_icon} {user_stat['name']}**")
                st.caption(user_stat['email'])
            
            with col2:
                st.metric("Total", user_stat['total_tasks'])
            
            with col3:
                st.metric("Completed", user_stat['completed_tasks'])
            
            with col4:
                # Completion rate with color coding
                completion_color = "#10b981" if user_stat['completion_rate'] >= 80 else "#f59e0b" if user_stat['completion_rate'] >= 50 else "#ef4444"
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 1.25rem; font-weight: 600; color: {completion_color};">
                        {user_stat['completion_rate']:.1f}%
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b;">Completion</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                overdue_color = "#ef4444" if user_stat['overdue_tasks'] > 0 else "#64748b"
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 1.25rem; font-weight: 600; color: {overdue_color};">
                        {user_stat['overdue_tasks']}
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b;">Overdue</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")

def show_edit_user_modal():
    """Show modal for editing user details"""
    st.markdown("---")
    st.subheader("✏️ Edit Team Member")
    
    with st.form("edit_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input(
                "Full Name *", 
                value=st.session_state.editing_user_name,
                placeholder="John Smith"
            )
        
        with col2:
            new_email = st.text_input(
                "Email Address *", 
                value=st.session_state.editing_user_email,
                placeholder="john.smith@company.com"
            )
        
        new_role = st.selectbox(
            "Role *",
            ["user", "admin"],
            index=0 if st.session_state.editing_user_role == "user" else 1,
            format_func=lambda x: "👑 Administrator" if x == "admin" else "👤 Team Member"
        )
        
        # Warning if user is editing themselves
        if st.session_state.editing_user_id == st.session_state.user_id:
            st.warning("⚠️ You are editing your own account. Changing your role may affect your access.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.form_submit_button("💾 Update User", use_container_width=True):
                if new_name and new_email:
                    if update_user(
                        st.session_state.editing_user_id,
                        new_name,
                        new_email,
                        new_role
                    ):
                        st.success("✅ User updated successfully!")
                        # Clear session state
                        for key in ['editing_user_id', 'editing_user_name', 'editing_user_email', 'editing_user_role']:
                            if hasattr(st.session_state, key):
                                delattr(st.session_state, key)
                        st.rerun()
                    else:
                        st.error("❌ Failed to update user")
                else:
                    st.error("⚠️ Please fill all fields")
        
        with col3:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                for key in ['editing_user_id', 'editing_user_name', 'editing_user_email', 'editing_user_role']:
                    if hasattr(st.session_state, key):
                        delattr(st.session_state, key)
                st.rerun()

def show_delete_user_modal():
    """Show confirmation modal for deleting user"""
    st.markdown("---")
    st.error("🚨 Delete User Confirmation")
    
    # Get user tasks for warning
    tasks_df = get_tasks(role='admin')
    user_tasks = tasks_df[tasks_df['assigned_to'] == st.session_state.deleting_user_id]
    active_tasks = len(user_tasks[user_tasks['status'].isin(['Open', 'In Progress'])])
    
    st.warning(f"""
    You are about to delete the user **"{st.session_state.deleting_user_name}"**.
    
    ⚠️ **This action will:**
    - Permanently remove this user from the system
    - The user will no longer be able to login
    - {active_tasks} active tasks will become unassigned
    - User comments will be preserved but show as "Deleted User"
    
    This action cannot be undone.
    """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("✅ Confirm Delete", type="primary", use_container_width=True):
            if delete_user(st.session_state.deleting_user_id):
                st.success("✅ User deleted successfully!")
                # Clear session state
                for key in ['deleting_user_id', 'deleting_user_name']:
                    if hasattr(st.session_state, key):
                        delattr(st.session_state, key)
                st.rerun()
            else:
                st.error("❌ Failed to delete user")
    
    with col3:
        if st.button("❌ Cancel", use_container_width=True):
            for key in ['deleting_user_id', 'deleting_user_name']:
                if hasattr(st.session_state, key):
                    delattr(st.session_state, key)
            st.rerun()

def show_all_domains():
    """Show all domains with edit and delete options"""
    st.subheader("Manage Domains & Mancom Members")
    
    domains_df = get_domains()
    
    if not domains_df.empty:
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Domains", len(domains_df))
        with col2:
            active_tasks_df = get_tasks(role='admin')
            domain_usage = active_tasks_df['domain'].value_counts()
            st.metric("Most Used Domain", domain_usage.index[0] if not domain_usage.empty else "N/A")
        with col3:
            st.metric("Mancom Members", len(domains_df['mancom_member_email'].unique()))
        
        st.markdown("---")
        
        # Search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search domains or mancom members...", placeholder="Enter domain name or mancom member name")
        with col2:
            sort_option = st.selectbox("Sort by", ["Domain Name A-Z", "Domain Name Z-A", "Mancom Member A-Z"])
        
        # Filter domains based on search
        filtered_domains = domains_df.copy()
        if search_term:
            filtered_domains = filtered_domains[
                filtered_domains['domain_name'].str.contains(search_term, case=False, na=False) |
                filtered_domains['mancom_member_name'].str.contains(search_term, case=False, na=False) |
                filtered_domains['mancom_member_email'].str.contains(search_term, case=False, na=False)
            ]
        
        # Sort domains
        if sort_option == "Domain Name A-Z":
            filtered_domains = filtered_domains.sort_values('domain_name')
        elif sort_option == "Domain Name Z-A":
            filtered_domains = filtered_domains.sort_values('domain_name', ascending=False)
        elif sort_option == "Mancom Member A-Z":
            filtered_domains = filtered_domains.sort_values('mancom_member_name')
        
        st.markdown(f"**Showing {len(filtered_domains)} of {len(domains_df)} domains**")
        
        # Display domains in a grid
        for idx, domain in filtered_domains.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
                        border: 1px solid #e2e8f0;
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin: 0.5rem 0;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    '>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                            <div style='flex: 1;'>
                                <h3 style='color: #1a202c; margin: 0 0 0.5rem 0; font-size: 1.25rem; font-weight: 600;'>
                                    🏷️ {domain['domain_name']}
                                </h3>
                                <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;'>
                                    <div style='
                                        background: #ebf8ff; 
                                        color: #3182ce; 
                                        padding: 0.25rem 0.75rem; 
                                        border-radius: 6px; 
                                        font-size: 0.875rem; 
                                        font-weight: 500;
                                        display: inline-flex;
                                        align-items: center;
                                        gap: 0.25rem;
                                    '>
                                        👤 {domain['mancom_member_name']}
                                    </div>
                                </div>
                                <div style='color: #64748b; font-size: 0.875rem;'>
                                    <strong>Email:</strong> {domain['mancom_member_email']}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_edit, col_delete = st.columns(2)
                    
                    with col_edit:
                        if st.button("✏️", key=f"edit_{domain['domain_id']}", help="Edit Domain"):
                            st.session_state.editing_domain_id = domain['domain_id']
                            st.session_state.editing_domain_name = domain['domain_name']
                            st.session_state.editing_mancom_name = domain['mancom_member_name']
                            st.session_state.editing_mancom_email = domain['mancom_member_email']
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️", key=f"delete_{domain['domain_id']}", help="Delete Domain"):
                            st.session_state.deleting_domain_id = domain['domain_id']
                            st.session_state.deleting_domain_name = domain['domain_name']
        
        # Edit Domain Modal
        if hasattr(st.session_state, 'editing_domain_id'):
            show_edit_domain_modal()
        
        # Delete Domain Confirmation
        if hasattr(st.session_state, 'deleting_domain_id'):
            show_delete_domain_modal()
            
    else:
        st.info("📭 No domains configured. Add your first domain to get started.")

def show_edit_domain_modal():
    """Show modal for editing domain details"""
    st.markdown("---")
    st.subheader("✏️ Edit Domain")
    
    with st.form("edit_domain_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_domain_name = st.text_input(
                "Domain Name", 
                value=st.session_state.editing_domain_name,
                placeholder="e.g., SAP, Network, Finance"
            )
        
        with col2:
            new_mancom_name = st.text_input(
                "Mancom Member Name", 
                value=st.session_state.editing_mancom_name,
                placeholder="Full name of mancom member"
            )
        
        new_mancom_email = st.text_input(
            "Mancom Member Email", 
            value=st.session_state.editing_mancom_email,
            placeholder="mancom.member@company.com"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.form_submit_button("💾 Update Domain", use_container_width=True):
                if new_domain_name and new_mancom_name and new_mancom_email:
                    if update_domain(
                        st.session_state.editing_domain_id,
                        new_domain_name,
                        new_mancom_name,
                        new_mancom_email
                    ):
                        st.success("✅ Domain updated successfully!")
                        # Clear session state
                        for key in ['editing_domain_id', 'editing_domain_name', 'editing_mancom_name', 'editing_mancom_email']:
                            if hasattr(st.session_state, key):
                                delattr(st.session_state, key)
                        st.rerun()
                    else:
                        st.error("❌ Failed to update domain")
                else:
                    st.error("⚠️ Please fill all fields")
        
        with col3:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                for key in ['editing_domain_id', 'editing_domain_name', 'editing_mancom_name', 'editing_mancom_email']:
                    if hasattr(st.session_state, key):
                        delattr(st.session_state, key)
                st.rerun()

def show_delete_domain_modal():
    """Show confirmation modal for deleting domain"""
    st.markdown("---")
    st.error("🚨 Delete Domain Confirmation")
    
    st.warning(f"""
    You are about to delete the domain **"{st.session_state.deleting_domain_name}"**.
    
    ⚠️ **This action will:**
    - Remove this domain from the system
    - Tasks assigned to this domain will show "Unknown Domain"
    - Mancom member will no longer receive escalation emails
    
    This action cannot be undone.
    """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("✅ Confirm Delete", type="primary", use_container_width=True):
            if delete_domain(st.session_state.deleting_domain_id):
                st.success("✅ Domain deleted successfully!")
                # Clear session state
                for key in ['deleting_domain_id', 'deleting_domain_name']:
                    if hasattr(st.session_state, key):
                        delattr(st.session_state, key)
                st.rerun()
            else:
                st.error("❌ Failed to delete domain")
    
    with col3:
        if st.button("❌ Cancel", use_container_width=True):
            for key in ['deleting_domain_id', 'deleting_domain_name']:
                if hasattr(st.session_state, key):
                    delattr(st.session_state, key)
            st.rerun()

def show_add_domain_form():
    """Show form to add new domain"""
    st.subheader("➕ Add New Domain")
    
    with st.form("add_domain_form"):
        st.markdown("""
        <div style='
            background: #f0f9ff; 
            border: 1px solid #bae6fd; 
            border-radius: 8px; 
            padding: 1rem; 
            margin-bottom: 1.5rem;
        '>
            <h4 style='color: #0369a1; margin: 0 0 0.5rem 0;'>💡 Domain Setup Guide</h4>
            <ul style='color: #0c4a6e; margin: 0; font-size: 0.875rem;'>
                <li>Domains represent functional areas in your organization</li>
                <li>Each domain has a Mancom member responsible for escalations</li>
                <li>Mancom members receive email notifications for overdue tasks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            domain_name = st.text_input(
                "Domain Name *", 
                placeholder="e.g., SAP, Network, Finance, Marketing",
                help="The functional area or department name"
            )
            
            mancom_member_name = st.text_input(
                "Mancom Member Name *", 
                placeholder="Full name of the responsible person",
                help="The executive or manager responsible for this domain"
            )
        
        with col2:
            mancom_member_email = st.text_input(
                "Mancom Member Email *", 
                placeholder="executive.name@company.com",
                help="Official email address for escalation notifications"
            )
            
            # Show existing domains for reference
            existing_domains = get_domains()
            if not existing_domains.empty:
                with st.expander("📋 Existing Domains", expanded=False):
                    st.dataframe(
                        existing_domains[['domain_name', 'mancom_member_name']], 
                        use_container_width=True,
                        hide_index=True
                    )
        
        # Validation
        if domain_name and not existing_domains.empty:
            domain_exists = domain_name in existing_domains['domain_name'].values
            if domain_exists:
                st.error(f"❌ Domain '{domain_name}' already exists")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit = st.form_submit_button("🚀 Add Domain", use_container_width=True)
            
            if submit:
                if domain_name and mancom_member_name and mancom_member_email:
                    if add_domain(domain_name, mancom_member_name, mancom_member_email):
                        st.success("🎉 Domain added successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to add domain. It might already exist.")
                else:
                    st.error("⚠️ Please fill all required fields (*)")

def show_domain_bulk_operations():
    """Show bulk operations for domains"""
    
        
    domains_df = get_domains()
    
   
    st.markdown("---")
 
    # Domain Usage Statistics
    st.subheader("📊 Domain Usage Statistics")
    
    tasks_df = get_tasks(role='admin')
    if not tasks_df.empty and not domains_df.empty:
        # Task count by domain
        domain_task_count = tasks_df['domain'].value_counts().reset_index()
        domain_task_count.columns = ['Domain', 'Task Count']
        
        # Merge with domain info
        domain_stats = pd.merge(
            domains_df, 
            domain_task_count, 
            left_on='domain_name', 
            right_on='Domain', 
            how='left'
        )
        domain_stats['Task Count'] = domain_stats['Task Count'].fillna(0).astype(int)
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            most_used_domain = domain_stats.loc[domain_stats['Task Count'].idxmax()] if not domain_stats.empty else None
            if most_used_domain is not None:
                st.metric(
                    "Most Active Domain", 
                    most_used_domain['domain_name'],
                    f"{most_used_domain['Task Count']} tasks"
                )
        
        with col2:
            total_tasks = domain_stats['Task Count'].sum()
            st.metric("Total Tasks Across Domains", total_tasks)
        
        with col3:
            domains_with_tasks = len(domain_stats[domain_stats['Task Count'] > 0])
            st.metric("Domains with Active Tasks", domains_with_tasks)
        
        # Display domain usage table
        st.markdown("#### Domain Task Distribution")
        display_df = domain_stats[['domain_name', 'mancom_member_name', 'Task Count']].sort_values('Task Count', ascending=False)
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "domain_name": "Domain",
                "mancom_member_name": "Mancom Member",
                "Task Count": st.column_config.NumberColumn("Task Count", format="%d")
            }
        )
        
        # Visualization
        if not domain_stats.empty:
            fig = px.bar(
                domain_stats.nlargest(10, 'Task Count'), 
                x='domain_name', 
                y='Task Count',
                title="Top 10 Domains by Task Count",
                color='Task Count',
                color_continuous_scale='blues'
            )
            fig.update_layout(
                xaxis_title="Domain",
                yaxis_title="Number of Tasks",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No task data available for domain usage statistics.")

def show_user_management():
    """Enhanced user management with similar interface"""
    st.title("👥 Team Management")
    
    tab1, tab2, tab3 = st.tabs(["📋 All Users", "➕ Add New User", "📊 User Statistics"])
    
    with tab1:
        show_all_users()
    
    with tab2:
        show_add_user_form()
    
    with tab3:
        show_user_statistics()

def show_all_users():
    """Show all users with edit and delete options"""
    st.subheader("Manage Team Members")
    
    users_df = get_all_users()
    
    if not users_df.empty:
        # Search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search users...", placeholder="Enter name or email")
        with col2:
            role_filter = st.selectbox("Filter by Role", ["All", "Admin", "User"])
        
        # Filter users
        filtered_users = users_df.copy()
        if search_term:
            filtered_users = filtered_users[
                filtered_users['name'].str.contains(search_term, case=False, na=False) |
                filtered_users['email'].str.contains(search_term, case=False, na=False)
            ]
        if role_filter != "All":
            filtered_users = filtered_users[filtered_users['role'] == role_filter.lower()]
        
        st.markdown(f"**Showing {len(filtered_users)} of {len(users_df)} users**")
        
        # Display users
        for idx, user in filtered_users.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    role_color = "#667eea" if user['role'] == "admin" else "#48bb78"
                    role_icon = "👑" if user['role'] == "admin" else "👤"
                    
                    st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
                        border: 1px solid #e2e8f0;
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin: 0.5rem 0;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    '>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                            <div style='flex: 1;'>
                                <h3 style='color: #1a202c; margin: 0 0 0.5rem 0; font-size: 1.25rem; font-weight: 600;'>
                                    {user['name']}
                                </h3>
                                <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;'>
                                    <div style='
                                        background: {role_color}; 
                                        color: white; 
                                        padding: 0.25rem 0.75rem; 
                                        border-radius: 6px; 
                                        font-size: 0.875rem; 
                                        font-weight: 500;
                                        display: inline-flex;
                                        align-items: center;
                                        gap: 0.25rem;
                                    '>
                                        {role_icon} {user['role'].upper()}
                                    </div>
                                </div>
                                <div style='color: #64748b; font-size: 0.875rem;'>
                                    <strong>Email:</strong> {user['email']}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_edit, col_delete = st.columns(2)
                    
                    with col_edit:
                        if st.button("✏️", key=f"edit_user_{user['user_id']}", help="Edit User"):
                            st.session_state.editing_user_id = user['user_id']
                            st.session_state.editing_user_name = user['name']
                            st.session_state.editing_user_email = user['email']
                            st.session_state.editing_user_role = user['role']
                            st.rerun()
                    
                    with col_delete:
                        if user['user_id'] != st.session_state.user_id:  # Prevent self-deletion
                            if st.button("🗑️", key=f"delete_user_{user['user_id']}", help="Delete User"):
                                st.session_state.deleting_user_id = user['user_id']
                                st.session_state.deleting_user_name = user['name']
                        else:
                            st.button("🗑️", key=f"delete_user_{user['user_id']}", disabled=True, help="Cannot delete yourself")
        
        # Edit User Modal
        if hasattr(st.session_state, 'editing_user_id'):
            show_edit_user_modal()
        
        # Delete User Confirmation
        if hasattr(st.session_state, 'deleting_user_id'):
            show_delete_user_modal()
            
    else:
        st.info("📭 No users found. Add your first team member.")

def show_email_page():
    st.title("Email Center")
    
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

def show_admin_dashboard():
    """Show admin dashboard with enhanced sidebar"""
    with st.sidebar:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        '>
            <div style='width: 64px; height: 64px; background-color: rgba(255, 255, 255, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem; color: white; font-size: 1.5rem; font-weight: 700; backdrop-filter: blur(10px);'>
                {st.session_state.user_name[0].upper()}
            </div>
            <h3 style='color: white; margin: 0 0 0.25rem 0; font-size: 1.125rem;'>{st.session_state.user_name}</h3>
            <p style='color: rgba(255, 255, 255, 0.8); margin: 0; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Administrator</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='color: #e2e8f0; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;'>Navigation</div>", unsafe_allow_html=True)
        
        menu_options = {
          
            "📋 Task Management": "tasks",
            "👥 Team Management": "team",
            "🏷️ Domain Management": "domains", 
            "📈 Analytics": "analytics",
            "💬 Comments": "comments",
            "📧 Email Center": "email",
          
        }
        
        menu = st.radio("", list(menu_options.keys()), label_visibility="collapsed")
        
        st.markdown("<hr style='border-color: #4a5568; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        # Quick stats - include domain count
        tasks_df = get_tasks(role='admin')
        domains_df = get_domains()
        
        if not tasks_df.empty:
            overdue_tasks = len(tasks_df[(tasks_df['due_date'] < datetime.now()) & (tasks_df['status'].isin(['Open', 'In Progress']))])
            st.markdown(f"""
            <div style='color: #00000; font-size: 0.75rem; margin-bottom: 1rem;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>Total Tasks:</span>
                    <span style='font-weight: 600;'>{len(tasks_df)}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>Overdue:</span>
                    <span style='color: #fc8181; font-weight: 600;'>{overdue_tasks}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>Domains:</span>
                    <span style='font-weight: 600;'>{len(domains_df)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content based on menu selection
    menu_action = menu_options[menu]
  
    if menu_action == "tasks":
        show_task_management()
    elif menu_action == "team":
        show_user_management()
    elif menu_action == "domains":  # New domain management
        show_domain_management()
    elif menu_action == "analytics":
        show_analytics_dashboard('admin')
    elif menu_action == "comments":
        show_comments_page()
    elif menu_action == "email":
        show_email_page()

def show_escalation_center():
    """Show escalation center for overdue tasks and mancom notifications"""
    st.title("🚨 Escalation Center")
    
    tab1, tab2,  = st.tabs(["📋 Overdue Tasks", "👥 Mancom Alerts"])
    
    with tab1:
        show_overdue_tasks()
    
    with tab2:
        show_mancom_alerts()
    

def show_overdue_tasks():
    """Show all overdue tasks with escalation options"""
    st.subheader("📋 Overdue Tasks Requiring Attention")
    
    # Get overdue tasks
    overdue_tasks = get_overdue_tasks()
    tasks_due_soon = get_tasks_due_soon(7)  # Tasks due in next 7 days
    
    if overdue_tasks.empty and tasks_due_soon.empty:
        st.success("🎉 No overdue tasks and no tasks due soon! Great job!")
        return
    
    # Overdue Tasks Section
    if not overdue_tasks.empty:
        st.error(f"🚨 **{len(overdue_tasks)} Overdue Tasks**")
        
        for idx, task in overdue_tasks.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Calculate overdue days
                    overdue_days = (datetime.now().date() - task['due_date'].date()).days
                    
                    st.markdown(f"""
                    <div style='
                        background: #fef2f2;
                        border: 1px solid #fecaca;
                        border-left: 4px solid #dc2626;
                        border-radius: 8px;
                        padding: 1rem;
                        margin: 0.5rem 0;
                    '>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                            <div style='flex: 1;'>
                                <h4 style='color: #dc2626; margin: 0 0 0.5rem 0; font-size: 1.125rem;'>
                                    ⚠️ {task['title']}
                                </h4>
                                <p style='color: #7f1d1d; margin: 0 0 0.5rem 0; font-size: 0.875rem;'>
                                    {task['description']}
                                </p>
                                <div style='display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.8125rem;'>
                                    <span style='background: #fecaca; color: #7f1d1d; padding: 0.25rem 0.5rem; border-radius: 4px;'>
                                        👤 {task['assigned_name']}
                                    </span>
                                    <span style='background: #fecaca; color: #7f1d1d; padding: 0.25rem 0.5rem; border-radius: 4px;'>
                                        🏷️ {task['domain']}
                                    </span>
                                    <span style='background: #dc2626; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: 600;'>
                                        ⏰ {overdue_days} days overdue
                                    </span>
                                    <span style='background: #fecaca; color: #7f1d1d; padding: 0.25rem 0.5rem; border-radius: 4px;'>
                                        📅 Due: {task['due_date'].strftime('%b %d, %Y')}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✉️ Escalate", key=f"escalate_{task['task_id']}", use_container_width=True):
                        if sender_email and sender_password:
                            with st.spinner("Sending escalation email..."):
                                if send_escalation_email(task, sender_email, sender_password):
                                    st.success(f"✅ Escalation sent to {task['domain']} mancom member")
                                else:
                                    st.error("❌ Failed to send escalation")
                        else:
                            st.error("❌ Email credentials not configured")
                
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("📝 Update", key=f"update_{task['task_id']}", use_container_width=True):
                        st.session_state.editing_task_id = task['task_id']
                        st.rerun()
        
        st.markdown("---")
    
    # Tasks Due Soon Section
    if not tasks_due_soon.empty:
        st.warning(f"⚠️ **{len(tasks_due_soon)} Tasks Due in Next 7 Days**")
        
        for idx, task in tasks_due_soon.iterrows():
            with st.container():
                # Calculate days remaining
                days_remaining = (task['due_date'].date() - datetime.now().date()).days
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='
                        background: #fffbeb;
                        border: 1px solid #fed7aa;
                        border-left: 4px solid #f59e0b;
                        border-radius: 8px;
                        padding: 1rem;
                        margin: 0.5rem 0;
                    '>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                            <div style='flex: 1;'>
                                <h4 style='color: #92400e; margin: 0 0 0.5rem 0; font-size: 1.125rem;'>
                                    📅 {task['title']}
                                </h4>
                                <p style='color: #92400e; margin: 0 0 0.5rem 0; font-size: 0.875rem;'>
                                    {task['description']}
                                </p>
                                <div style='display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.8125rem;'>
                                    <span style='background: #fed7aa; color: #92400e; padding: 0.25rem 0.5rem; border-radius: 4px;'>
                                        👤 {task['assigned_name']}
                                    </span>
                                    <span style='background: #fed7aa; color: #92400e; padding: 0.25rem 0.5rem; border-radius: 4px;'>
                                        🏷️ {task['domain']}
                                    </span>
                                    <span style='background: #f59e0b; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: 600;'>
                                        ⏰ Due in {days_remaining} days
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("📝 Update", key=f"soon_update_{task['task_id']}", use_container_width=True):
                        st.session_state.editing_task_id = task['task_id']
                        st.rerun()
    
    # Bulk Actions
    st.markdown("---")
    st.subheader("🔄 Bulk Escalation Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Escalate All Overdue", use_container_width=True):
            if not overdue_tasks.empty:
                if sender_email and sender_password:
                    success_count = 0
                    progress_bar = st.progress(0)
                    for idx, task in enumerate(overdue_tasks.iterrows()):
                        if send_escalation_email(task[1], sender_email, sender_password):
                            success_count += 1
                        progress_bar.progress((idx + 1) / len(overdue_tasks))
                    st.success(f"✅ Sent {success_count}/{len(overdue_tasks)} escalation emails")
                else:
                    st.error("❌ Email credentials not configured")
            else:
                st.info("ℹ️ No overdue tasks to escalate")
    
    with col2:
        if st.button("📋 Generate Escalation Report", use_container_width=True):
            if not overdue_tasks.empty:
                csv_data = overdue_tasks.to_csv(index=False)
                st.download_button(
                    label="📥 Download Overdue Report",
                    data=csv_data,
                    file_name=f"escalation_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ No overdue tasks for report")
    
    with col3:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()

def show_mancom_alerts():
    """Show mancom member information and alert settings"""
    st.subheader("👥 Mancom Member Alert Configuration")
    
    domains_df = get_domains()
    
    if domains_df.empty:
        st.info("📭 No domains configured. Add domains to set up mancom alerts.")
        return
    
    # Mancom Member Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Domains", len(domains_df))
    
    with col2:
        active_tasks = get_tasks(role='admin')
        domains_with_tasks = active_tasks['domain'].nunique() if not active_tasks.empty else 0
        st.metric("Domains with Active Tasks", domains_with_tasks)
    
    with col3:
        overdue_by_domain = active_tasks[
            (active_tasks['due_date'] < datetime.now()) & 
            (active_tasks['status'].isin(['Open', 'In Progress']))
        ]['domain'].value_counts()
        st.metric("Domains with Overdue", len(overdue_by_domain))
    
    st.markdown("---")
    
    # Mancom Member List
    st.subheader("🏷️ Domain Mancom Members")
    
    for idx, domain in domains_df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.markdown(f"**{domain['domain_name']}**")
                st.caption(f"👤 {domain['mancom_member_name']}")
            
            with col2:
                st.markdown(f"📧 {domain['mancom_member_email']}")
                
                # Get domain task statistics
                domain_tasks = active_tasks[active_tasks['domain'] == domain['domain_name']] if not active_tasks.empty else pd.DataFrame()
                overdue_count = len(domain_tasks[
                    (domain_tasks['due_date'] < datetime.now()) & 
                    (domain_tasks['status'].isin(['Open', 'In Progress']))
                ]) if not domain_tasks.empty else 0
                
                if overdue_count > 0:
                    st.error(f"🚨 {overdue_count} overdue tasks")
                else:
                    st.success("✅ No overdue tasks")
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_mancom_{domain['domain_id']}", use_container_width=True):
                    st.session_state.editing_domain_id = domain['domain_id']
                    st.session_state.editing_domain_name = domain['domain_name']
                    st.session_state.editing_mancom_name = domain['mancom_member_name']
                    st.session_state.editing_mancom_email = domain['mancom_member_email']
                    st.rerun()
            
            with col4:
                if st.button("📧 Test Email", key=f"test_mancom_{domain['domain_id']}", use_container_width=True):
                    if sender_email and sender_password:
                        # Create a test task for email
                        test_task = {
                            'title': 'Test Escalation Email',
                            'description': 'This is a test escalation email to verify configuration.',
                            'domain': domain['domain_name'],
                            'assigned_name': 'Test User',
                            'due_date': datetime.now(),
                            'status': 'Open',
                            'priority': 'High'
                        }
                        if send_escalation_email(test_task, sender_email, sender_password):
                            st.success("✅ Test email sent successfully!")
                        else:
                            st.error("❌ Failed to send test email")
                    else:
                        st.error("❌ Email credentials not configured")
            
            st.markdown("---")
    
    # Mancom Alert Statistics
    st.subheader("📊 Mancom Alert Statistics")
    
    if not active_tasks.empty:
        # Overdue tasks by domain
        domain_overdue = active_tasks[
            (active_tasks['due_date'] < datetime.now()) & 
            (active_tasks['status'].isin(['Open', 'In Progress']))
        ]['domain'].value_counts().reset_index()
        domain_overdue.columns = ['Domain', 'Overdue Tasks']
        
        if not domain_overdue.empty:
            fig = px.bar(
                domain_overdue,
                x='Domain',
                y='Overdue Tasks',
                title="Overdue Tasks by Domain",
                color='Overdue Tasks',
                color_continuous_scale='reds'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🎉 No overdue tasks across all domains!")


def show_task_reports():
    """Show comprehensive task reporting and analytics"""
    st.title("📊 Task Reports & Analytics")
    
    tab1, tab2, tab3 = st.tabs(["📈 Performance", "📋 Detailed Reports", "📅 Timeline"])
    
    with tab1:
        show_performance_reports()
    
    with tab2:
        show_detailed_reports()
    
    with tab3:
        show_timeline_reports()
    

def show_performance_reports():
    """Show performance analytics and metrics"""
    st.subheader("📈 Performance Analytics")
    
    tasks_df = get_tasks(role='admin')
    users_df = get_all_users()
    
    if tasks_df.empty:
        st.info("No task data available for performance reports.")
        return
    
    # Key Performance Indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = len(tasks_df)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        completion_rate = (len(tasks_df[tasks_df['status'] == 'Completed']) / total_tasks * 100) if total_tasks > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col3:
        avg_completion_time = calculate_avg_completion_time(tasks_df)
        st.metric("Avg Completion Time", avg_completion_time)
    
    with col4:
        on_time_rate = calculate_on_time_rate(tasks_df)
        st.metric("On-Time Rate", f"{on_time_rate:.1f}%")
    
    st.markdown("---")
    
    # Performance Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Status Distribution
        status_counts = tasks_df['status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Task Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Priority Distribution
        if 'priority' in tasks_df.columns:
            priority_counts = tasks_df['priority'].value_counts()
            fig_priority = px.bar(
                x=priority_counts.index,
                y=priority_counts.values,
                title="Tasks by Priority",
                color=priority_counts.values,
                color_continuous_scale='reds'
            )
            st.plotly_chart(fig_priority, use_container_width=True)
    
    # Monthly Performance Trend
    st.subheader("📅 Monthly Performance Trend")
    
    monthly_data = tasks_df.copy()
    monthly_data['month'] = monthly_data['due_date'].dt.to_period('M').astype(str)
    monthly_stats = monthly_data.groupby('month').agg({
        'task_id': 'count',
        'status': lambda x: (x == 'Completed').sum()
    }).reset_index()
    monthly_stats.columns = ['Month', 'Total Tasks', 'Completed Tasks']
    monthly_stats['Completion Rate'] = (monthly_stats['Completed Tasks'] / monthly_stats['Total Tasks'] * 100).round(1)
    
    fig_trend = px.line(
        monthly_stats,
        x='Month',
        y='Completion Rate',
        title="Monthly Completion Rate Trend",
        markers=True
    )
    fig_trend.update_traces(line=dict(color='#10b981', width=3))
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # User Performance
    st.subheader("👥 User Performance Ranking")
    
    user_performance = []
    for _, user in users_df.iterrows():
        user_tasks = tasks_df[tasks_df['assigned_to'] == user['user_id']]
        if not user_tasks.empty:
            completed = len(user_tasks[user_tasks['status'] == 'Completed'])
            total = len(user_tasks)
            user_performance.append({
                'User': user['name'],
                'Total Tasks': total,
                'Completed': completed,
                'Completion Rate': (completed / total * 100) if total > 0 else 0,
                'Overdue': len(user_tasks[
                    (user_tasks['due_date'] < datetime.now()) & 
                    (user_tasks['status'].isin(['Open', 'In Progress']))
                ])
            })
    
    if user_performance:
        performance_df = pd.DataFrame(user_performance).sort_values('Completion Rate', ascending=False)
        st.dataframe(
            performance_df,
            use_container_width=True,
            column_config={
                "User": "User",
                "Total Tasks": st.column_config.NumberColumn("Total Tasks"),
                "Completed": st.column_config.NumberColumn("Completed"),
                "Completion Rate": st.column_config.ProgressColumn(
                    "Completion Rate",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100
                ),
                "Overdue": st.column_config.NumberColumn("Overdue Tasks")
            }
        )

def show_detailed_reports():
    """Show detailed task reports with filtering"""
    st.subheader("📋 Detailed Task Reports")
    
    tasks_df = get_tasks(role='admin')
    
    if tasks_df.empty:
        st.info("No tasks available for detailed reports.")
        return
    
    # Report Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["All Tasks", "Overdue Tasks", "Completed Tasks", "High Priority", "By Domain"]
        )
    
    with col2:
        date_range = st.selectbox(
            "Date Range",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"]
        )
    
    with col3:
        if date_range == "Custom Range":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
    
    with col4:
        export_format = st.selectbox(
            "Export Format",
            ["CSV", "Excel", "PDF"]
        )
    
    # Apply filters
    filtered_df = tasks_df.copy()
    
    if report_type == "Overdue Tasks":
        filtered_df = filtered_df[
            (filtered_df['due_date'] < datetime.now()) & 
            (filtered_df['status'].isin(['Open', 'In Progress']))
        ]
    elif report_type == "Completed Tasks":
        filtered_df = filtered_df[filtered_df['status'] == 'Completed']
    elif report_type == "High Priority":
        filtered_df = filtered_df[filtered_df['priority'] == 'High']
    elif report_type == "By Domain":
        domains = filtered_df['domain'].unique()
        selected_domain = st.selectbox("Select Domain", domains)
        filtered_df = filtered_df[filtered_df['domain'] == selected_domain]
    
    if date_range == "Last 7 Days":
        cutoff_date = datetime.now() - timedelta(days=7)
        filtered_df = filtered_df[filtered_df['due_date'] >= cutoff_date]
    elif date_range == "Last 30 Days":
        cutoff_date = datetime.now() - timedelta(days=30)
        filtered_df = filtered_df[filtered_df['due_date'] >= cutoff_date]
    elif date_range == "Last 90 Days":
        cutoff_date = datetime.now() - timedelta(days=90)
        filtered_df = filtered_df[filtered_df['due_date'] >= cutoff_date]
    elif date_range == "Custom Range":
        filtered_df = filtered_df[
            (filtered_df['due_date'] >= pd.Timestamp(start_date)) & 
            (filtered_df['due_date'] <= pd.Timestamp(end_date))
        ]
    
    st.markdown(f"**Report: {report_type}** | **Total Records: {len(filtered_df)}**")
    
    # Display report
    if not filtered_df.empty:
        display_columns = ['task_id', 'title', 'domain', 'assigned_name', 'status', 'priority', 'due_date', 'comment_count']
        display_df = filtered_df[display_columns].copy()
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "task_id": "Task ID",
                "title": "Title",
                "domain": "Domain",
                "assigned_name": "Assigned To",
                "status": "Status",
                "priority": "Priority",
                "due_date": "Due Date",
                "comment_count": "Comments"
            }
        )
        
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if export_format == "CSV":
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"task_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            if export_format == "Excel":
                # For Excel export, you would use a library like openpyxl
                st.button("📊 Download Excel", use_container_width=True, disabled=True)
        
        with col3:
            if export_format == "PDF":
                st.button("📄 Generate PDF", use_container_width=True, disabled=True)
    else:
        st.info("No tasks match the selected filters.")

def show_timeline_reports():
    """Show timeline and Gantt chart reports"""
    st.subheader("📅 Task Timeline & Gantt Chart")
    
    tasks_df = get_tasks(role='admin')
    
    if tasks_df.empty:
        st.info("No tasks available for timeline reports.")
        return
    
    # Simplified Gantt chart using plotly
    gantt_data = []
    for _, task in tasks_df.iterrows():
        if pd.notna(task['due_date']):
            gantt_data.append({
                'Task': task['title'],
                'Start': task['created_at'].strftime('%Y-%m-%d'),
                'Finish': task['due_date'].strftime('%Y-%m-%d'),
                'Resource': task['assigned_name'],
                'Completion': 100 if task['status'] == 'Completed' else 50 if task['status'] == 'In Progress' else 0
            })
    
    if gantt_data:
        gantt_df = pd.DataFrame(gantt_data)
        
        fig = px.timeline(
            gantt_df,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Resource",
            title="Task Timeline View"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No valid timeline data available.")


def calculate_avg_completion_time(tasks_df):
    """Calculate average completion time for tasks"""
    completed_tasks = tasks_df[tasks_df['status'] == 'Completed']
    if completed_tasks.empty:
        return "N/A"
    
    completion_times = []
    for _, task in completed_tasks.iterrows():
        if pd.notna(task['due_date']) and pd.notna(task['created_at']):
            days = (task['due_date'] - task['created_at']).days
            completion_times.append(days)
    
    if completion_times:
        avg_days = sum(completion_times) / len(completion_times)
        return f"{avg_days:.1f} days"
    return "N/A"

def calculate_on_time_rate(tasks_df):
    """Calculate on-time completion rate"""
    if tasks_df.empty:
        return 0
    
    # Safe check for completed tasks
    if 'status' not in tasks_df.columns:
        return 0
    
    completed_tasks = tasks_df[tasks_df['status'] == 'Completed']
    
    # Check if completed_tasks is empty using .empty
    if completed_tasks.empty:
        return 0
    
    on_time_count = 0
    for _, task in completed_tasks.iterrows():
        if pd.notna(task.get('due_date')):
            # Consider task on-time if completed on or before due date
            # Allow 1 day grace period
            try:
                if isinstance(task['due_date'], (pd.Timestamp, datetime)):
                    due_date = task['due_date']
                else:
                    due_date = pd.to_datetime(task['due_date'])
                
                # If we have completion date, use it; otherwise assume completed now
                completion_date = datetime.now() - timedelta(days=1)  # Default to yesterday
                
                if due_date >= completion_date:
                    on_time_count += 1
            except:
                # If date comparison fails, count as not on-time
                continue
    
    # Use len() on the DataFrame to get count
    return (on_time_count / len(completed_tasks) * 100) if len(completed_tasks) > 0 else 0

def calculate_avg_completion_time(tasks_df):
    """Calculate average completion time for tasks"""
    if tasks_df.empty:
        return "N/A"
    
    # Safe column checks
    if 'status' not in tasks_df.columns or 'due_date' not in tasks_df.columns or 'created_at' not in tasks_df.columns:
        return "N/A"
    
    completed_tasks = tasks_df[tasks_df['status'] == 'Completed']
    
    # Check if completed_tasks is empty
    if completed_tasks.empty:
        return "N/A"
    
    completion_times = []
    for _, task in completed_tasks.iterrows():
        if pd.notna(task.get('due_date')) and pd.notna(task.get('created_at')):
            try:
                # Convert to datetime if needed
                if isinstance(task['due_date'], (pd.Timestamp, datetime)):
                    due_date = task['due_date']
                else:
                    due_date = pd.to_datetime(task['due_date'])
                
                if isinstance(task['created_at'], (pd.Timestamp, datetime)):
                    created_at = task['created_at']
                else:
                    created_at = pd.to_datetime(task['created_at'])
                
                days = (due_date - created_at).days
                completion_times.append(days)
            except Exception as e:
                # Skip if date calculation fails
                continue
    
    if completion_times:
        avg_days = sum(completion_times) / len(completion_times)
        return f"{avg_days:.1f} days"
    return "N/A"

def show_performance_reports():
    """Show performance analytics and metrics"""
    st.subheader("📈 Performance Analytics")
    
    tasks_df = get_tasks(role='admin')
    users_df = get_all_users()
    
    if tasks_df.empty:
        st.info("No task data available for performance reports.")
        return
    
    # Key Performance Indicators with safe checks
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = len(tasks_df)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        # Safe completion rate calculation
        if 'status' in tasks_df.columns:
            completed_count = len(tasks_df[tasks_df['status'] == 'Completed'])
            completion_rate = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
        else:
            completion_rate = 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col3:
        avg_completion_time = calculate_avg_completion_time(tasks_df)
        st.metric("Avg Completion Time", avg_completion_time)
    
    with col4:
        on_time_rate = calculate_on_time_rate(tasks_df)
        st.metric("On-Time Rate", f"{on_time_rate:.1f}%")
    
    st.markdown("---")
    
    # Performance Charts with safe data handling
    col1, col2 = st.columns(2)
    
    with col1:
        # Status Distribution with safe check
        if 'status' in tasks_df.columns:
            status_counts = tasks_df['status'].value_counts()
            if not status_counts.empty:
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Task Status Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("No status data available")
        else:
            st.info("Status column not available")
    
    with col2:
        # Priority Distribution with safe check
        if 'priority' in tasks_df.columns:
            priority_counts = tasks_df['priority'].value_counts()
            if not priority_counts.empty:
                fig_priority = px.bar(
                    x=priority_counts.index,
                    y=priority_counts.values,
                    title="Tasks by Priority",
                    color=priority_counts.values,
                    color_continuous_scale='reds'
                )
                st.plotly_chart(fig_priority, use_container_width=True)
            else:
                st.info("No priority data available")
        else:
            st.info("Priority column not available")
    
    # Monthly Performance Trend with safe date handling
    st.subheader("📅 Monthly Performance Trend")
    
    if 'due_date' in tasks_df.columns:
        monthly_data = tasks_df.copy()
        try:
            monthly_data['month'] = monthly_data['due_date'].dt.to_period('M').astype(str)
            monthly_stats = monthly_data.groupby('month').agg({
                'task_id': 'count',
                'status': lambda x: (x == 'Completed').sum()
            }).reset_index()
            monthly_stats.columns = ['Month', 'Total Tasks', 'Completed Tasks']
            monthly_stats['Completion Rate'] = (monthly_stats['Completed Tasks'] / monthly_stats['Total Tasks'] * 100).round(1)
            
            if not monthly_stats.empty:
                fig_trend = px.line(
                    monthly_stats,
                    x='Month',
                    y='Completion Rate',
                    title="Monthly Completion Rate Trend",
                    markers=True
                )
                fig_trend.update_traces(line=dict(color='#10b981', width=3))
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No monthly trend data available")
        except Exception as e:
            st.info("Could not generate monthly trend chart")
    else:
        st.info("Due date column not available for trend analysis")
    
    # User Performance with safe user data
    st.subheader("👥 User Performance Ranking")
    
    if not users_df.empty and 'assigned_to' in tasks_df.columns:
        user_performance = []
        for _, user in users_df.iterrows():
            user_tasks = tasks_df[tasks_df['assigned_to'] == user['user_id']]
            if not user_tasks.empty:
                completed = len(user_tasks[user_tasks['status'] == 'Completed']) if 'status' in user_tasks.columns else 0
                total = len(user_tasks)
                
                # Calculate overdue tasks safely
                overdue = 0
                if 'due_date' in user_tasks.columns and 'status' in user_tasks.columns:
                    overdue = len(user_tasks[
                        (user_tasks['due_date'] < datetime.now()) & 
                        (user_tasks['status'].isin(['Open', 'In Progress']))
                    ])
                
                completion_rate = (completed / total * 100) if total > 0 else 0
                
                user_performance.append({
                    'User': user['name'],
                    'Total Tasks': total,
                    'Completed': completed,
                    'Completion Rate': completion_rate,
                    'Overdue': overdue
                })
        
        if user_performance:
            performance_df = pd.DataFrame(user_performance).sort_values('Completion Rate', ascending=False)
            st.dataframe(
                performance_df,
                use_container_width=True,
                column_config={
                    "User": "User",
                    "Total Tasks": st.column_config.NumberColumn("Total Tasks"),
                    "Completed": st.column_config.NumberColumn("Completed"),
                    "Completion Rate": st.column_config.ProgressColumn(
                        "Completion Rate",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100
                    ),
                    "Overdue": st.column_config.NumberColumn("Overdue Tasks")
                }
            )
        else:
            st.info("No user performance data available")
    else:
        st.info("User or assignment data not available for performance ranking")

def show_task_management():
    """Enhanced task management with full CRUD operations"""
    st.title("Task Management")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 All Tasks", "➕ Create Task", "✏️ Bulk Operations", "🚨 Escalations", "📊 Task Reports"])
    
    with tab1:
        show_all_tasks_admin()
    
    with tab2:
        show_create_task_form()
    
    with tab4:
        show_escalation_center()
    
    with tab5:
        show_task_reports()

def show_all_tasks_admin():
    """Show all tasks with advanced filtering and editing"""
    st.subheader("All Tasks")
    
    # Advanced filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox("Status", ["All", "Open", "In Progress", "Completed"])
    with col2:
        domains_df = get_domains()
        domain_options = ["All"] + domains_df['domain_name'].tolist()
        domain_filter = st.selectbox("Domain", domain_options)
    with col3:
        priority_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
    with col4:
        users_df = get_all_users()
        user_options = ["All"] + [f"{row['name']} ({row['email']})" for _, row in users_df.iterrows()]
        user_filter = st.selectbox("Assigned To", user_options)
    
    # Get and filter tasks
    tasks_df = get_tasks(role='admin')
    
    if not tasks_df.empty:
        filtered_df = tasks_df.copy()
        
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        if domain_filter != "All":
            filtered_df = filtered_df[filtered_df['domain'] == domain_filter]
        if priority_filter != "All":
            filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
        if user_filter != "All":
            filtered_df = filtered_df[filtered_df['assigned_name'] == user_filter.split(' (')[0]]
        
        st.markdown(f"**Showing {len(filtered_df)} of {len(tasks_df)} tasks**")
        
        for idx, row in filtered_df.iterrows():
            with st.expander(f"{row['title']} - {row['assigned_name']} ({row['status']}) - 💬{row.get('comment_count', 0)}", expanded=False):
                show_task_edit_form(row)
    else:
        st.info("No tasks available")

def show_task_edit_form(task):
    """Show form to edit task details with comments section"""
    with st.form(f"edit_task_{task['task_id']}"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_title = st.text_input("Task Title", value=task['title'], key=f"title_{task['task_id']}")
            new_description = st.text_area("Description", value=task['description'], height=100, key=f"desc_{task['task_id']}")
            
            domains_df = get_domains()
            domain_options = domains_df['domain_name'].tolist()
            current_domain_index = domain_options.index(task['domain']) if task['domain'] in domain_options else 0
            new_domain = st.selectbox("Domain", domain_options, index=current_domain_index, key=f"domain_{task['task_id']}")
        
        with col2:
            users_df = get_all_users()
            user_options = {f"{user_row['name']} ({user_row['email']})": user_row['user_id'] for _, user_row in users_df.iterrows()}
            current_user_key = f"{task['assigned_name']} ({task['assigned_email']})"
            user_keys = list(user_options.keys())
            current_user_index = user_keys.index(current_user_key) if current_user_key in user_keys else 0
            new_assigned = st.selectbox("Assign To", user_keys, index=current_user_index, key=f"assigned_{task['task_id']}")
            
            new_attachment = st.text_input("Attachment Link", 
                                         value=task['attachment'] if task['attachment'] and str(task['attachment']) != 'nan' else "",
                                         key=f"attach_{task['task_id']}")
            
            status_options = ["Open", "In Progress", "Completed"]
            current_status_index = status_options.index(task['status']) if task['status'] in status_options else 0
            new_status = st.selectbox("Status", status_options, index=current_status_index, key=f"status_{task['task_id']}")
            
            priority_options = ["High", "Medium", "Low"]
            current_priority = task.get('priority', 'Medium')
            current_priority_index = priority_options.index(current_priority) if current_priority in priority_options else 1
            new_priority = st.selectbox("Priority", priority_options, index=current_priority_index, key=f"priority_{task['task_id']}")
        
        col3, col4 = st.columns(2)
        with col3:
            current_due_date = task['due_date'].date() if pd.notna(task['due_date']) else date.today()
            new_due_date = st.date_input("Due Date", value=current_due_date, key=f"due_{task['task_id']}")
        with col4:
            frequency_options = ["Monthly", "Quarterly", "Yearly", "One-time"]
            current_freq_index = frequency_options.index(task['frequency']) if task['frequency'] in frequency_options else 0
            new_frequency = st.selectbox("Frequency", frequency_options, index=current_freq_index, key=f"freq_{task['task_id']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Update Task", use_container_width=True):
                if update_task(
                    task['task_id'], 
                    new_title, 
                    new_description, 
                    new_domain,
                    user_options[new_assigned],
                    new_attachment,
                    new_status,
                    new_due_date,
                    new_frequency,
                    new_priority,
                    st.session_state.user_id
                ):
                    st.success("✅ Task updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update task")
        
        with col2:
            if st.form_submit_button("🗑️ Delete Task", use_container_width=True, type="secondary"):
                if delete_task(task['task_id']):
                    st.success("✅ Task deleted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete task")
    
    # Comments section
    st.markdown("---")
    show_comment_section_in_task(task)
    
    # Task history
    st.markdown("---")
    st.subheader("📋 Task History")
    history_df = get_task_history(task['task_id'])
    if not history_df.empty:
        for _, history in history_df.iterrows():
            st.markdown(f"""
            <div style='background: #f8fafc; padding: 0.75rem; border-radius: 6px; margin: 0.5rem 0; border-left: 3px solid #667eea;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;'>
                    <strong style='color: #2d3748; font-size: 0.875rem;'>{history['field_name'].replace('_', ' ').title()}</strong>
                    <small style='color: #718096; font-size: 0.75rem;'>{history['changed_at']}</small>
                </div>
                <div style='color: #4a5568; font-size: 0.8125rem;'>
                    <span style='color: #e53e3e;'>From: {history['old_value']}</span> → 
                    <span style='color: #38a169;'>To: {history['new_value']}</span>
                </div>
                <div style='color: #718096; font-size: 0.75rem; margin-top: 0.25rem;'>
                    By: {history['changed_by_name']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No history available for this task")

def show_create_task_form():
    """Show form to create new task"""
    st.subheader("Create New Task")
    
    with st.form("create_task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Task Title", placeholder="Enter a clear and descriptive task title...")
            description = st.text_area("Description", placeholder="Describe the task in detail...", height=120)
            
            domains_df = get_domains()
            domain_options = domains_df['domain_name'].tolist()
            domain = st.selectbox("Domain", domain_options)
        
        with col2:
            users_df = get_all_users()
            user_options = {f"{row['name']} ({row['email']})": row['user_id'] for _, row in users_df.iterrows()}
            assigned = st.selectbox("Assign To", list(user_options.keys()))
            
            attachment = st.text_input("Attachment Link", placeholder="https://drive.google.com/... or https://sharepoint.com/...")
            
            status = st.selectbox("Status", ["Open", "In Progress"])
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        col3, col4 = st.columns(2)
        with col3:
            due_date = st.date_input("Due Date", min_value=date.today())
        with col4:
            frequency = st.selectbox("Frequency", ["One-time", "Monthly", "Quarterly", "Yearly"])
        
        submit = st.form_submit_button("🚀 Create Task", use_container_width=True)
        
        if submit:
            if title and description:
                if create_task(
                    title, description, domain, user_options[assigned], 
                    attachment, status, due_date, frequency, priority, st.session_state.user_id
                ):
                    st.success("🎉 Task created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to create task")
            else:
                st.error("⚠️ Title and Description are required")


def show_user_dashboard():
    """Show user dashboard for regular users"""
    with st.sidebar:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        '>
            <div style='width: 64px; height: 64px; background-color: rgba(255, 255, 255, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem; color: white; font-size: 1.5rem; font-weight: 700; backdrop-filter: blur(10px);'>
                {st.session_state.user_name[0].upper()}
            </div>
            <h3 style='color: white; margin: 0 0 0.25rem 0; font-size: 1.125rem;'>{st.session_state.user_name}</h3>
            <p style='color: rgba(255, 255, 255, 0.8); margin: 0; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Team Member</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='color: #e2e8f0; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;'>Navigation</div>", unsafe_allow_html=True)
        
        menu_options = {
            "📋 My Tasks": "mytasks",
            "📊 My Performance": "myperformance",
            "💬 My Comments": "mycomments"
        }
        
        menu = st.radio("", list(menu_options.keys()), label_visibility="collapsed")
        
        st.markdown("<hr style='border-color: #4a5568; margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        # Quick user stats
        tasks_df = get_tasks(st.session_state.user_id, 'user')
        if not tasks_df.empty:
            overdue_count = len(tasks_df[
                (tasks_df['due_date'] < datetime.now()) & 
                (tasks_df['status'].isin(['Open', 'In Progress']))
            ])
            st.markdown(f"""
            <div style='color: #e2e8f0; font-size: 0.75rem; margin-bottom: 1rem;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>My Tasks:</span>
                    <span style='font-weight: 600;'>{len(tasks_df)}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                    <span>Overdue:</span>
                    <span style='color: #fc8181; font-weight: 600;'>{overdue_count}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content based on menu selection
    menu_action = menu_options[menu]
    
    if menu_action == "mytasks":
        show_my_tasks()
    elif menu_action == "myperformance":
        show_my_performance()
    elif menu_action == "mycomments":
        show_my_comments()

def show_my_tasks():
    """Show tasks assigned to the current user with enhanced comment functionality"""
    st.title("📋 My Tasks")
    
    tasks_df = get_tasks(st.session_state.user_id, 'user')
    
    if tasks_df.empty:
        st.info("🎉 No tasks assigned to you currently!")
        return
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = len(tasks_df)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        completed_tasks = len(tasks_df[tasks_df['status'] == 'Completed'])
        st.metric("Completed", completed_tasks)
    
    with col3:
        in_progress_tasks = len(tasks_df[tasks_df['status'].isin(['Open', 'In Progress', 'Pending'])])
        st.metric("In Progress", in_progress_tasks)
    
    with col4:
        overdue_tasks = len(tasks_df[
            (tasks_df['due_date'] < datetime.now()) & 
            (tasks_df['status'].isin(['Open', 'In Progress', 'Pending']))
        ])
        st.metric("Overdue", overdue_tasks)
    
    st.markdown("---")
    
    # Task filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Pending", "Completed"])
    
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    
    with col3:
        domain_filter = st.selectbox("Filter by Domain", ["All"] + tasks_df['domain'].unique().tolist())
    
    # Apply filters
    filtered_tasks = tasks_df.copy()
    
    if status_filter != "All":
        filtered_tasks = filtered_tasks[filtered_tasks['status'] == status_filter]
    if priority_filter != "All":
        filtered_tasks = filtered_tasks[filtered_tasks['priority'] == priority_filter]
    if domain_filter != "All":
        filtered_tasks = filtered_tasks[filtered_tasks['domain'] == domain_filter]
    
    st.markdown(f"**Showing {len(filtered_tasks)} of {len(tasks_df)} tasks**")
    
    # Display tasks
    for idx, task in filtered_tasks.iterrows():
        create_task_card(task)
        
        # Quick actions
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("💬 View Comments", key=f"view_comments_{task['task_id']}", use_container_width=True):
                st.session_state.viewing_task_id = task['task_id']
                st.session_state.viewing_task_title = task['title']
                st.rerun()
        
        with col2:
            if st.button("💬 Quick Comment", key=f"quick_comment_{task['task_id']}", use_container_width=True):
                st.session_state.quick_comment_task_id = task['task_id']
                st.rerun()
        
        with col3:
            current_status = task['status']
            # Map "Pending" to "In Progress" for the status dropdown
            display_status = "In Progress" if current_status == "Pending" else current_status
            status_options = ["Open", "In Progress", "Completed"]
            
            # Find the current index, default to 0 if not found
            try:
                current_index = status_options.index(display_status)
            except ValueError:
                current_index = 0  # Default to "Open" if status not found
            
            new_status = st.selectbox(
                "Update Status",
                status_options,
                index=current_index,
                key=f"status_{task['task_id']}"
            )
            
            # Map back "In Progress" to "Pending" if needed for database
            db_status = "Pending" if new_status == "In Progress" else new_status
            
            if db_status != current_status:
                update_task_status_with_notification(
                    task['task_id'], 
                    db_status, 
                    current_status,
                    st.session_state.user_name
                )
                st.success("Status updated!")
                st.rerun()
        
        st.markdown("---")
    
    # Handle comment viewing
    if hasattr(st.session_state, 'viewing_task_id'):
        st.markdown("---")
        st.subheader(f"💬 Comments for: {st.session_state.viewing_task_title}")
        show_task_comments(st.session_state.viewing_task_id)
        
        if st.button("← Back to Tasks", key="back_to_tasks"):
            if hasattr(st.session_state, 'viewing_task_id'):
                del st.session_state.viewing_task_id
            if hasattr(st.session_state, 'viewing_task_title'):
                del st.session_state.viewing_task_title
            st.rerun()
    
    # Handle quick comment
    if hasattr(st.session_state, 'quick_comment_task_id'):
        task = get_task_by_id(st.session_state.quick_comment_task_id)
        if task:
            st.markdown("---")
            st.subheader(f"💭 Quick Comment: {task['title']}")
            
            with st.form(key=f"quick_comment_form_{task['task_id']}"):
                quick_comment = st.text_area(
                    "Your comment",
                    placeholder="Type your quick comment here...",
                    height=80,
                    key=f"quick_comment_text_{task['task_id']}"
                )
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    submit_quick = st.form_submit_button("💬 Post Comment", use_container_width=True)
                with col2:
                    cancel_quick = st.form_submit_button("❌ Cancel", use_container_width=True, type="secondary")
                
                if submit_quick and quick_comment.strip():
                    if add_comment(st.session_state.quick_comment_task_id, st.session_state.user_id, quick_comment.strip()):
                        st.success("✅ Comment added successfully!")
                        del st.session_state.quick_comment_task_id
                        st.rerun()
                    else:
                        st.error("❌ Failed to add comment")
                elif cancel_quick:
                    del st.session_state.quick_comment_task_id
                    st.rerun()

def show_my_performance():
    """Show personal performance metrics for the user"""
    st.title("📊 My Performance")
    
    tasks_df = get_tasks(st.session_state.user_id, 'user')
    
    if tasks_df.empty:
        st.info("No task data available for performance analysis.")
        return
    
    # Personal metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = len(tasks_df)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        completed_tasks = len(tasks_df[tasks_df['status'] == 'Completed'])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col3:
        overdue_tasks = len(tasks_df[
            (tasks_df['due_date'] < datetime.now()) & 
            (tasks_df['status'].isin(['Open', 'In Progress']))
        ])
        st.metric("Overdue Tasks", overdue_tasks)
    
    with col4:
        avg_completion_time = calculate_avg_completion_time(tasks_df)
        st.metric("Avg Completion Time", avg_completion_time)
    
    st.markdown("---")
    
    # Personal charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_counts = tasks_df['status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="My Task Status Distribution"
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Domain distribution
        domain_counts = tasks_df['domain'].value_counts()
        fig_domain = px.bar(
            x=domain_counts.index,
            y=domain_counts.values,
            title="My Tasks by Domain"
        )
        st.plotly_chart(fig_domain, use_container_width=True)

def show_my_comments():
    """Show comments made by the current user"""
    st.title("💬 My Comments")
    
    # This would require additional database function to get user's comments
    st.info("🔧 Comment history feature coming soon!")

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="TaskFlow Pro - Enterprise Task Management",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styling
    set_page_styling()
    
    # Initialize database
    init_database()
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    
    # Show appropriate interface based on login status
    if not st.session_state.logged_in:
        show_login()
    else:
        if st.session_state.user_role == 'admin':
            show_admin_dashboard()
        else:
            show_user_dashboard()

if __name__ == "__main__":
    main()









# ... (Keep all the existing functions like show_login, show_domain_management, etc. from your previous code)
# The rest of your existing functions remain the same...




# ... (Keep all other existing functions the same)


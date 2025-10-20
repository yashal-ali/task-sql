# domain_operations.py
"""
Domain management operations and functions
"""

import pandas as pd
from database_connection import get_db_connection
import streamlit as st

def get_domains():
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

def add_domain(domain_name: str, mancom_member_name: str, mancom_member_email: str):
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
        
        # Insert new domain
        cursor.execute("""
            INSERT INTO domains (domain_name, mancom_member_name, mancom_member_email, is_active)
            VALUES (?, ?, ?, 1)
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


def delete_domain(domain_id: int):
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
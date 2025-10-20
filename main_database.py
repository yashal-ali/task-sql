

import streamlit as st
from database_connection import get_db_connection
from database_schema import create_all_tables, update_database_schema
from user_operations import PasswordHasher

def init_database():
    """Initialize database schema with proper enterprise structure"""
    conn = get_db_connection()
    if conn is None:
        st.error("❌ Cannot initialize database - no connection")
        return
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Create all tables
        create_all_tables()
        
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
    
    # Update schema for existing databases
    update_database_schema()
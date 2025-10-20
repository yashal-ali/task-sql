import pyodbc
import streamlit as st
from database_connection import get_db_connection

def create_users_table(cursor):
    """Create users table with auth_method column"""
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

def create_domains_table(cursor):
    """Create domains table"""
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

def create_tasks_table(cursor):
    """Create tasks table with proper enums and JSON comments"""
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

def create_task_history_table(cursor):
    """Create task_history table for audit trail"""
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

def create_indexes(cursor):
    """Create performance indexes"""
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

def create_all_tables():
    """Create all database tables"""
    conn = get_db_connection()
    if conn is None:
        st.error("❌ Cannot create tables - no connection")
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Create tables in order of dependencies
        create_users_table(cursor)
        create_domains_table(cursor)
        create_tasks_table(cursor)
        create_task_history_table(cursor)
        create_indexes(cursor)
        
        conn.commit()
        print("✅ All database tables created successfully!")
        return True
        
    except Exception as e:
        st.error(f"Error creating tables: {str(e)}")
        print(f"Table creation error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()

def update_database_schema():
    """Update database schema to add missing columns"""
    conn = get_db_connection()
    if conn is None:
        st.error("❌ Cannot update database schema - no connection")
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Check if auth_method column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'auth_method'
        """)
        auth_method_exists = cursor.fetchone()[0] > 0
        
        if not auth_method_exists:
            # Add auth_method column
            cursor.execute("""
                ALTER TABLE users 
                ADD auth_method NVARCHAR(20) DEFAULT 'traditional'
            """)
            print("✅ Added auth_method column to users table")
        
        # Update existing users to have 'traditional' as default auth_method
        cursor.execute("""
            UPDATE users 
            SET auth_method = 'traditional' 
            WHERE auth_method IS NULL
        """)
        
        conn.commit()
        print("✅ Database schema updated successfully!")
        return True
        
    except Exception as e:
        st.error(f"Error updating database schema: {str(e)}")
        print(f"Schema update error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
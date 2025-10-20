import pandas as pd
from datetime import datetime
from database_connection import get_db_connection
import streamlit as st
import hashlib
import secrets
import pyodbc

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
def authenticate_user(email: str, password: str):
    """Authenticate user by email and return user data if successful"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        # First, check if auth_method column exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'auth_method'
        """)
        auth_method_exists = cursor.fetchone()[0] > 0
        
        if auth_method_exists:
            query = """
                SELECT user_id, username, email, password_hash, role, is_active, auth_method
                FROM users 
                WHERE email = ? AND is_active = 1
            """
        else:
            query = """
                SELECT user_id, username, email, password_hash, role, is_active, 'traditional' as auth_method
                FROM users 
                WHERE email = ? AND is_active = 1
            """
        
        df = pd.read_sql(query, conn, params=(email,))
        
        if df.empty:
            return None
            
        user = df.iloc[0].to_dict()
        
        if PasswordHasher.verify_password(password, user['password_hash']):
            # Update last login
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

def get_user_by_email(email: str):
    """Get user by email (for Microsoft auth)"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        query = """
            SELECT user_id, username, email, password_hash, role, is_active, auth_method
            FROM users 
            WHERE email = ? AND is_active = 1
        """
        df = pd.read_sql(query, conn, params=(email,))
        
        if df.empty:
            return None
            
        user = df.iloc[0].to_dict()
        # Remove password hash from returned user data
        del user['password_hash']
        return user
        
    except Exception as e:
        print(f"Error fetching user by email: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def create_user(username: str, email: str, password: str, role: str = 'user', auth_method: str = 'traditional'):
    """Create a new user with hashed password"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    try:
        hashed_password = PasswordHasher.hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, auth_method)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, hashed_password, role, auth_method))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def get_all_users():
    """Get all users (without password hashes)"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
            SELECT user_id, username, email, role, auth_method, is_active, created_at, last_login
            FROM users 
            ORDER BY username
        """
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error fetching users: {str(e)}")
        return pd.DataFrame()

def update_user(user_id: int, username: str, email: str, role: str, is_active: bool):
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

def delete_user(user_id: int):
    """Delete a user"""
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
        
        # Simply delete the user
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

def get_admin_users():
    """Get all admin users"""
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
            required_columns = ['user_id', 'username', 'email', 'role']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            return df[required_columns]
        else:
            return pd.DataFrame(columns=required_columns)
            
    except Exception as e:
        st.error(f"Error fetching admin users: {str(e)}")
        return pd.DataFrame(columns=['user_id', 'username', 'email', 'role'])
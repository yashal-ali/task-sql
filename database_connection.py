import pyodbc
import streamlit as st

@st.cache_resource
def get_db_connection():
    """Creates a MSSQL connection using Streamlit secrets or local config."""
    try:
        drivers = pyodbc.drivers()
        print("Available drivers:", drivers)
        
        for driver in drivers:
            try:
                print(f"Testing driver: {driver}")
                conn = pyodbc.connect(
                    f"DRIVER={{{driver}}};"
                    "SERVER=localhost,1433;"
                    "DATABASE=Task_flo_Database;"
                    "UID=sa;"
                    "PWD=Yashal309;"
                    "Encrypt=yes;"
                    "TrustServerCertificate=yes;"
                )
                print(f"✅ SUCCESS with driver: {driver}")
                return conn
            except Exception as driver_error:
                print(f"❌ Failed with {driver}: {driver_error}")
                continue
        
        st.error("❌ All ODBC drivers failed to connect")
        return None
        
    except Exception as e:
        st.error(f"Failed to connect to SQL Server: {str(e)}")
        return None

def test_connection():
    """Test database connection"""
    conn = get_db_connection()
    if conn:
        print("✅ Database connection successful")
        conn.close()
        return True
    else:
        print("❌ Database connection failed")
        return False
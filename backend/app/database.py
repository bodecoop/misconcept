import oracledb
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Oracle Autonomous Database TCPS connection string (no wallet required)
# This is the working connection string from test_connection.py
CONNECTION_STRING = '''(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.us-chicago-1.oraclecloud.com))(connect_data=(service_name=g02527d20960581_uexulb26uojc2pyx_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'''

# Set fetch_lobs to False for better performance
oracledb.defaults.fetch_lobs = False

# Create connection pool using TCPS (SSL/TLS) - no wallet needed
pool = None
try:
    pool = oracledb.create_pool(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=CONNECTION_STRING,
        min=2,
        max=10,
        increment=1
    )
    print("✅ Oracle connection pool created successfully (TCPS direct connection)")
except Exception as e:
    print(f"❌ Failed to create Oracle connection pool: {e}")
    print("Make sure DB_USER and DB_PASSWORD are set in .env file")
    pool = None

@contextmanager
def get_connection():
    """
    Context manager for Oracle database connections.
    Automatically handles connection acquisition and release.
    """
    if pool is None:
        raise Exception("Database connection pool not available. Check your connection string and credentials.")

    connection = None
    try:
        connection = pool.acquire()
        yield connection
    except oracledb.Error as e:
        if connection:
            connection.rollback()
        raise Exception(f"Database error: {e}")
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            try:
                connection.close()
            except:
                pass  # Connection might already be closed

# Keep SQLAlchemy Base for model definitions (if needed)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

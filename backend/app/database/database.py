# database.py
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, JSON, TIMESTAMP, MetaData, Table, VARCHAR
from sqlalchemy.orm import sessionmaker
import datetime
import psycopg2
import socket
import socks
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_HOST = "pg-298e7c66-senthilnaveen003-3105.k.aivencloud.com"
DB_PORT = 26260
DB_NAME = "defaultdb"
DB_USER = "avnadmin"
DB_PASSWORD = "AVNS_d4bV5orCyjUIYKdkJiQ"

# SOCKS proxy configuration
SOCKS_PROXY_HOST = "socks-proxy.scss.tcd.ie"
SOCKS_PROXY_PORT = 1080


# Function to detect if we need to use the proxy
def is_college_environment():
    """Check if we're in the college environment that needs a proxy"""
    try:
        # Try to connect directly to the database
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)  # 2 second timeout
        result = s.connect_ex((DB_HOST, DB_PORT))
        s.close()

        # If we can connect directly, we don't need the proxy
        if result == 0:
            return False
        return True
    except:
        # If any error, assume we need the proxy
        return True


# Define a function to create a connection with proxy if needed
def create_psycopg2_connection():
    """Create a connection to PostgreSQL with or without proxy as needed"""
    if is_college_environment():
        # Set up SOCKS proxy for this connection
        print(f"Using SOCKS proxy at {SOCKS_PROXY_HOST}:{SOCKS_PROXY_PORT}")

        # Create a proxy-aware socket
        socks_socket = socks.socksocket()
        socks_socket.set_proxy(socks.PROXY_TYPE_SOCKS5, SOCKS_PROXY_HOST, SOCKS_PROXY_PORT)
        socks_socket.connect((DB_HOST, DB_PORT))

        # Use the socket for the connection
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            sslmode='require',
        )
        return connection
    else:
        # No proxy needed
        print("Connecting directly to database without proxy")
        return psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            sslmode='require',
        )


# Monkey patch psycopg2's connect function
original_connect = psycopg2.connect


def patched_connect(*args, **kwargs):
    """Patched connect function that uses proxy when needed"""
    if is_college_environment():
        # If args are used, extract connection params
        if args and isinstance(args[0], str):
            # Parse connection string
            params = urlparse(args[0])
            if params.hostname:
                # Set up SOCKS proxy
                socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, SOCKS_PROXY_HOST, SOCKS_PROXY_PORT)
                socket.socket = socks.socksocket
                # Continue with original connection
                return original_connect(*args, **kwargs)

        # If kwargs are used
        if 'host' in kwargs or 'dsn' in kwargs:
            # Set up SOCKS proxy
            socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, SOCKS_PROXY_HOST, SOCKS_PROXY_PORT)
            socket.socket = socks.socksocket
            # Continue with original connection
            return original_connect(*args, **kwargs)

    # No proxy needed or couldn't determine if needed
    return original_connect(*args, **kwargs)


# Override psycopg2's connect function with our patched version
psycopg2.connect = patched_connect

# Database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
print(f"Database URL: {DATABASE_URL}")

# Create Engine
engine = create_engine(DATABASE_URL, echo=True)

# Define Metadata
metadata = MetaData()

# Define Table Schema
response_data = Table(
    "response_data",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", VARCHAR(20), nullable=True),
    Column("filename", VARCHAR(100), nullable=True),
    Column("timestamp", TIMESTAMP, default=datetime.datetime.utcnow),
    Column("code", JSON, nullable=False),
    Column("report_response", JSON, nullable=False),
)

# Create Session Factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Function to Initialize DB and Create Table
def init_db():
    print("Initializing database...")
    try:
        # Reset socket to original state in case it was patched
        orig_socket = socket.socket
        # Set up SOCKS proxy if needed
        if is_college_environment():
            print("College environment detected, Setting up proxy")
            socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, SOCKS_PROXY_HOST, SOCKS_PROXY_PORT)
            socket.socket = socks.socksocket
        else:
            print("No Proxy set")

        # Create tables
        with engine.connect() as conn:
            metadata.create_all(engine)
            print("Database initialized successfully. Table 'response_data' is ready.")

        # Reset socket
        socket.socket = orig_socket
    except Exception as e:
        print(f"Error initializing database: {e}")
        # Reset socket
        socket.socket = orig_socket
        raise


# Get DB function
def get_db():
    print("Database session requested")
    # Set up proxy if needed
    orig_socket = socket.socket
    if is_college_environment():
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, SOCKS_PROXY_HOST, SOCKS_PROXY_PORT)
        socket.socket = socks.socksocket

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Reset socket to original
        socket.socket = orig_socket
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, JSON, TIMESTAMP, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Load environment variables from .env file
load_dotenv()

# Retrieve DB credentials from .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")  # Default to 5432 if not specified
DB_NAME = os.getenv("DB_NAME")

# Construct the DATABASE_URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create Engine
engine = create_engine(DATABASE_URL, echo=True)

# Define Metadata
metadata = MetaData()

# Define Table Schema
response_data = Table(
    "response_data",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", TIMESTAMP, default=datetime.datetime.utcnow),
    Column("code", JSON, nullable=False),
    Column("report_response", JSON, nullable=False),
)

# Create Session Factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Function to Initialize DB and Create Table
def init_db():
    with engine.connect() as conn:
        metadata.create_all(engine)  # Creates table if it does not exist


# Move get_db function here
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
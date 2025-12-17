from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for simplicity and Windows compatibility
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./student_ai.db")

# check_same_thread=False is needed for SQLite with FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)

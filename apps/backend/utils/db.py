from decimal import ROUND_DOWN, Decimal
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, validator
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()    

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String)
    image = Column(String)
    email = Column(String, unique=True, index=True)
    github_id = Column(String, unique=True, index=True, nullable=True)
    stripe_customer_id = Column(String, unique=True, nullable=True)  
    api_keys = relationship("ApiKey", back_populates="user")

    # unused for now
    password_hash = Column(String, nullable=True)  # Only required for Credentials provider
    
    # Add any other necessary columns for user data
    
    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"

class ApiKey(Base):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="api_keys")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection(engine):
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"Database connection successful. Result: {result.scalar()}")
    except OperationalError:
        print("Failed to connect to the database.")

if __name__ == "__main__":
  # Test the connection
  test_connection(engine)
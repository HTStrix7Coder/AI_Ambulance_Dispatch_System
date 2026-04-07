from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This URL needs to be configured with your MySQL credentials
# Using pymysql instead of mysqlconnector for better MySQL 8.0+ compatibility
DATABASE_URL = "mysql+pymysql://hari:1234@localhost/medicalsystem"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This is a new function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
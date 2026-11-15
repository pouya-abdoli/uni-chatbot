import os
from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from a .env file (e.g., DB_URL)
load_dotenv()

# Create the SQLAlchemy engine. Falls back to a local SQLite file if DB_URL isn't set.
engine = create_engine(os.getenv("DB_URL", "sqlite:///./uni.db"))

# Factory for creating database sessions. Each call returns a new Session bound to the engine.
SessionLocal = sessionmaker(bind=engine)

# Base class that all ORM models inherit from; collects table metadata.
Base = declarative_base()

class Course(Base):
    """Represents a university course offered in a given semester."""
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    description = Column(String)


class Instructor(Base):
    """Represents a person who teaches one or more courses."""
    __tablename__ = "instructors"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class CourseInstructor(Base):
    """Association table linking courses to instructors (many-to-many relationship)."""
    __tablename__ = "course_instructors"
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    instructor_id = Column(Integer, ForeignKey("instructors.id"), primary_key=True)

class CourseRequirement(Base):        
    """
    Defines prerequisite/co-requisite relationships between courses.
    `type` indicates the kind of relationship (e.g., "prerequisite", "corequisite").
    """
    __tablename__ = "course_requirements"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    related_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    type = Column(String, nullable=False)
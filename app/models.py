from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))

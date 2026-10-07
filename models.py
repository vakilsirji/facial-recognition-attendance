from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    emp_id = Column(String, unique=True, index=True)
    photo_path = Column(String)  # Path to the reference photo for face recognition

    attendance_logs = relationship("Attendance", back_populates="employee")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String) # e.g. "Present"
    
    employee = relationship("Employee", back_populates="attendance_logs")

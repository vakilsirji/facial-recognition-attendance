from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class EmployeeBase(BaseModel):
    name: str
    emp_id: str

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    photo_path: str

    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    status: str

class AttendanceCreate(AttendanceBase):
    employee_id: int

class Attendance(AttendanceBase):
    id: int
    employee_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

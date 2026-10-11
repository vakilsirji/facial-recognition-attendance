from pydantic import BaseModel, field_serializer
from datetime import datetime, timezone, timedelta
from typing import List, Optional

IST = timezone(timedelta(hours=5, minutes=30))

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

    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime, _info):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=IST).isoformat()
        return dt.astimezone(IST).isoformat()

    class Config:
        from_attributes = True

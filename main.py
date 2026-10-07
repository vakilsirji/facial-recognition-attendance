from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import uuid

import models, schemas
from database import SessionLocal, engine, get_db
from recognizer import process_group_attendance

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Facial Recognition Attendance System")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    with open("admin.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/add_employee", response_class=HTMLResponse)
async def add_employee_page():
    with open("register.html", "r", encoding="utf-8") as f:
        return f.read()


# Create a directory to store employee photos
UPLOAD_DIR = "employee_photos"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/employee_photos", StaticFiles(directory=UPLOAD_DIR), name="employee_photos")
    
TEMP_DIR = "temp_scans"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@app.post("/register/", response_model=schemas.Employee)
async def register_employee(
    name: str = Form(...),
    emp_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check if employee exists
    db_employee = db.query(models.Employee).filter(models.Employee.emp_id == emp_id).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Employee ID already registered")
        
    # Save the file
    file_extension = file.filename.split('.')[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Create employee record
    db_employee = models.Employee(name=name, emp_id=emp_id, photo_path=file_path)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    # Delete DeepFace cache files so the new employee is recognized
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith('.pkl'):
            try:
                os.remove(os.path.join(UPLOAD_DIR, f))
            except Exception:
                pass
                
    return db_employee

@app.post("/mark_attendance/")
async def mark_attendance(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint for CCTV/Mobile to upload a classroom image.
    The system will detect all faces and mark attendance for everyone matched.
    """
    # Save temp file
    file_extension = file.filename.split('.')[-1]
    temp_file_name = f"temp_{uuid.uuid4()}.{file_extension}"
    temp_file_path = os.path.join(TEMP_DIR, temp_file_name)
    
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # OPTIMIZATION: Resize the huge mobile phone photo to make CPU processing much faster
    import cv2
    img = cv2.imread(temp_file_path)
    if img is not None:
        # Resize to max width of 800px while maintaining aspect ratio
        height, width = img.shape[:2]
        if width > 800:
            new_height = int(height * (800 / width))
            img = cv2.resize(img, (800, new_height))
            cv2.imwrite(temp_file_path, img)
            
    # Get all matched employee filenames from the group photo
    matched_filenames = process_group_attendance(temp_file_path, UPLOAD_DIR)
    
    # Clean up temp file
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
        
    if not matched_filenames:
        raise HTTPException(status_code=404, detail="No registered employees recognized in the photo.")
        
    # Mark attendance for all matched employees
    present_employees = []
    
    for filename in matched_filenames:
        # Find employee by photo filename
        db_employee = db.query(models.Employee).filter(models.Employee.photo_path.endswith(filename)).first()
        if db_employee:
            attendance = models.Attendance(employee_id=db_employee.id, status="Present")
            db.add(attendance)
            present_employees.append(db_employee.name)
            
    db.commit()
    
    return {
        "message": "Attendance marked successfully",
        "count": len(present_employees),
        "present_employees": present_employees
    }

@app.get("/employees/", response_model=List[schemas.Employee])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees = db.query(models.Employee).offset(skip).limit(limit).all()
    return employees

@app.get("/attendance/", response_model=List[schemas.Attendance])
def read_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    attendance = db.query(models.Attendance).offset(skip).limit(limit).all()
    return attendance

# Facial Recognition Attendance System

This is a FastAPI-based backend for a facial recognition attendance system. It allows registering employees with a reference photo and marking attendance by matching uploaded photos (e.g., from CCTV or mobile devices).

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Endpoints

- **Swagger UI (Interactive API documentation)**: `http://localhost:8000/docs`

- `POST /register/`: Register a new employee with a name, employee ID, and photo.
- `POST /mark_attendance/`: Upload a photo (from CCTV/mobile) to recognize the face and mark attendance.
- `GET /employees/`: List all registered employees.
- `GET /attendance/`: List all attendance logs.

## Technologies Used

- **FastAPI**: Backend web framework.
- **DeepFace**: Robust facial recognition framework.
- **SQLAlchemy & SQLite**: Database for storing employees and attendance logs.

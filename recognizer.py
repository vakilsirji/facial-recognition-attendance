from deepface import DeepFace
import cv2
import os
import pandas as pd

def process_group_attendance(group_img_path, db_path="employee_photos"):
    """
    Detects all faces in a group photo and compares them against all images in the db_path.
    Returns a list of matched employee photo filenames.
    """
    try:
        # DeepFace.find detects all faces in the image and matches them against the db
        results = DeepFace.find(
            img_path=group_img_path,
            db_path=db_path,
            model_name="Facenet",          # Facenet is much faster than VGG-Face
            detector_backend="mtcnn",      # MTCNN is much faster on CPUs than retinaface
            enforce_detection=False
        )
        
        matched_filenames = []
        
        # Results is a list of Pandas DataFrames (one per detected face)
        for df in results:
            if not df.empty:
                # Get the best match identity path (e.g. employee_photos/c5df...PNG)
                identity_path = df.iloc[0]['identity']
                filename = os.path.basename(identity_path)
                matched_filenames.append(filename)
                
        return list(set(matched_filenames)) # Return unique matches
        
    except Exception as e:
        print(f"Error in group face recognition: {e}")
        return []




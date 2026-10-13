from deepface import DeepFace
import cv2
import os
import gc

# Use lightweight model + fast detector for low-memory devices
MODEL_NAME = "Facenet"
DETECTOR = "ssd"             # better accuracy than opencv, lighter than mtcnn
DISTANCE_METRIC = "cosine"
MAX_IMG_WIDTH = 640          # aggressive downscale before recognition


def _downscale(img_path, max_width=MAX_IMG_WIDTH):
    """Downscale image in-place to reduce memory during recognition."""
    img = cv2.imread(img_path)
    if img is None:
        return
    h, w = img.shape[:2]
    if w > max_width:
        new_h = int(h * (max_width / w))
        img = cv2.resize(img, (max_width, new_h), interpolation=cv2.INTER_AREA)
        cv2.imwrite(img_path, img, [cv2.IMWRITE_JPEG_QUALITY, 80])
    del img


def process_group_attendance(group_img_path, db_path="employee_photos"):
    """
    Detects all faces in a group photo and compares them against the db_path.
    Returns a list of matched employee photo filenames.
    Optimized for low-memory mobile environments.
    """
    # Downscale before any processing
    _downscale(group_img_path)

    try:
        results = DeepFace.find(
            img_path=group_img_path,
            db_path=db_path,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR,
            distance_metric=DISTANCE_METRIC,
            enforce_detection=False,
            silent=True,
            normalization="base",
        )

        print(f"[RECOGNITION] Faces detected in scan: {len(results)}")
        matched_filenames = []

        # Results is a list of DataFrames (one per detected face)
        for i, df in enumerate(results):
            print(f"[RECOGNITION] Face {i+1}: {len(df)} candidates in DB")
            if not df.empty:
                best_row = df.iloc[0]
                dist = best_row.get("distance", 999)
                threshold = best_row.get("threshold", 0.4)
                identity_path = best_row["identity"]
                filename = os.path.basename(identity_path)
                print(f"[RECOGNITION] Face {i+1}: best={filename} dist={dist:.4f} threshold={threshold}")
                matched_filenames.append(filename)
            else:
                print(f"[RECOGNITION] Face {i+1}: NO match above threshold")

        print(f"[RECOGNITION] Final matched: {matched_filenames}")
        return list(set(matched_filenames))

    except Exception as e:
        print(f"[RECOGNITION ERROR] {e}")
        return []

    finally:
        # Explicitly free memory after heavy DeepFace work
        gc.collect()

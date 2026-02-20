import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from typing import List
from datetime import date
from ..database import get_connection
from ..schemas.lecture import Lecture as LectureSchema, LectureCreate, LectureLabel, LectureFile
from ..config import config
from pypdf import PdfReader

router = APIRouter()

# Default user ID for proof of concept
DEFAULT_USER_ID = 1

# Get lectures for a specific class
@router.get("/by_class/{class_id}", response_model=List[LectureSchema])
def get_lectures_by_class(class_id: int):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM lectures WHERE class_id = :class_id ORDER BY created_at DESC", {"class_id": class_id})
            lecture_ids = [row[0] for row in cursor.fetchall()]
            lectures = []
            for lecture_id in lecture_ids:
                lecture_data = get_lecture_data(cursor, lecture_id)
                if lecture_data:
                    lectures.append(lecture_data)
            return lectures
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve lectures for class: {str(e)}")

# Delete a single lecture and its files/labels
@router.delete("/{lecture_id}", status_code=204)
def delete_lecture(lecture_id: int):
    """Delete a single lecture and its associated files and labels."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Delete lecture_labels for this lecture
            cursor.execute("DELETE FROM lecture_labels WHERE lecture_id = :lecture_id", {"lecture_id": lecture_id})
            # Delete lecture_files for this lecture
            cursor.execute("DELETE FROM lecture_files WHERE lecture_id = :lecture_id", {"lecture_id": lecture_id})
            # Delete the lecture itself
            cursor.execute("DELETE FROM lectures WHERE id = :lecture_id", {"lecture_id": lecture_id})
            conn.commit()
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete lecture: {str(e)}")

def validate_file_type(file: UploadFile, allowed_types: List[str]):
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}")

def get_lecture_data(cursor, lecture_id):
    """Helper function to get complete lecture data with files and labels"""
    # Get lecture basic info
    cursor.execute("""
        SELECT id, class_id, lecture_title, lecture_date, created_at
        FROM lectures
        WHERE id = :lecture_id
    """, {"lecture_id": lecture_id})

    lecture_data = cursor.fetchone()
    if not lecture_data:
        return None

    # Get files
    cursor.execute("""
        SELECT id, file_type, pdf_text, uploaded_at
        FROM lecture_files
        WHERE lecture_id = :lecture_id
    """, {"lecture_id": lecture_id})

    files_data = cursor.fetchall()
    files = [LectureFile(
        id=f[0], file_type=f[1], pdf_text=f[2], uploaded_at=f[3]
    ) for f in files_data]

    # Get labels
    cursor.execute("""
        SELECT l.id, l.label_name, ll.lecture_id
        FROM labels l
        JOIN lecture_labels ll ON l.id = ll.label_id
        WHERE ll.lecture_id = :lecture_id
    """, {"lecture_id": lecture_id})

    labels_data = cursor.fetchall()
    labels = [LectureLabel(
        id=l[0], label_name=l[1], lecture_id=l[2]
    ) for l in labels_data]

    return LectureSchema(
        id=lecture_data[0],
        class_id=lecture_data[1],
        lecture_title=lecture_data[2],
        lecture_date=lecture_data[3],
        created_at=lecture_data[4],
        files=files,
        labels=labels
    )

@router.post("/upload", response_model=LectureSchema)
async def upload_lecture(
    pdf_file: UploadFile = File(None),
    transcript_file: UploadFile = File(None),
    class_id: int = Form(...),
    lecture_title: str = Form(...),
    lecture_date: date = Form(...),
    labels: str = Form(""),  # Comma-separated labels
):
    # Validate files
    if pdf_file:
        validate_file_type(pdf_file, ["application/pdf"])
    if transcript_file:
        validate_file_type(transcript_file, ["text/plain"])

    # Parse labels
    label_list = [label.strip() for label in labels.split(",") if label.strip()]

    # Create upload directory if it doesn't exist
    os.makedirs(config.UPLOAD_DIR, exist_ok=True) # type: ignore

    pdf_path = None
    transcript_path = None

    try:
        # Save PDF file
        if pdf_file:
            pdf_filename = f"{DEFAULT_USER_ID}_{pdf_file.filename}"
            pdf_path = os.path.join(config.UPLOAD_DIR, pdf_filename) # type: ignore
            with open(pdf_path, "wb") as buffer:
                shutil.copyfileobj(pdf_file.file, buffer)

        # Save transcript file
        if transcript_file:
            transcript_filename = f"{DEFAULT_USER_ID}_{transcript_file.filename}"
            transcript_path = os.path.join(config.UPLOAD_DIR, transcript_filename) # type: ignore
            with open(transcript_path, "wb") as buffer:
                shutil.copyfileobj(transcript_file.file, buffer)

        with get_connection() as conn:
            cursor = conn.cursor()

            # Create lecture record
            cursor.execute("""
                INSERT INTO lectures (class_id, lecture_title, lecture_date)
                VALUES (:class_id, :lecture_title, :lecture_date)
            """, {
                "class_id": class_id,
                "lecture_title": lecture_title,
                "lecture_date": lecture_date
            })

            # Get the inserted lecture data
            cursor.execute("""
                SELECT id, class_id, lecture_title, lecture_date, created_at
                FROM lectures
                WHERE class_id = :class_id AND lecture_title = :lecture_title
                ORDER BY created_at DESC
                FETCH FIRST 1 ROW ONLY
            """, {
                "class_id": class_id,
                "lecture_title": lecture_title
            })

            lecture_data = cursor.fetchone()
            if not lecture_data:
                raise HTTPException(status_code=500, detail="Failed to create lecture")

            lecture_id = lecture_data[0]

            # Insert files
            if pdf_path:
                reader = PdfReader(pdf_path)
                text = ""

                for page in reader.pages:
                    text += page.extract_text()
                
                cursor.execute("""
                    INSERT INTO lecture_files (lecture_id, file_type, pdf_text)
                    VALUES (:lecture_id, :file_type, :pdf_text)
                """, {
                    "lecture_id": lecture_id,
                    "file_type": "pdf",
                    "pdf_text": text
                })

            if transcript_path:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    text = f.read()
                cursor.execute("""
                    INSERT INTO lecture_files (lecture_id, file_type, pdf_text)
                    VALUES (:lecture_id, :file_type, :pdf_text)
                """, {
                    "lecture_id": lecture_id,
                    "file_type": "transcript",
                    "pdf_text": text
                })

            # Handle labels
            for label in label_list:
                # Insert label if it doesn't exist (Oracle syntax for upsert)
                try:
                    cursor.execute("""
                        INSERT INTO labels (label_name)
                        VALUES (:label_name)
                    """, {"label_name": label})
                except:
                    # Label already exists, continue
                    pass

                # Get label ID
                cursor.execute("""
                    SELECT id FROM labels WHERE label_name = :label_name
                """, {"label_name": label})

                label_data = cursor.fetchone()
                if label_data:
                    label_id = label_data[0]

                    # Link lecture to label
                    cursor.execute("""
                        INSERT INTO lecture_labels (lecture_id, label_id)
                        VALUES (:lecture_id, :label_id)
                    """, {
                        "lecture_id": lecture_id,
                        "label_id": label_id
                    })

            conn.commit()

            # Get complete lecture data with files and labels
            return get_lecture_data(cursor, lecture_id)

    except Exception as e:
        # Clean up files if database operation fails
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
        if transcript_path and os.path.exists(transcript_path):
            os.remove(transcript_path)
        raise HTTPException(status_code=500, detail=f"Failed to upload lecture: {str(e)}")

@router.get("/", response_model=List[LectureSchema])
def get_lectures():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Get all lectures
            cursor.execute("""
                SELECT id FROM lectures ORDER BY created_at DESC
            """)

            lecture_ids = [row[0] for row in cursor.fetchall()]
            lectures = []

            for lecture_id in lecture_ids:
                lecture_data = get_lecture_data(cursor, lecture_id)
                if lecture_data:
                    lectures.append(lecture_data)

            return lectures

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve lectures: {str(e)}")

@router.get("/{lecture_id}", response_model=LectureSchema)
def get_lecture(lecture_id: int):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            lecture_data = get_lecture_data(cursor, lecture_id)
            if not lecture_data:
                raise HTTPException(status_code=404, detail="Lecture not found")

            return lecture_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve lecture: {str(e)}")
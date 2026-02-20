from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime
import os

from ..database import get_connection
from ..config import config
try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

# Import Oracle AI utility (absolute import for FastAPI)
from app.utils.oracle_ai import run_class_analysis


router = APIRouter()


# Class Analytics Route
@router.post("/class_analytics/{class_id}")
def run_class_analytics(class_id: int):
    from ..database import get_connection
    # Aggregate lecture text
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pdf_text FROM lecture_files lf JOIN lectures l ON lf.lecture_id = l.id WHERE l.class_id = :class_id", {"class_id": class_id})
        lecture_texts = [row[0] for row in cursor.fetchall() if row[0]]
        cursor.execute("SELECT quiz_content, quiz_results FROM quizzes WHERE class_id = :class_id", {"class_id": class_id})
        quiz_rows = cursor.fetchall()
        if not quiz_rows:
            raise HTTPException(status_code=400, detail="Cannot run analysis: No quizzes found for this class.")
        quiz_contents = [row[0] for row in quiz_rows if row[0]]
        quiz_results = [row[1] for row in quiz_rows if row[1]]

    lecture_text = "\n".join(lecture_texts)
    quiz_content = "\n".join(quiz_contents)
    quiz_results_text = "\n".join(quiz_results)
    prompt = (
        "You are an AI teaching assistant analyzing a university course.\n\n"

        "Below are lecture transcripts and slide content:\n"
        f"{lecture_text}\n\n"

        "Below are quiz questions:\n"
        f"{quiz_content}\n\n"

        "Below are quiz performance results:\n"
        f"{quiz_results_text}\n\n"

        "Your task:\n"
        "1. Identify the concepts students are struggling with most based on quiz performance.\n"
        "2. Cross-reference those weak concepts with the lecture transcripts and slides.\n"
        "3. Determine where (which lecture topic, section, or example) each concept was originally covered.\n"
        "4. Infer why students may have misunderstood it (e.g., insufficient examples, rushed explanation, abstract treatment, lack of practice alignment).\n"
        "5. Suggest specific ways the professor could revisit or improve coverage of each concept.\n\n"

        "Output Requirements:\n"
        "- Only provide the TOP 3 weakest concepts.\n"
        "- For each concept, provide:\n"
        "   - Concept Name\n"
        "   - Estimated Mastery Score (0-100)\n"
        "   - Where It Was Covered (cite lecture title or topic if possible)\n"
        "   - Why Students Struggled\n"
        "   - How to Revisit / Improve It\n\n"

        "Be concise but specific. Ground your reasoning in the lecture and quiz content provided. List sections titles exaclty as provided."
    )
    import json
    try:
        analysis = run_class_analysis(prompt)
        print("Got promt")
        # Delete any existing analysis for this class, then insert new
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM class_analysis WHERE class_id = :class_id",
                {"class_id": class_id}
            )
            cursor.execute(
                """
                INSERT INTO class_analysis (class_id, analysis_text)
                VALUES (:class_id, :analysis_text)
                """,
                {"class_id": class_id, "analysis_text": json.dumps(analysis)}
            )
            conn.commit()
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run class analysis: {str(e)}")

# Get latest class analysis
@router.get("/class_analytics/{class_id}")
def get_class_analytics(class_id: int):
    from ..database import get_connection
    import json
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT analysis_text, created_at FROM class_analysis WHERE class_id = :class_id ORDER BY created_at DESC FETCH FIRST 1 ROW ONLY",
            {"class_id": class_id}
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="No analysis found for this class.")
        try:
            analysis_obj = json.loads(row[0])
        except Exception:
            analysis_obj = row[0]
        return {"analysis": analysis_obj, "created_at": row[1]}

# Get all quizzes for a specific class
@router.get("/by_class/{class_id}")
def get_quizzes_by_class(class_id: int):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, class_id, quiz_title, quiz_content, created_at FROM quizzes WHERE class_id = :class_id ORDER BY created_at DESC", {"class_id": class_id})
            quizzes = [
                {
                    "id": row[0],
                    "class_id": row[1],
                    "quiz_title": row[2],
                    "quiz_content": row[3],
                    "created_at": row[4],
                }
                for row in cursor.fetchall()
            ]
            return quizzes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quizzes for class: {str(e)}")

@router.post("/quizzes")
async def upload_quiz_plain(
    class_id: int = Form(...),
    quiz_title: str = Form(...),
    file: UploadFile = File(...),
    results_file: UploadFile = File(None)
):
    from PyPDF2 import PdfReader
    import io
    # Parse quiz file
    content = await file.read()
    reader = PdfReader(io.BytesIO(content))
    quiz_text = ""
    for page in reader.pages:
        quiz_text += page.extract_text() or ""

    # Parse results file if present
    results_text = None
    if results_file:
        results_content = await results_file.read()
        if results_file.filename and results_file.filename.lower().endswith('.pdf'):
            results_reader = PdfReader(io.BytesIO(results_content))
            results_text = ""
            for page in results_reader.pages:
                results_text += page.extract_text() or ""
        else:
            try:
                results_text = results_content.decode('utf-8')
            except Exception:
                results_text = results_content.decode('latin-1', errors='replace')

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO quizzes (class_id, quiz_title, quiz_content, quiz_results)
                VALUES (:class_id, :quiz_title, :quiz_content, :quiz_results)
                """,
                {
                    "class_id": class_id,
                    "quiz_title": quiz_title,
                    "quiz_content": quiz_text,
                    "quiz_results": results_text,
                },
            )
            conn.commit()
        return {"message": "Quiz stored"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store quiz: {str(e)}")

def extract_text_from_file(upload_file: UploadFile) -> str:
    """Extract text from uploaded .txt or .pdf file."""
    filename = upload_file.filename or ""
    content_type = upload_file.content_type or ""
    upload_file.file.seek(0)
    content = upload_file.file.read()
    if filename.lower().endswith('.txt') or content_type == 'text/plain':
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('latin-1', errors='replace')
        if not isinstance(text, str):
            raise HTTPException(status_code=400, detail="Uploaded .txt file could not be decoded as text.")
        return text
    elif filename.lower().endswith('.pdf') or content_type == 'application/pdf':
        if PdfReader is None:
            raise HTTPException(status_code=500, detail="PyPDF2 is not installed on the server.")
        import tempfile
        with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp:
            tmp.write(content)
            tmp.flush()
            reader = PdfReader(tmp.name)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if not text or not isinstance(text, str):
            raise HTTPException(status_code=400, detail="No extractable text found in PDF. Please upload a PDF with selectable text.")
        return text
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only .txt and .pdf are allowed.")


# Removed /upload endpoint and QuizSchema usage

@router.get("/")
def get_quizzes():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, class_id, quiz_title, quiz_content, created_at FROM quizzes ORDER BY created_at DESC")
            quizzes = [
                {
                    "id": row[0],
                    "class_id": row[1],
                    "quiz_title": row[2],
                    "quiz_content": row[3],
                    "created_at": row[4],
                }
                for row in cursor.fetchall()
            ]
            return quizzes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quizzes: {str(e)}")

@router.get("/{quiz_id}")
def get_quiz(quiz_id: int):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, class_id, quiz_title, quiz_content, created_at FROM quizzes WHERE id = :quiz_id", {"quiz_id": quiz_id})
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Quiz not found")
            return {
                "id": row[0],
                "class_id": row[1],
                "quiz_title": row[2],
                "quiz_content": row[3],
                "created_at": row[4],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quiz: {str(e)}")

@router.post("/")
def create_quiz(
    class_id: int = Form(...),
    quiz_title: str = Form(...),
    file: UploadFile = File(...)
):
    content = file.file.read()
    from PyPDF2 import PdfReader
    import io
    reader = PdfReader(io.BytesIO(content))
    quiz_text = ""
    for page in reader.pages:
        quiz_text += page.extract_text() or ""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO quizzes (class_id, quiz_title, quiz_content)
                VALUES (:class_id, :quiz_title, :quiz_content)
                """,
                {
                    "class_id": class_id,
                    "quiz_title": quiz_title,
                    "quiz_content": quiz_text,
                },
            )
            conn.commit()
        return {"message": "Quiz stored"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create quiz: {str(e)}")

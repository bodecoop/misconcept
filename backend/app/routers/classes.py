from fastapi import APIRouter, HTTPException
from typing import List
from ..database import get_connection
from ..schemas import ClassSchema, ClassCreate

router = APIRouter()


# Delete a single class and all its dependent lectures, files, and labels
@router.delete("/{class_id}", status_code=204)
def delete_class(class_id: int):
    """Delete a single class and all its dependent lectures, files, and labels."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Get all lecture IDs for this class
            cursor.execute("SELECT id FROM lectures WHERE class_id = :class_id", {"class_id": class_id})
            lecture_ids = [row[0] for row in cursor.fetchall()]
            # Delete lecture_labels for these lectures
            for lecture_id in lecture_ids:
                cursor.execute("DELETE FROM lecture_labels WHERE lecture_id = :lecture_id", {"lecture_id": lecture_id})
                cursor.execute("DELETE FROM lecture_files WHERE lecture_id = :lecture_id", {"lecture_id": lecture_id})
                cursor.execute("DELETE FROM lectures WHERE id = :lecture_id", {"lecture_id": lecture_id})
            # Delete the class itself
            cursor.execute("DELETE FROM classes WHERE id = :class_id", {"class_id": class_id})
            conn.commit()
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete class: {str(e)}")

@router.post("/", response_model=ClassSchema)
def create_class(class_data: ClassCreate):
    """Create a new class"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Check if class already exists
            cursor.execute("SELECT id FROM classes WHERE class_name = :class_name",
                         {"class_name": class_data.class_name})
            existing_class = cursor.fetchone()

            if existing_class:
                raise HTTPException(status_code=400, detail="Class already exists")

            # Create new class
            cursor.execute("""
                INSERT INTO classes (class_name)
                VALUES (:class_name)
            """, {"class_name": class_data.class_name})

            # Get the inserted class data
            cursor.execute("""
                SELECT id, class_name, created_at
                FROM classes
                WHERE class_name = :class_name
                ORDER BY created_at DESC
                FETCH FIRST 1 ROW ONLY
            """, {"class_name": class_data.class_name})

            class_data_result = cursor.fetchone()
            if not class_data_result:
                raise HTTPException(status_code=500, detail="Failed to create class")

            conn.commit()

            return ClassSchema(
                id=class_data_result[0],
                class_name=class_data_result[1],
                created_at=class_data_result[2]
            )

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create class: {str(e)}")

@router.get("/", response_model=List[ClassSchema])
def get_classes():
    """Get all classes"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, class_name, created_at
                FROM classes
                ORDER BY created_at DESC
            """)

            classes_data = cursor.fetchall()
            classes = []

            for class_data in classes_data:
                classes.append(ClassSchema(
                    id=class_data[0],
                    class_name=class_data[1],
                    created_at=class_data[2]
                ))

            return classes

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve classes: {str(e)}")

@router.get("/{class_id}", response_model=ClassSchema)
def get_class(class_id: int):
    """Get a specific class by ID"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, class_name, created_at
                FROM classes
                WHERE id = :class_id
            """, {"class_id": class_id})

            class_data = cursor.fetchone()
            if not class_data:
                raise HTTPException(status_code=404, detail="Class not found")

            return ClassSchema(
                id=class_data[0],
                class_name=class_data[1],
                created_at=class_data[2]
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve class: {str(e)}")
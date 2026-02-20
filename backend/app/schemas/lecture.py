from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class LectureLabelBase(BaseModel):
    label_name: str

class LectureLabel(LectureLabelBase):
    id: int
    lecture_id: int

    class Config:
        from_attributes = True

class LectureFile(BaseModel):
    id: int
    file_type: str  # 'pdf', 'transcript'
    pdf_text: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class LectureBase(BaseModel):
    class_id: int
    lecture_title: str
    lecture_date: date
    labels: List[str] = []

class LectureCreate(LectureBase):
    pass

class Lecture(LectureBase):
    id: int
    created_at: datetime
    files: List[LectureFile] = []
    labels: List[LectureLabel] = []

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True
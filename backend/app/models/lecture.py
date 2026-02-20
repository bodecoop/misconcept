from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_name = Column(String(255), nullable=False)
    lecture_title = Column(String(255), nullable=False)
    lecture_date = Column(Date, nullable=False)
    pdf_file_path = Column(String(500))
    transcript_file_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    user = relationship("User")
    labels = relationship("LectureLabel", back_populates="lecture")
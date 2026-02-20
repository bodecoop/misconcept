from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class LectureLabel(Base):
    __tablename__ = "lecture_labels"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    label = Column(String(100), nullable=False)

    # Relationship
    lecture = relationship("Lecture", back_populates="labels")
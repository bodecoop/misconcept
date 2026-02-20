from pydantic import BaseModel
from typing import List
from datetime import datetime

class ClassBase(BaseModel):
    class_name: str

class ClassCreate(ClassBase):
    pass

class Class(ClassBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
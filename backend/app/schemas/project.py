from typing import Optional
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    project_name: str
    description: Optional[str] = None


class ProjectOut(ProjectCreate):
    id: int
    created_by: int

    class Config:
        from_attributes = True

from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "Open"
    priority: Optional[str] = "Medium"
    severity: Optional[str] = "Low"
    assigned_to: Optional[int] = None
    project_id: int


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    severity: Optional[str] = None
    assigned_to: Optional[int] = None
    project_id: Optional[int] = None


class IssueOut(IssueCreate):
    id: int
    reporter: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

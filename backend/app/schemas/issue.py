from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional

SEVERITIES = {"Critical", "High", "Medium", "Low"}
PRIORITIES = {"High", "Medium", "Low"}
STATUSES = {"Open", "Assigned", "In Progress", "In Review", "Resolved", "Verified", "Closed"}

class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = "Medium"
    severity: str = "Low"
    category: Optional[str] = None
    assigned_to: Optional[int] = None
    project_id: int
    sprint_id: Optional[int] = None
    duplicate_of_issue_id: Optional[int] = None
    confirm_duplicate: bool = False
    @field_validator("severity")
    @classmethod
    def valid_severity(cls, value: str) -> str:
        if value not in SEVERITIES: raise ValueError("Invalid severity")
        return value
    @field_validator("priority")
    @classmethod
    def valid_priority(cls, value: str) -> str:
        if value not in PRIORITIES: raise ValueError("Invalid priority")
        return value

class IssueUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    assigned_to: Optional[int] = None
    project_id: Optional[int] = None
    sprint_id: Optional[int] = None
    @field_validator("status")
    @classmethod
    def valid_status(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in STATUSES: raise ValueError("Invalid workflow status")
        return value
    @field_validator("severity")
    @classmethod
    def valid_severity(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in SEVERITIES: raise ValueError("Invalid severity")
        return value
    @field_validator("priority")
    @classmethod
    def valid_priority(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in PRIORITIES: raise ValueError("Invalid priority")
        return value

class IssueOut(IssueCreate):
    id: int
    reporter: int
    status: str
    reporter_name: Optional[str] = None
    assignee_name: Optional[str] = None
    project_name: Optional[str] = None
    sprint_name: Optional[str] = None
    attachment_count: int = 0
    comment_count: int = 0
    ai_score: Optional[int] = None
    embedding: Optional[str] = None
    is_possible_duplicate: bool = False
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True

class CommentCreate(BaseModel): body: str = Field(min_length=1)
class CommentUpdate(CommentCreate): pass
class CommentOut(BaseModel):
    id: int
    issue_id: int
    author_id: int
    author_name: Optional[str] = None
    body: str
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True

class AttachmentOut(BaseModel):
    id: int
    issue_id: int
    uploaded_by: int
    uploader_name: Optional[str] = None
    original_filename: str
    content_type: Optional[str]
    size_bytes: int
    created_at: datetime
    class Config: from_attributes = True

class ActivityOut(BaseModel):
    id: int
    issue_id: int
    actor_id: Optional[int]
    actor_name: Optional[str] = None
    action: str
    details: Optional[str]
    created_at: datetime
    class Config: from_attributes = True
class SprintBase(BaseModel):
    name: str = Field(min_length=1, max_length=255); goal: Optional[str] = None; start_date: date; end_date: date; status: str = "Planned"; project_id: int
    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str) -> str:
        if value not in {"Planned", "Active", "Completed"}: raise ValueError("Invalid sprint status")
        return value
class SprintCreate(SprintBase): pass
class SprintUpdate(BaseModel):
    name: Optional[str] = None; goal: Optional[str] = None; start_date: Optional[date] = None; end_date: Optional[date] = None; status: Optional[str] = None
class SprintOut(SprintBase):
    id: int; created_by: int; created_at: datetime; issue_count: int = 0
    class Config: from_attributes = True
class DuplicateCandidate(BaseModel): id: int; title: str; similarity: float
class DuplicateCheck(BaseModel): title: str; description: Optional[str] = None; project_id: Optional[int] = None

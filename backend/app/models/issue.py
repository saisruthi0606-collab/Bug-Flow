from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.database import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="Open", nullable=False)
    priority = Column(String(50), default="Medium", nullable=False)
    severity = Column(String(50), default="Low", nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    reporter = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_issues")
    reporter_user = relationship("User", foreign_keys=[reporter], backref="reported_issues")
    project = relationship("Project", backref="issues")

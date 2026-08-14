from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
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
    category = Column(String(100), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    embedding = Column(Text, nullable=True)
    is_possible_duplicate = Column(Boolean, default=False, nullable=False)
    duplicate_of_issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    reporter = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_issues")
    reporter_user = relationship("User", foreign_keys=[reporter], backref="reported_issues")
    project = relationship("Project", backref="issues")
    sprint = relationship("Sprint", back_populates="issues")
    duplicate_of = relationship("Issue", remote_side=[id], foreign_keys=[duplicate_of_issue_id])

    @property
    def reporter_name(self) -> str | None:
        return self.reporter_user.full_name if self.reporter_user else None

    @property
    def assignee_name(self) -> str | None:
        return self.assignee.full_name if self.assignee else None

    @property
    def project_name(self) -> str | None:
        return self.project.project_name if self.project else None

    @property
    def sprint_name(self) -> str | None:
        return self.sprint.name if self.sprint else None

    @property
    def attachment_count(self) -> int:
        return len(self.attachments) if hasattr(self, 'attachments') else 0

    @property
    def comment_count(self) -> int:
        return len(self.comments) if hasattr(self, 'comments') else 0

    @property
    def ai_score(self) -> int | None:
        return self.ai_recommendation.confidence_score if hasattr(self, 'ai_recommendation') and self.ai_recommendation else None

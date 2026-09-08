from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.database import Base


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (Index("ix_comments_issue_created", "issue_id", "created_at"),)
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    issue = relationship("Issue", backref="comments")
    author = relationship("User")
    @property
    def author_name(self):
        return self.author.full_name if self.author else None


class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    content_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    issue = relationship("Issue", backref="attachments")
    uploader = relationship("User")
    @property
    def uploader_name(self):
        return self.uploader.full_name if self.uploader else None


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (Index("ix_activities_issue_created", "issue_id", "created_at"),)
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    issue = relationship("Issue", backref="activities")
    actor = relationship("User")
    @property
    def actor_name(self):
        return self.actor.full_name if self.actor else None


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    severity = Column(String(50), nullable=True)
    priority = Column(String(50), nullable=True)
    root_cause = Column(Text, nullable=True)
    suggested_resolution = Column(Text, nullable=True)
    confidence_score = Column(Integer, nullable=False)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    issue = relationship("Issue", backref="ai_recommendation", uselist=False)


class ImpactPredictionRecord(Base):
    """Shared, versioned predictor output for an issue."""
    __tablename__ = "impact_prediction_records"
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, unique=True, index=True)
    signature = Column(String(64), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    payload = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    issue = relationship("Issue", backref="impact_prediction", uselist=False)

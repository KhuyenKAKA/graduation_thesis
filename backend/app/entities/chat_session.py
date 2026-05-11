"""
Entity: ChatSession
SQLAlchemy ORM model for the `chat_sessions` table.
"""
from __future__ import annotations
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from app.database import Base
from datetime import datetime

if TYPE_CHECKING:
    from .chat_message import ChatMessage
    from .chat_summary import ChatSummary


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(255), default="New Chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ──────────────────────────────────────────────────────
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )
    summary: Mapped[Optional["ChatSummary"]] = relationship(
        "ChatSummary", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ChatSession id={self.id!r} user_id={self.user_id}>"
 
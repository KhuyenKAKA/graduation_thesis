"""
Entity: ChatSummary
SQLAlchemy ORM model for the `chat_session_summaries` table.
"""
from __future__ import annotations
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional
from app.database import Base
from datetime import datetime

if TYPE_CHECKING:
    from .chat_session import ChatSession


class ChatSummary(Base):
    __tablename__ = "chat_session_summaries"

    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), primary_key=True
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    updated_msg_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────
    session: Mapped[Optional["ChatSession"]] = relationship(
        "ChatSession", back_populates="summary"
    )

    def __repr__(self) -> str:
        return f"<ChatSummary session_id={self.session_id!r} msg_count={self.updated_msg_count}>"
 
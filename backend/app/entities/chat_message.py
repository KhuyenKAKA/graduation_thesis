"""
Entity: ChatMessage
SQLAlchemy ORM model for the `chat_messages` table.
"""
from __future__ import annotations
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional
from app.database import Base
from datetime import datetime

if TYPE_CHECKING:
    from .chat_session import ChatSession


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        Enum("user", "assistant", name="chat_role"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # ── Relationships ──────────────────────────────────────────────────────
    session: Mapped[Optional["ChatSession"]] = relationship(
        "ChatSession", back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} role={self.role!r} session_id={self.session_id!r}>"
 
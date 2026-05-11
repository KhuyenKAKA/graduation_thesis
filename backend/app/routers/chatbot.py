"""
Chatbot API router.

Endpoints:
  POST   /api/chatbot/chat                           — send a message, get AI reply
  GET    /api/chatbot/sessions                       — list sessions for a user
  GET    /api/chatbot/sessions/{session_id}/messages — load message history
  DELETE /api/chatbot/sessions/{session_id}          — delete a session
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.entities.chat_session import ChatSession
from app.entities.chat_message import ChatMessage
from app.entities.chat_summary import ChatSummary
from app.dependencies import get_current_user
from app.utils.chatbot import ChatbotEngine

router = APIRouter()
_engine: Optional[ChatbotEngine] = None

# Profile cache: {user_id: (profile_dict, timestamp)}
_profile_cache: Dict[int, Tuple[Optional[dict], float]] = {}
_PROFILE_TTL = 300  # 5 minutes


def _get_engine() -> ChatbotEngine:
    global _engine
    if _engine is None:
        try:
            from app.config import settings
            gemini_key     = getattr(settings, "GEMINI_KEY",     None)
            tavily_key     = getattr(settings, "TAVILY_API_KEY", None)
            gemini_key_pro = getattr(settings, "GEMINI_KEY_PRO", None)
        except Exception:
            gemini_key = None
            tavily_key = None
            gemini_key_pro = None
        _engine = ChatbotEngine(
                gemini_key     = gemini_key,
                tavily_key     = tavily_key,
                gemini_key_pro = gemini_key_pro,
                google_key     = getattr(settings, "GOOGLE_GENAI_KEY", "") or "",
                primary_base   = getattr(settings, "PRIMARY_API_BASE",  "") or "",
                primary_model  = getattr(settings, "PRIMARY_MODEL",      "") or "",
                wokushop_base  = getattr(settings, "WOKUSHOP_BASE",      "") or "",
                wokushop_model = getattr(settings, "WOKUSHOP_MODEL",     "") or "",
            )
    return _engine


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message:    str           = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    user_id:    Optional[int] = None


class ChatResponse(BaseModel):
    response:   str
    session_id: str


class SessionItem(BaseModel):
    id:         str
    title:      str
    created_at: str


class MessageItem(BaseModel):
    id:         int
    role:       str
    content:    str
    created_at: str


# ---------------------------------------------------------------------------
# Route helpers
# ---------------------------------------------------------------------------

def _get_or_create_session(session_id: Optional[str], user_id: Optional[int], title: str) -> str:
    db: Session = SessionLocal()
    try:
        if session_id:
            row = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if row:
                return session_id

        new_id = str(uuid.uuid4())
        session = ChatSession(id=new_id, user_id=user_id, title=title[:255])
        db.add(session)
        db.commit()
        return new_id
    finally:
        db.close()


def _load_history(session_id: str, limit: int = 10) -> List[dict]:
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.id.desc())
            .limit(limit)
            .all()
        )
        return [{"role": r.role, "content": r.content} for r in reversed(rows)]
    finally:
        db.close()


def _load_user_profile(user_id: Optional[int]) -> Optional[dict]:
    """Load study background scores + language info for a user (used as profile context for the AI)."""
    if not user_id:
        return None
    # Return cached profile if still fresh
    if user_id in _profile_cache:
        cached_profile, cached_ts = _profile_cache[user_id]
        if time.time() - cached_ts < _PROFILE_TTL:
            return cached_profile
    try:
        from app.models.study_bg import StudyBGModel
        from app.entities.user import User as UserEntity
        from app.entities.country import Country as CountryEntity
        db: Session = SessionLocal()
        try:
            profile = StudyBGModel.get_by_user_id(db, user_id)
            user_row = db.query(UserEntity).filter(UserEntity.id == user_id).first()

            result: dict = {}
            if profile:
                keys = ("ielts", "toefl", "gpa", "sat", "gre", "gmat", "act",
                        "inter_bac", "cam_adv_test", "level", "major", "graduate_year")
                result = {k: profile[k] for k in keys if profile.get(k) is not None}
            if user_row:
                if user_row.main_lang:
                    result["main_lang"] = user_row.main_lang
                if user_row.add_lang:
                    result["add_lang"] = user_row.add_lang
                if user_row.country_id:
                    country = db.query(CountryEntity).filter(CountryEntity.id == user_row.country_id).first()
                    if country:
                        result["country"] = country.name
        finally:
            db.close()
        profile_result = result if result else None
        _profile_cache[user_id] = (profile_result, time.time())
        print(f"[Chatbot] Loaded profile for user_id={user_id}: {profile_result}")
        return profile_result
    except Exception as exc:
        print(f"[Chatbot] Failed to load user profile for user_id={user_id}: {exc}")
        return None


def _save_messages(session_id: str, user_msg: str, bot_reply: str) -> None:
    db: Session = SessionLocal()
    try:
        db.add(ChatMessage(session_id=session_id, role="user", content=user_msg))
        db.add(ChatMessage(session_id=session_id, role="assistant", content=bot_reply))
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.updated_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


def _load_summary(session_id: str) -> str:
    """Load the stored conversation summary for a session (empty string if none)."""
    db: Session = SessionLocal()
    try:
        row = (
            db.query(ChatSummary)
            .filter(ChatSummary.session_id == session_id)
            .first()
        )
        return row.summary if row else ""
    finally:
        db.close()


def _maybe_update_summary(session_id: str, engine) -> None:
    """
    Summarize older messages and cache in chat_session_summaries when the
    session has >= 10 messages AND at least 10 new messages arrived since
    the last summary update.  Runs synchronously after the SSE done event.
    """
    try:
        db: Session = SessionLocal()
        try:
            count = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).count()
            if count < 10:
                return

            existing = (
                db.query(ChatSummary)
                .filter(ChatSummary.session_id == session_id)
                .first()
            )
            last_count = existing.updated_msg_count if existing else 0
            if count - last_count < 10:
                return

            all_msgs = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.id.asc())
                .all()
            )
            older = all_msgs[:-5] if len(all_msgs) > 5 else all_msgs
            if not older:
                return

            older_dicts = [{"role": m.role, "content": m.content} for m in older]
            summary_text = engine.summarize_history(older_dicts)
            if not summary_text:
                return

            if existing:
                existing.summary = summary_text
                existing.updated_msg_count = count
                existing.updated_at = datetime.utcnow()
            else:
                db.add(ChatSummary(
                    session_id=session_id,
                    summary=summary_text,
                    updated_msg_count=count,
                    updated_at=datetime.utcnow(),
                ))
            db.commit()
            print(f"[Chatbot] Summary updated for session {session_id} ({count} messages).")
        finally:
            db.close()
    except Exception as exc:
        print(f"[Chatbot] Summary update error: {exc}")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    Send a user message and receive an AI-generated reply grounded in the
    university database. Manages session creation and history automatically.
    """
    try:
        user_id    = current_user["id"]
        title      = (req.message[:60] + "…") if len(req.message) > 60 else req.message
        session_id = _get_or_create_session(req.session_id, user_id, title)

        history         = _load_history(session_id)
        history_summary = _load_summary(session_id)
        user_profile    = _load_user_profile(user_id)
        engine          = _get_engine()
        bot_reply       = engine.process(req.message, history, user_profile=user_profile, history_summary=history_summary)

        _save_messages(session_id, req.message, bot_reply)
        _maybe_update_summary(session_id, engine)

        return ChatResponse(response=bot_reply, session_id=session_id)
    except Exception as exc:
        exc_name = type(exc).__name__
        if any(k in exc_name for k in ("OperationalError", "DatabaseError", "InterfaceError", "ProgrammingError")):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cannot connect to the database. Please try again later.",
            ) from exc
        raise


@router.get("/sessions", response_model=List[SessionItem])
async def list_sessions(current_user: dict = Depends(get_current_user)):
    """List the 50 most recent chat sessions for the authenticated user."""
    user_id = current_user["id"]
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .limit(50)
            .all()
        )
        return [
            SessionItem(id=r.id, title=r.title, created_at=str(r.created_at))
            for r in rows
        ]
    finally:
        db.close()


@router.get("/sessions/{session_id}/messages", response_model=List[MessageItem])
async def get_messages(session_id: str, current_user: dict = Depends(get_current_user)):
    """Return all messages in a chat session, ordered oldest \u2192 newest."""
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.id.asc())
            .all()
        )
        return [
            MessageItem(
                id=r.id,
                role=r.role,
                content=r.content,
                created_at=str(r.created_at),
            )
            for r in rows
        ]
    finally:
        db.close()


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a session and all its messages (cascades via FK)."""
    db: Session = SessionLocal()
    try:
        db.query(ChatSession).filter(ChatSession.id == session_id).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------

async def _sync_gen_to_sse(sync_gen) -> AsyncGenerator[str, None]:
    """
    Wraps a blocking sync generator into an async generator suitable for
    FastAPI StreamingResponse.  Each text chunk is emitted as an SSE
    'data:' line; the special <<ONLINE_SEARCH|query>> signal is emitted
    as a named 'online_search' SSE event.
    Port of the Tkinter chunk-writing loop in /chatbot/engine/chat_engine.py.
    """
    loop = asyncio.get_event_loop()
    while True:
        chunk = await loop.run_in_executor(None, lambda: next(sync_gen, None))
        if chunk is None:
            break
        if chunk.startswith("<<ONLINE_SEARCH|"):
            query = chunk[len("<<ONLINE_SEARCH|"):-2]  # strip << and >>
            yield f"event: online_search\ndata: {json.dumps({'query': query})}\n\n"
        else:
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"


# ---------------------------------------------------------------------------
# Streaming chat endpoint  (port of ask_stream from /chatbot/engine/chat_engine.py)
# ---------------------------------------------------------------------------

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    SSE streaming endpoint — yields text chunks as they are generated.

    SSE event types:
      (default)      data: {"chunk": "..."}
      online_search  data: {"query": "..."}
      done           data: {"session_id": "..."}
    """
    title        = (req.message[:60] + "…") if len(req.message) > 60 else req.message
    session_id   = _get_or_create_session(req.session_id, req.user_id, title)
    history      = _load_history(session_id)
    history_summary = _load_summary(session_id)
    user_profile = _load_user_profile(req.user_id)
    engine       = _get_engine()

    async def generate() -> AsyncGenerator[str, None]:
        sync_gen     = engine.process_stream(req.message, history, user_profile=user_profile, history_summary=history_summary)
        full_reply   = []
        has_sent_done = False

        try:
            async for sse_line in _sync_gen_to_sse(sync_gen):
                # Accumulate plain text chunks for DB storage
                if sse_line.startswith("data: ") and '"chunk"' in sse_line:
                    try:
                        payload = json.loads(sse_line[6:])
                        full_reply.append(payload.get("chunk", ""))
                    except Exception:
                        pass
                yield sse_line
        except Exception as exc:
            err_chunk = '\u274c Error: ' + str(exc)
            yield 'data: ' + json.dumps({'chunk': err_chunk}) + '\n\n'
        finally:
            # Save conversation to DB
            reply_text = "".join(full_reply)
            if reply_text:
                _save_messages(session_id, req.message, reply_text)
            # Emit done event with session_id for the frontend to persist
            yield f"event: done\ndata: {json.dumps({'session_id': session_id})}\n\n"
            # Update summary after done event (runs after stream completes)
            _maybe_update_summary(session_id, engine)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ---------------------------------------------------------------------------
# Online search endpoint  (port of perform_online_search + search_tool.py)
# ---------------------------------------------------------------------------

class SearchOnlineRequest(BaseModel):
    message:     str           = Field(..., min_length=1, max_length=2000)
    session_id:  Optional[str] = None
    search_hint: str           = Field(default="", max_length=200)


@router.post("/chat/search-online")
async def search_online(req: SearchOnlineRequest):
    """
    Triggered when the user clicks the 'Search Online' button after the bot
    signals insufficient DB data (<<ONLINE_SEARCH|query>> signal).

    SSE event types:
      (default)  data: {"chunk": "..."}
      done       data: {}
    """
    from app.utils.online_search import OnlineSearchEngine
    try:
        from app.config import settings
        tavily_key = getattr(settings, "TAVILY_API_KEY", None)
    except Exception:
        tavily_key = None

    engine        = _get_engine()
    search_engine = OnlineSearchEngine(
        stream_gemini=engine._gemini.stream,
        tavily_key=tavily_key,
    )

    async def generate() -> AsyncGenerator[str, None]:
        sync_gen   = search_engine.search_and_stream(
            user_query=req.message,
            search_hint=req.search_hint,
        )
        full_reply = []

        try:
            async for sse_line in _sync_gen_to_sse(sync_gen):
                if sse_line.startswith("data: ") and '"chunk"' in sse_line:
                    try:
                        payload = json.loads(sse_line[6:])
                        full_reply.append(payload.get("chunk", ""))
                    except Exception:
                        pass
                yield sse_line
        except Exception as exc:
            err_chunk = '\u274c Search error: ' + str(exc)
            yield 'data: ' + json.dumps({'chunk': err_chunk}) + '\n\n'
        finally:
            # Optionally persist search result to session
            if req.session_id and full_reply:
                reply_text = "".join(full_reply)
                try:
                    _db: Session = SessionLocal()
                    try:
                        _db.add(ChatMessage(
                            session_id=req.session_id,
                            role="assistant",
                            content=f"[Online Search]\n{reply_text}",
                        ))
                        sess = _db.query(ChatSession).filter(ChatSession.id == req.session_id).first()
                        if sess:
                            sess.updated_at = datetime.utcnow()
                        _db.commit()
                    finally:
                        _db.close()
                except Exception:
                    pass
            yield f"event: done\ndata: {{}}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
 
"""FastAPI with isolated, in-process SmartDesk sessions."""
import asyncio
import os
import time
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .agent import SmartDesk
from .security import SecurityError

app = FastAPI(title='SmartDesk Agent')
SESSION_TTL_SECONDS = 3600
MAX_SESSIONS = 100
_sessions = {}
_sessions_lock = asyncio.Lock()


class Ask(BaseModel):
    question: str
    session_id: str | None = None


class Approve(BaseModel):
    order_id: str
    issue: str
    approved: bool = False


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/ask')
async def ask(body: Ask):
    now = time.monotonic()
    async with _sessions_lock:
        for sid, entry in list(_sessions.items()):
            if now - entry['last_used'] > SESSION_TTL_SECONDS and not entry['lock'].locked():
                del _sessions[sid]
        if body.session_id is not None:
            entry = _sessions.get(body.session_id)
            if entry is None:
                raise HTTPException(404, 'Session not found or expired')
            sid = body.session_id
        else:
            if len(_sessions) >= MAX_SESSIONS:
                raise HTTPException(503, 'Too many active sessions')
            sid = str(uuid.uuid4())
            entry = {
                'agent': SmartDesk(mock=os.getenv('SMARTDESK_MOCK') == '1'),
                'lock': asyncio.Lock(),
                'last_used': now,
            }
            _sessions[sid] = entry
        entry['last_used'] = now
    async with entry['lock']:
        try:
            result = await entry['agent'].run(body.question)
            return {'session_id': sid, **result,
                    'pending_approval': entry['agent'].pending_ticket is not None}
        except (SecurityError, ValueError) as exc:
            raise HTTPException(400, str(exc)) from exc
        finally:
            entry['last_used'] = time.monotonic()


@app.post('/approve-ticket')
def approve_ticket(body: Approve):
    # This route is deliberately disabled until authenticated operator approval exists.
    # A client-provided `approved: true` is NOT trusted authorization.
    raise HTTPException(403, 'API ticket approval disabled; use the interactive CLI')

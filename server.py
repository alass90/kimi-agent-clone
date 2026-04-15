"""
Kimi Clone - Main API Server
Mirrors Kimi's kernel_server.py architecture.
Provides endpoints for chat, session management, and file access.
"""
import os
import uuid
import logging
import time
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

# Load environment variables from .env file first
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from config.settings import (
    API_HOST, API_PORT, CORS_ORIGINS, 
    WORKSPACE_DIR, UPLOAD_DIR, OUTPUT_DIR, LOG_FILE, AGENT_MODES
)
from agent.orchestrator import session_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE)
    ]
)
logger = logging.getLogger("kimi-server")

app = FastAPI(
    title="Kimi Clone API",
    description="Faithful reproduction of Kimi's agentic backend",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Models ──────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: Optional[str] = "ok_computer"
    stream: Optional[bool] = False

class SessionCreate(BaseModel):
    mode: Optional[str] = "ok_computer"

# ─── Endpoints ───────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "active_sessions": len(session_manager.sessions)
    }

@app.get("/api/modes")
async def list_modes():
    """List available agent modes."""
    return {"modes": AGENT_MODES}

@app.post("/api/sessions")
async def create_session(req: SessionCreate):
    """Create a new agent session."""
    session_id = str(uuid.uuid4())[:8]
    mode = req.mode or "ok_computer"
    if mode not in AGENT_MODES:
        raise HTTPException(400, f"Invalid mode: {mode}")
    
    session = session_manager.get_or_create(session_id, mode)
    return {
        "session_id": session_id,
        "mode": session.mode,
        "created_at": session.created_at,
        "description": AGENT_MODES[mode]["description"]
    }

@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions."""
    return {"sessions": session_manager.list_sessions()}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and cleanup resources."""
    await session_manager.delete(session_id)
    return {"status": "deleted", "session_id": session_id}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Supports both standard and streaming responses.
    """
    session_id = request.session_id or str(uuid.uuid4())[:8]
    session = session_manager.get_or_create(session_id, request.mode)
    
    logger.info(f"Chat request: session={session_id}, mode={session.mode}, stream={request.stream}")

    if request.stream:
        async def event_generator():
            async for event in session.process_message_stream(request.message):
                yield f"data: {json.dumps(event)}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        try:
            response_text = await session.process_message(request.message)
            return {
                "session_id": session_id,
                "response": response_text,
                "history": session.get_history(),
                "tool_calls_used": session.tool_call_count
            }
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise HTTPException(500, f"Agent error: {str(e)}")

@app.get("/api/sessions/{session_id}/history")
async def get_history(session_id: str):
    """Get conversation history for a session."""
    if session_id not in session_manager.sessions:
        raise HTTPException(404, "Session not found")
    session = session_manager.sessions[session_id]
    return {"history": session.get_history()}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the agent's workspace."""
    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    logger.info(f"File uploaded: {filename} ({len(content)} bytes)")
    
    return {
        "filename": filename,
        "path": str(file_path),
        "size": len(content)
    }

@app.get("/api/files/{filename}")
async def get_file(filename: str):
    """Download a file from the workspace (output or upload)."""
    out_path = OUTPUT_DIR / filename
    up_path = UPLOAD_DIR / filename
    
    if out_path.exists():
        return FileResponse(out_path)
    elif up_path.exists():
        return FileResponse(up_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/workspace")
async def list_workspace():
    """List all files in the workspace."""
    files = []
    for root, dirs, filenames in os.walk(WORKSPACE_DIR):
        for f in filenames:
            path = Path(root) / f
            files.append({
                "name": f,
                "path": str(path.relative_to(WORKSPACE_DIR)),
                "size": path.stat().st_size,
                "modified": path.stat().st_mtime
            })
    return {"files": files}

# ─── WebSocket for Streaming ─────────────────────────────────────────────

@app.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat with event streaming."""
    await websocket.accept()
    session = session_manager.get_or_create(session_id)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                user_message = msg.get("message", "")
                if msg.get("mode"):
                    session = session_manager.get_or_create(session_id, msg["mode"])
            except json.JSONDecodeError:
                user_message = data

            if not user_message:
                continue

            # Process the message with streaming
            try:
                async for event in session.process_message_stream(user_message):
                    await websocket.send_json(event)
            except Exception as e:
                logger.error(f"WS Error: {e}")
                await websocket.send_json({"type": "error", "content": str(e)})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")

# ─── Static Files ────────────────────────────────────────────────────────

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

# ─── Lifecycle ───────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Run on server startup."""
    logger.info("🚀 Kimi Clone Backend starting up...")
    # Start background task for session cleanup
    async def cleanup_loop():
        while True:
            await asyncio.sleep(3600) # Every hour
            await session_manager.cleanup_inactive()
    
    asyncio.create_task(cleanup_loop())

@app.on_event("shutdown")
async def shutdown_event():
    """Run on server shutdown."""
    logger.info("Kimi Clone Backend shutting down...")
    # Cleanup all sessions
    for sid in list(session_manager.sessions.keys()):
        await session_manager.delete(sid)

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)

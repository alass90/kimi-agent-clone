"""
Agent Orchestrator
Implements the core agent loop:
1. Receive user message
2. Build system prompt (with skill injection if needed)
3. Call LLM with tools
4. Execute tool calls
5. Feed results back to LLM
6. Repeat until LLM responds without tool calls
7. Return final response

Mirrors Kimi's architecture:
- Connectivity (tools) is fixed infrastructure
- Cognition (skills, context) is dynamic, loaded at runtime
- E2B sandbox for isolated code execution
"""
import json
import logging
import asyncio
import time
import traceback
from typing import List, Dict, Any, Optional, AsyncGenerator
from pathlib import Path
from openai import OpenAI
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.prompts import build_system_prompt, PROMPTS
from tools.registry import get_all_tools, get_tool_names
from tools.executors import ToolExecutor
from config.settings import (
    LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    AGENT_MODES, SKILLS_DIR, MAX_OUTPUT_LENGTH,
    MAX_AGENT_ITERATIONS, DEFAULT_MODE, OPENAI_BASE_URL,
)

logger = logging.getLogger(__name__)


class AgentSession:
    """
    Represents a single agent session with conversation history,
    tool state, and skill context.

    Each session has its own:
    - Conversation history (messages)
    - Tool executor (with persistent state: browser, kernel, todo)
    - Loaded skills set
    - Tool call counter
    """

    def __init__(self, session_id: str, mode: str = None):
        self.session_id = session_id
        self.mode = mode or DEFAULT_MODE
        self.messages: List[Dict[str, Any]] = []
        self.tool_call_count = 0
        self.total_tool_calls = 0
        self.loaded_skills: set = set()
        self.created_at = time.time()
        self.last_active = time.time()

        # Max tool calls per turn (0 = unlimited)
        mode_config = AGENT_MODES.get(self.mode, AGENT_MODES["ok_computer"])
        self.max_tool_calls = mode_config.get("max_tool_calls_per_turn", 0)
        if self.max_tool_calls == 0:
            self.max_tool_calls = MAX_AGENT_ITERATIONS

        # Initialize OpenAI client
        client_kwargs = {}
        if OPENAI_BASE_URL:
            client_kwargs["base_url"] = OPENAI_BASE_URL
        # Don't fail if no API key - it will be caught at runtime
        if os.getenv("OPENAI_API_KEY"):
            self.client = OpenAI(**client_kwargs)
        else:
            self.client = None

        # Initialize tool executor (persistent across turns)
        self.executor = ToolExecutor()

        # Initialize with system prompt
        system_prompt = build_system_prompt(self.mode)
        self.messages.append({"role": "system", "content": system_prompt})
        logger.info(f"Session {session_id} created in mode: {self.mode}")

    def _detect_skills(self, user_message: str) -> List[str]:
        """
        Detect which skills should be loaded based on user intent.
        Mirrors Kimi's skill detection from the system prompt.
        """
        from config.settings import SKILL_REGISTRY
        needed_skills = []
        message_lower = user_message.lower()

        for skill_name, skill_info in SKILL_REGISTRY.items():
            for trigger in skill_info.get("triggers", []):
                if trigger in message_lower:
                    needed_skills.append(skill_name)
                    break

        return needed_skills

    async def _inject_skill(self, skill_name: str) -> Optional[str]:
        """
        Load a skill file and inject it into context.
        This is the core of Kimi's 'cognition is dynamic' architecture.
        """
        if skill_name in self.loaded_skills:
            return None

        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        if skill_path.exists():
            content = skill_path.read_text(encoding="utf-8")
            self.loaded_skills.add(skill_name)
            logger.info(f"Skill injected: {skill_name}")
            return content

        return None

    async def process_message(
        self,
        user_message: str,
        attachments: List[str] = None,
    ) -> str:
        """
        Process a user message through the full agent loop.

        This is the main orchestration loop that mirrors Kimi's execution:
        1. Add user message
        2. Detect and inject skills
        3. Call LLM with tools
        4. Execute any tool calls
        5. Feed results back
        6. Repeat until done
        """
        self.last_active = time.time()

        # Build user message content
        user_content = user_message
        if attachments:
            attachment_text = "\n\n[Attached files: " + ", ".join(attachments) + "]"
            user_content += attachment_text

        self.messages.append({"role": "user", "content": user_content})

        # Skill detection and injection (if in agentic mode)
        mode_config = AGENT_MODES.get(self.mode, {})
        if mode_config.get("skill_loading", False):
            needed_skills = self._detect_skills(user_message)
            for skill_name in needed_skills:
                skill_content = await self._inject_skill(skill_name)
                if skill_content:
                    # Inject skill as a system message (context enrichment)
                    # Truncate to avoid context overflow
                    truncated = skill_content[:8000]
                    self.messages.append({
                        "role": "system",
                        "content": f"[Skill Loaded: {skill_name}]\n{truncated}",
                    })

        # Reset tool call counter for this turn
        self.tool_call_count = 0

        # Get available tools
        tools = get_all_tools()

        # Agent loop: call LLM, execute tools, repeat
        for iteration in range(self.max_tool_calls):
            # Check if client is available
            if not self.client:
                error_msg = "OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
                self.messages.append({"role": "assistant", "content": error_msg})
                return error_msg

            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=self.messages,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else None,
                    temperature=LLM_TEMPERATURE,
                    max_tokens=LLM_MAX_TOKENS,
                )
            except Exception as e:
                logger.error(f"LLM call failed: {e}\n{traceback.format_exc()}")
                error_msg = f"I encountered an error communicating with the language model: {str(e)}"
                self.messages.append({"role": "assistant", "content": error_msg})
                return error_msg

            choice = response.choices[0]
            message = choice.message

            # Check finish reason
            if choice.finish_reason == "stop" or not message.tool_calls:
                # Final response — no more tool calls
                content = message.content or ""
                self.messages.append({"role": "assistant", "content": content})
                logger.info(
                    f"Session {self.session_id}: completed after {self.tool_call_count} tool calls "
                    f"in {iteration + 1} iterations"
                )
                return content

            # Process tool calls
            # Add assistant message with tool calls to history
            assistant_msg = {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            }
            self.messages.append(assistant_msg)

            # Execute each tool call
            for tool_call in message.tool_calls:
                self.tool_call_count += 1
                self.total_tool_calls += 1

                # Check budget
                if self.max_tool_calls > 0 and self.tool_call_count > self.max_tool_calls:
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({
                            "error": f"Tool call budget exceeded ({self.max_tool_calls} calls per turn). "
                                     "Please respond to the user with what you have so far."
                        }),
                    })
                    continue

                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                logger.info(
                    f"[{self.session_id}] Tool #{self.tool_call_count}: "
                    f"{tool_name}({json.dumps(arguments)[:200]})"
                )

                # Execute the tool
                try:
                    result = await self.executor.execute(tool_name, arguments)
                except Exception as e:
                    logger.error(f"Tool execution error: {tool_name}: {e}")
                    result = json.dumps({
                        "error": f"Tool execution failed: {str(e)}",
                        "tool": tool_name,
                    })

                # Truncate result if needed
                if isinstance(result, str) and len(result) > MAX_OUTPUT_LENGTH:
                    result = result[:MAX_OUTPUT_LENGTH] + "\n... [output truncated]"

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result if isinstance(result, str) else json.dumps(result),
                })

        # If we exhausted iterations, return what we have
        final_content = (
            message.content
            or "I've reached the maximum number of iterations for this turn. "
               "Please continue the conversation to proceed."
        )
        self.messages.append({"role": "assistant", "content": final_content})
        return final_content

    async def process_message_stream(
        self,
        user_message: str,
        attachments: List[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a user message with streaming output.
        Yields events for real-time UI updates.

        Event types:
        - {"type": "thinking", "content": "..."} — agent is thinking
        - {"type": "tool_call", "tool": "...", "args": {...}} — tool being called
        - {"type": "tool_result", "tool": "...", "result": "..."} — tool result
        - {"type": "text", "content": "..."} — text chunk from LLM
        - {"type": "done", "content": "..."} — final response
        - {"type": "error", "content": "..."} — error occurred
        """
        self.last_active = time.time()

        # Build user message
        user_content = user_message
        if attachments:
            user_content += "\n\n[Attached files: " + ", ".join(attachments) + "]"
        self.messages.append({"role": "user", "content": user_content})

        # Skill injection
        mode_config = AGENT_MODES.get(self.mode, {})
        if mode_config.get("skill_loading", False):
            needed_skills = self._detect_skills(user_message)
            for skill_name in needed_skills:
                skill_content = await self._inject_skill(skill_name)
                if skill_content:
                    self.messages.append({
                        "role": "system",
                        "content": f"[Skill Loaded: {skill_name}]\n{skill_content[:8000]}",
                    })
                    yield {"type": "thinking", "content": f"Loading skill: {skill_name}"}

        self.tool_call_count = 0
        tools = get_all_tools()

        for iteration in range(self.max_tool_calls):
            # Check if client is available
            if not self.client:
                yield {"type": "error", "content": "OpenAI API key not configured. Set OPENAI_API_KEY environment variable."}
                return

            try:
                yield {"type": "thinking", "content": f"Thinking... (iteration {iteration + 1})"}

                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=self.messages,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else None,
                    temperature=LLM_TEMPERATURE,
                    max_tokens=LLM_MAX_TOKENS,
                )
            except Exception as e:
                yield {"type": "error", "content": str(e)}
                return

            choice = response.choices[0]
            message = choice.message

            if choice.finish_reason == "stop" or not message.tool_calls:
                content = message.content or ""
                self.messages.append({"role": "assistant", "content": content})
                yield {"type": "done", "content": content}
                return

            # Process tool calls
            assistant_msg = {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            }
            self.messages.append(assistant_msg)

            for tool_call in message.tool_calls:
                self.tool_call_count += 1
                self.total_tool_calls += 1
                tool_name = tool_call.function.name

                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                yield {
                    "type": "tool_call",
                    "tool": tool_name,
                    "args": arguments,
                    "call_id": tool_call.id,
                }

                try:
                    result = await self.executor.execute(tool_name, arguments)
                except Exception as e:
                    result = json.dumps({"error": str(e)})

                if isinstance(result, str) and len(result) > MAX_OUTPUT_LENGTH:
                    result = result[:MAX_OUTPUT_LENGTH] + "\n... [truncated]"

                yield {
                    "type": "tool_result",
                    "tool": tool_name,
                    "result": result[:500] if isinstance(result, str) else str(result)[:500],
                }

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result if isinstance(result, str) else json.dumps(result),
                })

        yield {
            "type": "done",
            "content": "Reached maximum iterations. Please continue to proceed.",
        }

    def get_history(self) -> List[Dict[str, Any]]:
        """Return conversation history (excluding system messages)."""
        return [
            msg for msg in self.messages
            if msg.get("role") in ("user", "assistant")
            and msg.get("content")
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Return session statistics."""
        return {
            "session_id": self.session_id,
            "mode": self.mode,
            "total_tool_calls": self.total_tool_calls,
            "loaded_skills": list(self.loaded_skills),
            "message_count": len(self.messages),
            "created_at": self.created_at,
            "last_active": self.last_active,
        }

    def reset(self):
        """Reset the session, keeping only the system prompt."""
        system_msg = self.messages[0] if self.messages else None
        self.messages = [system_msg] if system_msg else []
        self.tool_call_count = 0
        self.total_tool_calls = 0
        self.loaded_skills.clear()

    async def cleanup(self):
        """Cleanup resources (browser, E2B sandbox, etc.)."""
        await self.executor.cleanup()


# ═══════════════════════════════════════════════════════════════════════════
# Session Manager
# ═══════════════════════════════════════════════════════════════════════════

class SessionManager:
    """Manages multiple agent sessions with lifecycle management."""

    def __init__(self):
        self.sessions: Dict[str, AgentSession] = {}

    def get_or_create(self, session_id: str, mode: str = None) -> AgentSession:
        """Get existing session or create a new one."""
        if session_id not in self.sessions:
            self.sessions[session_id] = AgentSession(session_id, mode)
        return self.sessions[session_id]

    async def delete(self, session_id: str):
        """Delete a session and cleanup its resources."""
        if session_id in self.sessions:
            await self.sessions[session_id].cleanup()
            del self.sessions[session_id]

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions with their stats."""
        return [session.get_stats() for session in self.sessions.values()]

    async def cleanup_inactive(self, max_idle_seconds: int = 3600):
        """Cleanup sessions that have been idle for too long."""
        now = time.time()
        to_delete = [
            sid for sid, session in self.sessions.items()
            if now - session.last_active > max_idle_seconds
        ]
        for sid in to_delete:
            await self.delete(sid)
            logger.info(f"Cleaned up inactive session: {sid}")


# Global session manager
session_manager = SessionManager()

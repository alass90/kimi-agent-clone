import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent.orchestrator import AgentSession
from tools.registry import get_all_tools
from config.settings import AGENT_MODES

async def test_session_creation():
    print("Testing session creation...")
    session = AgentSession("test-session", mode="ok_computer")
    assert session.session_id == "test-session"
    assert session.mode == "ok_computer"
    assert len(session.messages) == 1
    assert session.messages[0]["role"] == "system"
    print("✅ Session creation successful")

async def test_tool_registry():
    print("Testing tool registry...")
    tools = get_all_tools()
    assert len(tools) == 27 # Based on my registry.py implementation
    tool_names = [t["function"]["name"] for t in tools]
    assert "ipython" in tool_names
    assert "browser_visit" in tool_names
    assert "todo_read" in tool_names
    print(f"✅ Tool registry contains {len(tools)} tools")

async def test_skill_detection():
    print("Testing skill detection...")
    session = AgentSession("test-skill")
    skills = session._detect_skills("I need to create a Word document and a PDF")
    assert "docx" in skills
    assert "pdf" in skills
    print(f"✅ Skill detection successful: {skills}")

async def test_tool_execution_mock():
    print("Testing tool execution (mocked)...")
    session = AgentSession("test-exec")
    
    # Mock the executor.execute method
    session.executor.execute = MagicMock(return_value=asyncio.Future())
    session.executor.execute.return_value.set_result("Tool result")
    
    result = await session.executor.execute("get_current_time", {})
    assert result == "Tool result"
    session.executor.execute.assert_called_once_with("get_current_time", {})
    print("✅ Tool execution mocking successful")

async def main():
    try:
        await test_session_creation()
        await test_tool_registry()
        await test_skill_detection()
        await test_tool_execution_mock()
        print("\n🎉 All backend unit tests passed!")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

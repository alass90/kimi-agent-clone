"""
Agent Configuration Settings
Mirrors Kimi's architecture: connectivity (tools) + cognition (skills + prompts)
Integrates E2B as cloud sandbox for code execution and shell.
"""
import os
from pathlib import Path

# ─── Paths ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"
OUTPUT_DIR = WORKSPACE_DIR / "output"
UPLOAD_DIR = WORKSPACE_DIR / "upload"
DEPLOY_DIR = WORKSPACE_DIR / "deploy"
SKILLS_DIR = BASE_DIR / "skills"
TOOLS_DIR = BASE_DIR / "tools"
STATIC_DIR = BASE_DIR / "static"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for d in [OUTPUT_DIR, UPLOAD_DIR, DEPLOY_DIR, SKILLS_DIR, STATIC_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── LLM Configuration ──────────────────────────────────────────────────
LLM_MODEL = os.getenv("LLM_MODEL", "moonshot-v1-auto")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "16384"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.moonshot.ai/v1")

# ─── E2B Sandbox Configuration ──────────────────────────────────────────
E2B_API_KEY = os.getenv("E2B_API_KEY", "")
E2B_TEMPLATE = os.getenv("E2B_TEMPLATE", "base")  # E2B sandbox template
E2B_TIMEOUT = int(os.getenv("E2B_TIMEOUT", "300"))  # Sandbox timeout in seconds
USE_E2B = bool(E2B_API_KEY)  # Auto-enable E2B if API key is set

# ─── Agent Modes ─────────────────────────────────────────────────────────
# Mirrors Kimi's dual-mode architecture
AGENT_MODES = {
    "base_chat": {
        "max_tool_calls_per_turn": 10,
        "persistent_workspace": False,
        "skill_loading": False,
        "description": "Conversational mode - fast responses, limited tool budget",
    },
    "ok_computer": {
        "max_tool_calls_per_turn": 0,  # 0 = unlimited
        "persistent_workspace": True,
        "skill_loading": True,
        "description": "Agentic mode - unlimited tools, skill injection, persistent workspace",
    },
}

DEFAULT_MODE = os.getenv("DEFAULT_MODE", "ok_computer")

# ─── Tool Budget & Limits ───────────────────────────────────────────────
MAX_EXECUTION_TIMEOUT = 600  # seconds (matches Kimi's 600000ms)
CODE_EXECUTION_TIMEOUT = 30  # seconds per code block
MAX_OUTPUT_LENGTH = 10000  # characters before truncation
MAX_FILE_WRITE_LENGTH = 100000  # max chars per write_file call
MAX_AGENT_ITERATIONS = 50  # max loops before forced stop

# ─── Browser Configuration ──────────────────────────────────────────────
BROWSER_HEADLESS = True
BROWSER_TIMEOUT = 30000  # ms
BROWSER_VIEWPORT_WIDTH = 1280
BROWSER_VIEWPORT_HEIGHT = 720
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# ─── Server Configuration ────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ─── Available Skills (mirrors Kimi's skill registry) ────────────────────
SKILL_REGISTRY = {
    "docx": {
        "description": "Word document creation, editing, and analysis using python-docx",
        "triggers": ["docx", "word", "document"],
    },
    "pdf": {
        "description": "PDF creation via HTML+Paged.js or LaTeX, PDF analysis and extraction",
        "triggers": ["pdf", "latex", "academic paper"],
    },
    "xlsx": {
        "description": "Spreadsheet manipulation, analysis, and creation with openpyxl",
        "triggers": ["xlsx", "excel", "spreadsheet", "csv"],
    },
    "webapp-building": {
        "description": "React webapp building with TypeScript, Tailwind, and deployment",
        "triggers": ["webapp", "website", "web app", "frontend"],
    },
    "slides": {
        "description": "Presentation design with McKinsey-style high-density slides",
        "triggers": ["slides", "presentation", "pptx", "powerpoint"],
    },
    "data_analysis": {
        "description": "Data analysis, visualization, and statistical modeling",
        "triggers": ["data analysis", "visualization", "chart", "graph", "statistics"],
    },
}

# ─── Data Sources (mirrors Kimi's datasource registry) ───────────────────
DATA_SOURCES = {
    "yahoo_finance": {
        "domain": "Financial",
        "coverage": "Stock prices, company financials, market data, historical quotes",
    },
    "world_bank": {
        "domain": "Economic",
        "coverage": "Global development indicators by country",
    },
    "world_bank_open_data": {
        "domain": "Economic",
        "coverage": "16,000+ global indicators (GDP, population, poverty rate, etc.)",
    },
    "arxiv": {
        "domain": "Academic",
        "coverage": "Scientific preprints across physics, CS, math, biology, etc.",
    },
    "google_scholar": {
        "domain": "Academic",
        "coverage": "Scholarly literature, citations, author profiles",
    },
}

# ─── Logging ─────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "agent.log"

"""Vercel Python ASGI entrypoint for the DuMate MCP connector."""

from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shopflow.mcp_server import app  # noqa: E402,F401

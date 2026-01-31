uv venv
uv sync
uv run mcp dev server.py
uv run mcp run server.py

產生 claude_desktop_config.json 
加入{"mcpServers": {}}

運行uv run fastmcp install claude-desktop server.py:mcp
uv run fastmcp run server.py:mcp
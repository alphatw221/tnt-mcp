FROM --platform=linux/x86-64 python:3.12-slim

# 複製 uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 先複製 dependency 檔案，利用 Docker layer cache
COPY pyproject.toml uv.lock ./

# 安裝依賴（不包含 dev 套件）
RUN uv sync --frozen --no-dev

# 複製原始碼
COPY server.py .
COPY tokens.json .

EXPOSE 8080

CMD ["uv", "run", "python", "server.py"]

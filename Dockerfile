FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4.10 /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (cache friendly)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy the rest of the application
COPY . .

# Expose port (chọn 8000 cho FastAPI hoặc 80 nếu bạn muốn chạy trực tiếp ở port 80)
EXPOSE 8000

# Start FastAPI with uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =========================================
# 1️⃣ Base image: official Python 3.11 slim
# =========================================
FROM python:3.11-slim AS base

# =========================================
# 2️⃣ Install UV (modern Python package manager)
# =========================================
RUN pip install --no-cache-dir uv

# =========================================
# 3️⃣ Set working directory
# =========================================
WORKDIR /app

# =========================================
# 4️⃣ Copy only project metadata first (for caching)
# =========================================
COPY pyproject.toml uv.lock ./

# =========================================
# 5️⃣ Install dependencies using UV
# =========================================
RUN uv sync --frozen --no-cache --no-dev

# =========================================
# 6️⃣ Copy the rest of your source code
# =========================================
COPY . .

# =========================================
# 7️⃣ Expose FastAPI port
# =========================================
EXPOSE 8000

# =========================================
# 8️⃣ Default command
# =========================================
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

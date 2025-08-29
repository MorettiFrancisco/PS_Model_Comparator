FROM python:3.11

EXPOSE 8000

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy only dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies with cache mount and suppress hardlink warning
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_LINK_MODE=copy uv sync --frozen

# Copy application code (separate layer to avoid reinstalling deps on code changes)
COPY . .

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
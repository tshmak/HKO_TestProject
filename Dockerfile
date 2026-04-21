FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen --no-install-project --no-dev

# Install the package
COPY app/ ./app/
COPY scripts/ ./scripts/
RUN uv sync --frozen --no-dev

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Expose Streamlit port
EXPOSE 8501

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "streamlit", "run", "scripts/streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]

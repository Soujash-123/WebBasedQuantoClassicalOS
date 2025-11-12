# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy both backend and ai_os requirements
COPY backend/requirements.txt ./backend/requirements.txt
COPY ai_os/requirements.txt ./ai_os/requirements.txt

# Install dependencies with increased timeout and retries
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --timeout=1000 --retries=5 -r ./backend/requirements.txt && \
    pip install --no-cache-dir --timeout=1000 --retries=5 -r ./ai_os/requirements.txt

# Copy the entire backend directory
COPY backend ./backend/
COPY ai_os ./ai_os/

# Expose port 5000
EXPOSE 5000

# Run uvicorn server with backend.main:app path
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

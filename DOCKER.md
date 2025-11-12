# Docker instructions for Web-Based Virtual OS

This project has been containerized with two service Dockerfiles and a `docker-compose.yml` to run the backend and frontend together.

Files provided
- `backend/Dockerfile` - Builds the FastAPI backend from `backend/requirements.txt`. Runs Uvicorn on port 8000.
- `frontend/Dockerfile` - Multi-stage build for the Vite React app. Builds with Node and serves the `dist` folder via nginx on port 80.
- `docker-compose.yml` - Starts `backend` and `frontend` services. Maps ports `8000` (backend) and `5173` (frontend -> nginx:80).

Quick start

1. Build and start both services:

```bash
# From project root
docker compose up --build
```

2. Open the frontend at `http://localhost:5173` and API docs at `http://localhost:8000/docs`.

Development notes
- The compose file mounts `./backend` and `./ai_os` into the backend container as read-only to make iterating on code easier locally. For production remove these mounts.
- To rebuild only one service, use:

```bash
docker compose build backend
docker compose build frontend
```

- To run detached:

```bash
docker compose up -d --build
```

Troubleshooting
- If a dependency fails to compile in the backend image, ensure the system build tools are present (the Dockerfile installs `build-essential`/`gcc`).
- If you prefer running the Vite dev server rather than a built nginx image, alter the frontend service to run `npm run dev` and map port `5173`.

# AI-Powered-Project-Management-SaaS

Backend-first MVP for an AI-powered project management SaaS built with FastAPI, MongoDB, and Redis.

## MVP 1 Included

- JWT authentication with access + refresh tokens
- Refresh token rotation with Redis-backed `jti` storage
- Role-based access scaffolding (`admin`, `manager`, `member`)
- Protected profile endpoint and admin-only endpoint
- FastAPI app lifecycle wiring for MongoDB and Redis
- Dockerized local runtime
- Auth-focused test suite

## Project Structure

```text
backend/
	app/
		api/v1/
		auth/
		core/
		db/
		models/
		schemas/
	tests/
docker-compose.yml
.env.example
```

## Quick Start (Docker)

1. Create an environment file:

```bash
cp .env.example .env
```

2. Start services:

```bash
docker compose up --build
```

3. Open API docs:

- http://localhost:8000/docs

## Backend Local Setup (without Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.lock
uvicorn app.main:app --reload
```

Ensure MongoDB and Redis are running and `.env` values point to reachable instances.

## Auth Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/users/me`
- `GET /api/v1/users/admin-only`

## Run Tests

```bash
cd backend
pytest -q
```

Tests expect MongoDB and Redis to be available.

## Lockfile Workflow

Backend dependencies are TOML-defined in [backend/pyproject.toml](backend/pyproject.toml) and pinned in:

- [backend/requirements.lock](backend/requirements.lock) (runtime)
- [backend/requirements-dev.lock](backend/requirements-dev.lock) (dev/test/CI)

Regenerate lock files after dependency changes:

```bash
cd backend
python3 -m piptools compile pyproject.toml --resolver=backtracking --strip-extras --generate-hashes -o requirements.lock
python3 -m piptools compile pyproject.toml --extra dev --resolver=backtracking --strip-extras --generate-hashes -o requirements-dev.lock
```

## Next Milestones

- Projects → Tasks → Comments domain modules
- Activity logging
- WebSocket real-time updates
- File uploads (S3-compatible)
- AI summarization jobs (Celery + OpenAI)
- Analytics endpoints
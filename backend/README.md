# Backend Package

FastAPI backend package for AI-Powered Project Management SaaS.

## Dependency Management

- Source of truth: `pyproject.toml`
- Runtime lock: `requirements.lock`
- Dev lock: `requirements-dev.lock`

Install for local development:

```bash
python -m pip install -r requirements-dev.lock
```

Regenerate lock files:

```bash
python3 -m piptools compile pyproject.toml --resolver=backtracking --strip-extras --generate-hashes -o requirements.lock
python3 -m piptools compile pyproject.toml --extra dev --resolver=backtracking --strip-extras --generate-hashes -o requirements-dev.lock
```

## Import Style

Use package-level imports where possible to keep imports consistent and readable.

Preferred examples:

```python
from app import app
from app.api import api_router
from app.core import Settings, get_settings
from app.db import get_database, get_redis_client
from app.auth import create_access_token, decode_token, require_role
from app.models import UserRole, UserPublic
from app.schemas import RegisterRequest, TokenResponse
```

Guidelines:

- Prefer importing from package roots (`app.core`, `app.db`, `app.auth`, etc.) when the symbol is exported.
- Import from module paths only when a symbol is intentionally internal and not exported via `__init__.py`.
- Keep imports explicit and grouped by standard library, third-party, then local package imports.

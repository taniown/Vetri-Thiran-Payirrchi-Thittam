# PocketSmart AI

A complete FastAPI + Jinja2 generative-AI budget recommendation assistant for:

- Home interiors
- Party planning
- Jewelry recommendations

## Features

- Registration and login
- JWT authentication
- SQLite persistence
- Home planner
- Party planner
- Jewelry planner
- Optional outfit image upload
- Gemini multimodal integration
- Local recommendation fallback
- Recommendation history
- Dashboard
- Responsive UI
- API validation
- Upload validation
- CORS
- Health endpoint
- Startup endpoint
- Automated tests
- Docker support
- VS Code debugging configuration

## Architecture

Frontend:

- Jinja2
- HTML
- CSS
- JavaScript

Backend:

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

Authentication:

- JWT
- Secure password hashing using scrypt

AI:

- Google Gemini
- Configurable Gemini model

Fallback:

- Local deterministic recommendation catalog

## Installation

Create a virtual environment.

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
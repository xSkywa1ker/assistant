.PHONY: up down logs migrate makemigration lint test seed doctor

up:
docker compose -f docker-compose.yaml up -d --build
docker compose -f docker-compose.yaml logs -f api

down:
docker compose -f docker-compose.yaml down -v

logs:
docker compose -f docker-compose.yaml logs -f

migrate:
docker compose -f docker-compose.yaml run --rm api poetry run alembic upgrade head

makemigration:
docker compose -f docker-compose.yaml run --rm api poetry run alembic revision --autogenerate -m "update"

lint:
poetry run ruff check ..
poetry run mypy ../backend/app

test:
poetry run pytest

seed:
docker compose -f docker-compose.yaml run --rm api poetry run python -m app.scripts.seed

doctor:
poetry run python -m app.scripts.doctor

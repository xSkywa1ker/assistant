FROM python:3.11-slim

WORKDIR /app

ENV POETRY_HOME=/opt/poetry
RUN pip install --no-cache-dir poetry

COPY pyproject.toml README.md ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

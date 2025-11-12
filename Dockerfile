FROM python:3.11-slim
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml .
RUN poetry install --no-interaction --no-ansi
COPY src ./src
CMD ["poetry","run","uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]

FROM python:3.11-bullseye

WORKDIR /

COPY poetry.lock pyproject.toml ./
COPY ./wordle ./wordle/

RUN pip install poetry
RUN poetry install

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "wordle.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
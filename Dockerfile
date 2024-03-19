FROM python:3.11-bullseye

WORKDIR /

COPY poetry.lock pyproject.toml start.sh ./
COPY ./wordle ./wordle/

RUN chmod +x /start.sh
RUN pip install poetry
RUN poetry install

EXPOSE $PORT

CMD ["./start.sh"]
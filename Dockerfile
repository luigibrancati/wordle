FROM python:3.11-bullseye

WORKDIR /

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /src

COPY ./src /src

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.12.1 as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12.1

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /app

EXPOSE $SERVER_PORT

CMD ["sh", "-c", "uvicorn server.__main__:app --host 0.0.0.0 --port $SERVER_PORT"]

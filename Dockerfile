FROM python:3.10-slim

WORKDIR /app
ENV PRISMO_CONFIG=/app/external/config_docker.json
COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY ./app /app

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "application:app"]
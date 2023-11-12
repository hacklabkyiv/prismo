FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "application:app"]
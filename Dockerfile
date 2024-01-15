FROM python:latest
WORKDIR /app
ENV PRISMO_CONFIG=/app/external/config_docker.json

RUN apt-get update && apt-get install -y jo git

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY ./app /app

# Download latest reader firmware
VOLUME ["/reader-firmware"]
RUN git clone https://github.com/hacklabkyiv/prismo-reader.git /reader-firmware

# We increase timeout here because flasher script takes long time to flash a reader device.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "application:app", "--timeout", "600", "--workers", "4"]
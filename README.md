![Imgur](https://i.imgur.com/V2k2seh.png)

PRISMO Admin Panel
===================

Prismo is fully open source and easy to install access system for control access of tools and equipment for maker
spaces.

The gold for the project to create a system which any maker space in the world can setup for own use. The system fully
open source, include the backend, readers firmware and PCB schema.

## Installation by docker

- Install docker on the host machine.
  Check [the tutorial for Raspberry Pi 4](https://github.com/codingforentrepreneurs/Pi-Awesome/blob/main/how-tos/Docker%20%26%20Docker%20Compose%20on%20Raspberry%20Pi.md)
- Create a folder `data` - the folder use for keep all persistent data, like a database.
- Run docker container:

```bash
docker run --name=prisom-app -p 5000:5000 --restart -v "$(pwd)/data/:/app/external/" vovochkastelmashchuk/prismo-app:0.0.10
```

## Installation by docker compose

```bash
version: '3'

services:
  prisom-app:
    image: vovochkastelmashchuk/prismo-app:0.0.10
    container_name: prisom-app
    ports:
      - "5000:5000"
    restart: always
    volumes:
      - "/home/pi/prismo/data/:/app/external/"
```

Add docker to autostart:

```bash
sudo systemctl enable docker
```

The application will be available on `http://localhost:5000`

#### Nginx setup

After installation of nginx(`sudo apt install nginx`) edit config `sudo vim /etc/nginx/conf.d/virtual.conf`

```bash
server {
   listen       80;
   server_name  prismo.local;

   location / {
       proxy_pass http://127.0.0.1:8000;
   }
}
```

This config should be placed as `prismo.conf` into `/etc/supervisor/conf.d/`
The application doesn't create any table in database, so you should create it manually. See section "Prepare database"

### Configuration

Config file name is `config.cfg`, the file located in the root directory of the project. Configs stored in YAML format.

```
logging:
    debug: Yes
    logfile: log.txt
    logsize_kb: 1000
    rolldepth: 3
```

## Development

### Preconditions

- Python 3.10+ with pip
- git
- supervisor(optional)

### Step-by-step installation

1. Clone the repository:

    ```sh
    git clone git@github.com:hacklabkyiv/prismo.git
    ```
   or by https:
    ```sh
    git clone https://github.com/hacklabkyiv/prismo.git
    ```

2. Install virtualenv in project's directory:

    ```sh
    $ python3 -m venv ./virtualenv
    ```

3. Activate virtual environment

    ```
    source ./virtualenv/bin/activate
    ```

4. Install required packages:

    ```sh
    pip3 install -r requirements.txt
    ```

5. Run for debugging and development: (it will reload app on code changes and enable debug mode)

```sh
export FLASK_APP=application.py
flask run --debug
```

By default, this should be run by Prismo admin process, but for debugging purpose you should run this commands by
yourself.

## Database

All information about the database is stored in [doc/database.md](docs/database.md) file.

### Logging

All logs are stored in `log.txt` file.

## API

The docs for API is stored in [docs/api.md](docs/api.md) file.

## Slack

Slack integration works with slack bot. You need to create slack bot in your slack workspace and get token for it.
Scope:

- chat:write
- files:write
- incoming-webhook

## Build docker image

The main target platform is `linux/arm64/v8` (Raspberry Pi 4). To build docker image for this platform you should use
buildx.

```
docker buildx create --use
docker buildx build --platform linux/arm64/v8 -t vovochkastelmashchuk/prismo-app:<version> --push .
```

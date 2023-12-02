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
docker run --name=prismo-app -p 80:5000 --restart always --detach -v "$(pwd)/data/:/app/external/" hacklabkyiv/prismo-app:0.1.7
```

Add docker to autostart:

```bash
sudo systemctl enable docker
```

The application ready to work and available on `http://localhost:5000`

### The reader firmware

The reader is a device which connected to the network and read RFID cards. The reader firmware is stored in
the `prismo-reader` [repository](https://github.com/hacklabkyiv/prismo-reader/tree/micropython_pn532).

### Configuration

Config file name is `config.cfg`, the file located in the root directory of the project. Configs stored in YAML format.

```
logging:
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

Execute `docker login` with hacklabkyiv credentials.
Execute this commands in the root directory of the project:

```
docker buildx create --use
docker buildx build --platform linux/arm64/v8 -t hacklabkyiv/prismo-app:<version> --push .
```

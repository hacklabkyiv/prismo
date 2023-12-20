![Imgur](https://i.imgur.com/V2k2seh.png)

PRISMO Admin Panel
===================

Prismo is a fully open-source and easy-to-install access system designed to 
control access to tools and equipment in maker spaces. Our goal is to 
create a system that any maker space in the world can easily set up for
its own use. The system is completely open-source, including the backend, 
reader firmware, and PCB schematics.


## Config handling
By default, PRISMO searches for a file named `config_default.json` inside 
the `/app` directory. This is suitable for development purposes, but for 
production deployments, you should specify your own configuration file and
pass its path as the `PRISMO_CONFIG` environment variable. When running
PRISMO in a Docker container, this path is specified in the `Dockerfile` 
like so:

```commandline
ENV PRISMO_CONFIG=/app/external/config_docker.json
```
In this example, the path `app/external/config_docker.json` is relative to 
the container's internal directory and mapped from an external directory 
(see the following paragraph for details).

## Running in `Docker`

Running PRISMO in a separate Docker container offers several advantages. It 
isolates data and ensures a well-defined environment for smooth operation. 
You can verify everything is ready for Docker deployment by running the
following command:
```commandline
$ docker build --no-cache -t prismo-app .
```
This command build a container and sets all environment variables from dockerfile.
```commandline
$ docker run --name=prismo-app -p 80:5000 --restart always --detach -v "$(pwd)/data/:/app/external/" prismo-app
```
This command runs the newly built container and starts the server on port 80. Note that on some systems, port 80 might be 
unavailable for non-privileged users. For development purposes, you can use 
the alternative mapping \`5000\:5000\` instead\.
As shown in the command, the `-v "</span>(pwd)/data/:/app/external/"` 
option mounts an external volume where you should store your `database.db` 
and `config_docker.json` files. This volume persists data and configuration 
outside the container, ensuring they are not lost even if the container is 
deleted.

**Additional Notes:**

- Remember to replace the placeholder values for environment variables like `DATABASE_URL` and `SECRET_KEY` with your actual settings in the example commands.

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
if you want to autorestart you app on Flask changes, you can do `export FLASK_DEBUG=1`. In case of `Import Error` run `pip3 install --upgrade watchdog`.
By default, this should be run by Prismo admin process, but for debugging purpose you should run this commands by
yourself.

## Database

All information about the database is stored in [doc/database.md](docs/database.md) file.

## API

The docs for API is stored in [docs/api.md](docs/api.md) file.

## Slack

Slack integration works with slack bot. You need to create slack bot in your slack workspace and get token for it.
Scope:

- chat:write
- files:write
- incoming-webhook

## Build final docker image and deployment

The main target platform is `linux/arm64/v8` (Raspberry Pi 4). To build docker image for this platform you should use
buildx.

Execute `docker login` with hacklabkyiv credentials.
Execute this commands in the root directory of the project:

```
docker buildx create --use
docker buildx build --platform linux/arm64/v8 -t hacklabkyiv/prismo-app:<version> --push .
```

Developers info
====================================

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
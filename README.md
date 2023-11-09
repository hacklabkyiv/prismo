![Imgur](https://i.imgur.com/V2k2seh.png)

PRISMO Admin Panel
===================

Prismo is fully open source and easy to install access system for control access of tools and equipment for maker
spaces.

The gold for the project to create a system which any maker space in the world can setup for own use. The system fully
open source, include the backend, readers firmware and PCB schema.

## Installation

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

5. Run app:

   ```sh
   export FLASK_APP=application.py && flask run
   ```

#### Supper visitor setup

Install supervisor

```bash
sudo apt install supervisor
```

Server autostart using `supervisor`

Supervisor is handy tool for autostart different scripts in userspace(supervisord.org). Here is example of configuration
script for this:

```
[program:prismo]
command=/home/prismo/prismo/.venv/bin/python /home/prismo/prismo/.venv/bin/gunicorn --bind 0.0.0.0:8000 application:app
directory=/home/prismo/prismo
startsecs=5
autostart=true
autorestart=true
redirect_stderr=true
stderr_logfile=/var/log/prismo/prismo.err.log
stdout_logfile=/var/log/prismo/prismo.out.log  
```

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

Run for debugging and development: (it will reload app on code changes and enable debug mode)

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

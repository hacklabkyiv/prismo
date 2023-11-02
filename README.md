![Imgur](https://i.imgur.com/V2k2seh.png)

PRISMO Admin Panel
===================

The goal of this web tool is provide one of the basic capabilities for hackerspaces, manage and monitor access to the
space and equipment.

## Installation

### Preconditions

- Python 3.6+ with pip
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

  ```
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

  ```
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
app:
    secret_key: some_secret_key
logging:
    debug: Yes
    logfile: log.txt
    logsize_kb: 1000
    rolldepth: 3
slack:
    token: <slack_token>
```

The secret key is used for session encryption. We strongly recommend to generate random values for the secret key.

### Add admin user

After installation and start the application, visit application web page. You wil redirected to create admin user page.
Fill the form and click "Create admin user" button. After that, you will be redirected to login page. Use your
credentials to login.

The application redirect you to admin create page only in case if there is no admin users in database.

### Add admin user manually

You can also add more admin users manually. To do this, you need to insert new record into `admins` table in database.
Our system can work with several admins. But it is not fully supported features, we don't have admin management page,
logs for admin actions, etc. In case when you add several admins, you take responsibility and risks.

```bash
INSERT INTO admins (username, password) VALUES ('admin', '<hashed admin password>');
```

To generate hashed password, you can use `hash_password.py` script.

- Modify the salt in `hash_password.py` to match the salt in your `config.cfg`
- Modify the password in `hash_password.py` to match the password you want to hash

The script will print the hashed password to the console. Copy this value and insert it into the database.

## Development

Run for debugging and development: (it will reload app on code changes and enable debug mode)

```sh
export FLASK_APP=application.py
flask run --debug
```

By default, this should be run by Prismo admin process, but for debugging purpose you should run this commands by
yourself.

## Database

All information about the database is stored in `docs/database.md` file.

### Logging

All logs are stored in `log.txt` file.

## API for readers

#### Get all users with access to device

GET: `/device/user_with_access/<device_id>`

#### User start work with device

POST: `/device/start_work/<device_id>/<user_key>`

#### User stop work with device

POST: `/device/stop_work/<device_id>/<user_key>`

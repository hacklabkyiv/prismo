![Imgur](https://i.imgur.com/V2k2seh.png)

PRISMO Admin Panel
===================

The goal of this webtool is provide basic management capabilities for hackerspaces, like:

1. Presence management basing on MAC address monitoring
2. RFID access system management
3. Payments monitoring
4. Internal information storage(wiki based)

Installation
============
1. Install virtualenv in project's directory:
	```sh
    $ virtualenv hackadmin
   ```
2. Install required packages:
	```sh
    $ pip3 install -r requirements.txt
   ```
3. Run app:
	```sh
    $ export FLASK_APP=application.py 
    $ flask run
   ```
table.sql contains create statements for database tables

Configuration
=============

Currently config is stored in YAML file. Example of config:

```
# Example config file
logging:
    debug: Yes
    logfile: log.txt
    logsize_kb: 1000
    rolldepth: 3
```

path to config file is set in `applicaiton.py`. By default, config file name is `config.cfg`


#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Core of Hacklab Admin Panel

@author: Artem Synytsyn
"""

from flask import Flask, render_template, request, abort
import time
import json
import yaml
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from collections import namedtuple
from threading import Thread
from os.path import getmtime
import datetime
import psycopg2 as psycopg
import requests
import txt_log_reader

try:
    from yaml import CLoader as Loader, CDumper
except ImportError:
    from yaml import Loader

# Configuration file
CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.cfg')

# Initial setup
try:
    cfg = yaml.load(open(CONFIG_FILE, 'r'), Loader=Loader)
except IOError as e:
    logger.error("Config file not found!")
    logger.error("Exception: %s" % str(e))
    sys.exit(1)

LATEST_KEY_FILE = cfg['data']['latest-key-file']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
logger = logging.getLogger(__name__)
if cfg['logging']['debug'] is True:
    app.config['DEBUG'] = True
    logging.basicConfig(level=logging.DEBUG)
    # Create logger to be able to use rolling logs
    logger.setLevel(logging.DEBUG)
    log_handler = RotatingFileHandler(cfg['logging']['logfile'],mode='a',
                                      maxBytes=int(cfg['logging']['logsize_kb'])*1024,
                                      backupCount=int(cfg['logging']['rolldepth']),
                                      delay=0)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

def get_latest_key_info():
    try:
        with open(LATEST_KEY_FILE, 'r') as f:
            key_value = f.read()
    except FileNotFoundError:
        key_value = '<absent>'
    # Getting modification datetime
    try:
        mod_time = getmtime(LATEST_KEY_FILE)
        mod_time_converted = datetime.datetime.fromtimestamp(
                mod_time).strftime('%Y-%m-%d %H:%M:%S')
    except OSError:
        mod_time_converted = '<unknown>'
    return ("%s updated at: %s" % (key_value, mod_time_converted))


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        conn = psycopg.connect(user = cfg['data']['user'],
                                  password = cfg['data']['password'],
                                  host = cfg['data']['host'],
                                  port = cfg['data']['port'],
                                  database = cfg['data']['name'])
    except (Exception, psycopg.DatabaseError) as error :
        logger.error("Error while connecting to PostgreSQL: %s" % error)
        abort(500)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    all_column_names = list(description[0] for description in
                          cursor.description)

    # Get column names for devices, needed access control. Exclude the others
    access_info_columns = list(filter(lambda value: not value in ['id', 'name', 'key', 'last_enter'], all_column_names))
    cursor.execute('SELECT id, name, key, last_enter FROM users')
    user_info = cursor.fetchall()
    cursor.execute('SELECT %s FROM users'
                        % ','.join(access_info_columns))
    user_access_info = cursor.fetchall()
    template_data = zip(user_info, user_access_info)

    # Updating latest key information
    latest_key_info = get_latest_key_info()
    # Parsing data from frontend: editing access, user additioin and deletion
    if request.method == 'POST':
        operation = request.form['operation']
        if operation == 'edit':
            user_id = request.form['id']
            user_device = request.form['device']
            user_state = request.form['state']
            if user_state == 'true':
                user_state = '1'
            elif user_state == 'false':
                user_state = '0'

            logger.info('Updated user info: %s, %s, %s' % (user_id,
                         access_info_columns[int(user_device)],
                         user_state))
            command = "UPDATE users SET %s = '%s' WHERE id = %s" \
                % (access_info_columns[int(user_device)], user_state,
                   user_id)
            cursor.execute(command)
            conn.commit()
        elif operation == 'delete':
            user_id = request.form['id']
            user_device = request.form['device']
            user_state = request.form['state']
            cursor.execute('DELETE FROM users WHERE id=%s', (user_id, ))
            conn.commit()
            logger.info('User deleted, id: %s' % user_id)
        elif operation == 'add':
            user_name = request.form['nick']
            user_key = request.form['key']
            cursor.execute('INSERT INTO users(name, key) VALUES(%s, %s)',(user_name, user_key))
            conn.commit()
            logger.info('User added: %s, %s' % (user_name, user_key))
    cursor.close()
    conn.close()
    return render_template('index.html', data=template_data,
                           column_names=all_column_names,
                           latest_key_info=latest_key_info)

@app.route("/log_viewer")
def log_reader_wrapper():
    return txt_log_reader.render_logs_to_html()

import os

import slack_notifications as slack
import yaml
from yaml import Loader

CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../config.cfg')
cfg = yaml.load(open(CONFIG_FILE, 'r'), Loader=Loader)

if __name__ == '__main__':
    slack = slack.Slack(token=cfg['slack']['token'])

    print(cfg['slack']['token'])
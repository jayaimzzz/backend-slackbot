#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A slackbot that responds to commands.
This uses the Slack RTM (Real Time Messaging) API.
Required environment variables (example only, these are not real tokens).
Get these from the Slack account settings that you are connecting to.
   BOT_USER_ID = 'U20981S736'
   BOT_USER_TOKEN = 'xoxb-106076235608-AbacukynpGahsicJqugKZC'
"""
__author__ = 'jenjam aka jhoelzer and jayaimzzz'

import time
import signal
import logging

BOT_NAME = 'magic-eight-bot'
BOT_CHAN = '#magic-eight-test'

int_ = 2  # loop pause interval (seconds)
run_flag = True
logger = logging.getLogger(__name__)


def config_logger():
    """Setup logging configuration"""
    global logger
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s:%(message)s')
    file_handler = logging.FileHandler("filelog.log")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def command_loop(bot):
    """Process incoming bot commands"""
    print("hello")
    # pass


def signal_handler(sig_num, frame):
    global logger
    logger.info("signal number: {}".format(sig_num))
    if sig_num == 2:
        global run_flag
        run_flag = False


class SlackBot:

    def __init__(self, bot_user_token, bot_id=None):
        """Create a client instance"""
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __enter__(self):
        """Implement this method to make this a context manager"""
        pass

    def __exit__(self, type, value, traceback):
        """Implement this method to make this a context manager"""
        pass

    def post_message(self, msg, chan=BOT_CHAN):
        """Sends a message to a Slack Channel"""
        pass

    def handle_command(self, raw_cmd, channel):
        """Parses a raw command string from the bot"""
        pass


def main():
    config_logger()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    bot = SlackBot("dontknow", "what") # TODO 
    while run_flag:
        command_loop(bot)
        time.sleep(int_)


if __name__ == '__main__':
    main()

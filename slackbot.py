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
import os
from slackclient import SlackClient
import re


BOT_USERNAME = os.environ.get("SLACK_BOT_USER")
BOT_USER_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
BOT_NAME = 'magic8bot'
BOT_CHAN = '#magic-eight-test'

int_ = 2  # loop pause interval (seconds)
run_flag = True
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
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
    command, channel = bot.parse_bot_commands(bot.slack_client.rtm_read())
    print(command, channel)


def signal_handler(sig_num, frame):
    global logger
    logger.info("signal number: {}".format(sig_num))
    if sig_num == 2:
        global run_flag
        run_flag = False


class SlackBot:

    def __init__(self, bot_user_token, bot_id=None):
        """Create a client instance"""
        self.slack_client = SlackClient(bot_user_token)
        self.bot_name = BOT_NAME
        self.bot_id = self.get_bot_id()

        if self.bot_id is None:
            exit("Error, could not find " + str(self.bot_name))

    def get_bot_id(self):
        api_call = self.slack_client.api_call("users.list")
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == self.bot_name:
                    # return "<@" + user.get('id') + ">"
                    return user.get('id')
            return None

    def parse_bot_commands(self, slack_events):
        # print(slack_events)
        for event in slack_events:
            if event.get("type") == "message" and not "subtype" in event:
                user_id, message = self.parse_direct_mention(event.get("text"))
                print(user_id, self.bot_id)
                if user_id == self.bot_id:
                    print("inside logic")
                    return message, event.get("channel")
        return None, None

    def parse_direct_mention(self, message_text):
        matches = re.search(MENTION_REGEX, message_text)
        if matches:
            return matches.group(1), matches.group(2).strip()
        else:
            return (None, None)

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
    bot = SlackBot(BOT_USER_TOKEN)
    if bot.slack_client.rtm_connect(with_team_state=False):
        print("{} connected and running!".format(bot.bot_name))
        while run_flag:
            command_loop(bot)
            time.sleep(int_)


if __name__ == '__main__':
    main()

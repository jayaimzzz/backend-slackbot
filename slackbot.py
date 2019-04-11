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

import time
import signal
import logging
import os
from slackclient import SlackClient
import re
import requests
import string
from dotenv import load_dotenv

__author__ = 'jenjam aka jhoelzer and jayaimzzz'

load_dotenv()

SLACK_BOT_ICON = 'https://raw.githubusercontent.com/jayaimzzz/backend-slackbot/dev/images/magic-8-bot.png'
MW_ICON = "https://dictionaryapi.com/images/info/branding-guidelines/MWLogo_LightBG_120x120_2x.png"
BOT_USERNAME = os.environ.get("SLACK_BOT_USER")
BOT_USER_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
BOT_NAME = 'magic8bot'
BOT_CHAN = 'CCD7MHJD8'
MW_API = 'https://dictionaryapi.com/api/v3/references/thesaurus/json/'
MERRIAM_WEBSTER_API_KEY = os.environ.get("MERRIAM_WEBSTER_API_KEY")


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
    if command:
        if command == "help":
            bot.help(channel)
        elif command == "exit":
            bot.exit(channel)
        elif command == "ping":
            bot.ping(channel)
        else:
            bot.answer_question_and_get_synonyms(command, channel)


def signal_handler(sig_num, frame):
    global logger
    logger.info("signal number: {}".format(sig_num))
    if sig_num == 2:
        global run_flag
        run_flag = False


def fetch_yes_no():
    '''Use the Yes No api to fetch a yes or no and image'''
    try:
        r = requests.get("https://yesno.wtf/api")
        data = r.json()
        return data
    except requests.exceptions.RequestException as err:
        print(err)
        return None


def get_longest_word(text):
    '''Find the longest word out a string of text'''
    result = ""
    text = text.split()
    for word in text:
        if len(word) > len(result):
            result = word
    exclude = set(string.punctuation)
    result = ''.join(ch for ch in result if ch not in exclude)
    return result


def get_synonyms(word):
    '''use a thesaurus API to find all synonyms'''
    try:
        key = MERRIAM_WEBSTER_API_KEY
        url = "{}{}?key={}".format(MW_API, word, key)
        r = requests.get(url)
        data = r.json()
        try:
            synonyms = data[0].get("meta").get("syns")[0]
            if len(synonyms) > 1:
                synonyms[-1] = "and " + synonyms[-1]
            return ", ".join(synonyms)
        except Exception:
            logger.error(f"No synonyms found for {word}")
            return None
    except requests.exceptions.RequestException as err:
        logger.error(err)
        return None


class SlackBot:

    def __init__(self, bot_user_token, bot_id=None):
        """Create a client instance"""
        self.slack_client = SlackClient(bot_user_token)
        self.bot_name = BOT_NAME
        self.bot_id = self.get_bot_id()
        self.start_time = time.time()

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
            if event.get("type") == "message" and "subtype" not in event:
                user_id, message = self.parse_direct_mention(event.get("text"))
                if user_id == self.bot_id:
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

    def help(self, channel):
        message = '''
        Magic Eight Bot can answer all your yes or no questions.
        Simply end your question with a "?".
        Use the "exit" keyword to shut me down.
        Use the "ping" keyword to check my status.
        I am also an excellent thesaurus.
        '''
        self.post_message(message, channel)

    def ping(self, channel):
        stime = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(self.start_time)
            )
        message = f"{self.bot_name} has been running since {stime}."
        self.post_message(message, channel)

    def exit(self, channel):
        self.post_message(f'{self.bot_name} is exiting. Goodbye.', channel)
        global run_flag
        run_flag = False

    def post_message(self, msg, channel, attachments=None, icon_url=SLACK_BOT_ICON):
        """Sends a message to a Slack Channel"""
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg,
            attachments=attachments,
            icon_url=icon_url
        )

    def answer_question_and_get_synonyms(self, command, channel):
        word = get_longest_word(command)
        synonyms = get_synonyms(word)
        if command.endswith("?"):
            data = fetch_yes_no()
            text = data.get("answer").title()
            img = data.get("image")
            attachments = [{"title": text, "image_url": img}]
            self.post_message(command, channel, attachments)
        else:
            message = 'To ask a question, use a "?" at the end.'
            self.post_message(message, channel)
        if synonyms:
            t_message = "Other words for *{}* are {}.".format(word, synonyms)
            attachments = [{"title": "Thesaurus", "text": t_message, "footer": "Synonyms provided by Marriam-Webster", "footer_icon": MW_ICON}]
            self.post_message("", channel, attachments)

    def handle_command(self, raw_cmd, channel):
        """Parses a raw command string from the bot"""
        pass


def main():
    config_logger()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    bot = SlackBot(BOT_USER_TOKEN)
    if bot.slack_client.rtm_connect(with_team_state=False):
        logger.info("{} connected and running!".format(bot.bot_name))
        bot.post_message(f"{bot.bot_name} is online.", BOT_CHAN)
        while run_flag:
            command_loop(bot)
            time.sleep(int_)


if __name__ == '__main__':
    main()

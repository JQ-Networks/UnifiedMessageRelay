import time
import logging

from collections import namedtuple

from utils import *
import global_vars
from command import *
from cqsdk import CQBot, CQAt, CQImage, RcvdPrivateMessage, RcvdGroupMessage,\
    SendGroupMessage, GetGroupMemberList, RcvGroupMemberList
from telegram.ext import Updater, CommandHandler, InlineQueryHandler,\
    ConversationHandler, RegexHandler, MessageHandler, Filters, dispatcher
from telegram.error import BadRequest, TimedOut, NetworkError
import telegram
import os
import traceback
from PIL import Image
from configparser import ConfigParser
from urllib.request import urlretrieve
import json
import re
from cq_utils import *
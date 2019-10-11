#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Everything is stuck here.
"""

import aiohttp
import numpy
import os
import pprint
import requests
import sys

from bs4 import BeautifulSoup
from flask import Flask, request, redirect, jsonify, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# class IllegalParameter(HTTPException):
#     code = 400
#     description = 'ILLIGAL PARAMETER'

def decorate_args(func):
    """
    Decorator that removes the space between the last name and the name.
    """
    def or_dec_sepalate(*args, **kwargs):
        try:
            names = str(args[0]).replace(" ", "")
            func(names)
        except Exception:
            abort(404)
    return or_dec_sepalate


@app.errorhandler(404)
def no_such_human_pages(error):
    return "No such file or direcotory"

if __name__ == "__main__":
    FLASK_HOST = str(os.getenv("FLASK_HOST", "0.0.0.0"))
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG_MODE = True

    # app.logger.disabled = False
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG_MODE)

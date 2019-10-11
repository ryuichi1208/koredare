#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Everything is stuck here.
"""

import aiohttp
import datetime
import itertools
import numpy
import os
import pprint
import requests
import sys

from bs4 import BeautifulSoup
from collections import OrderedDict
from flask import Flask, request, redirect, jsonify, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

app = Flask(__name__)

LINE_BOT_ACCESS_TOKEN = os.getenv("LINE_BOT_ACCESS_TOKEN", None)
LINE_BOT_CHANNEL_SECRET = os.getenv("LINE_BOT_CHANNEL_SECRET", None)

HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME", None)

# class IllegalParameter(HTTPException):
#     code = 400
#     description = 'ILLIGAL PARAMETER'

linebot_api = LineBotApi(LINE_BOT_ACCESS_TOKEN)
handler = WebhookHandler(LINE_BOT_CHANNEL_SECRET)
if LINE_BOT_ACCESS_TOKEN is None or LINE_BOT_CHANNEL_SECRET is None:
    app.logger.warn("Error : not set token...")
    sys.exit(1)


def call_func_time(func):
    def _wrapLog(*args, **kwargs):
        print(
            datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
            "call : ",
            func.__name__,
        )
        func(*args, **kwargs)
    return _wrapLog


@call_func_time
def exec_http_requests(url: str):
    app.logger.info("request url " + url)
    try:
        res = requests.get(url)
        if res.status_code == 404:
            return None
        return res.text
    except requests.exceptions.MissingSchema:
        return None


@call_func_time
def parse_html_file(res: str):
    pass


@call_func_time
def down_load_image(url: str):
    pass


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


@decorate_args
def url_generator(name: str):
    base_url = "https://ja.wikipedia.org/wiki"
    url = f"{base_url}/{name}"
    res = exec_http_requests(url)
    return "aaa"


@app.route("/_check/status")
@call_func_time
def status_check():
    status = {
        "date": datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
        "status": "ok",
    }
    app.logger.info(status["status"])
    return jsonify(OrderedDict(status))


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "ok"


@call_func_time
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    rev_message = url_generator(event.message.text)
    app.logger.info("Recv message " + event.message.text)

    # linebot_api.reply_message(
    #     event.reply_token, TextSendMessage(text="aaa")
    # )

    image = {
        "image_url": f"{HEROKU_APP_NAME}/static/Sample.png",
        "preview_image_url": f"{HEROKU_APP_NAME}/static/Sample.png",
    }

    image_message = ImageSendMessage(
        original_content_url=image["image_url"],
        preview_image_url=image["preview_image_url"],
    )

    linebot_api.reply_message(event.reply_token, image_message)


@app.errorhandler(404)
def no_such_human_pages(error):
    return "No such file or direcotory"


if __name__ == "__main__":
    FLASK_HOST = str(os.getenv("FLASK_HOST", "0.0.0.0"))
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG_MODE = True

    # app.logger.disabled = False
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG_MODE)

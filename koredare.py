#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Everything is stuck here.
The images are downloaded from wikipedia.
"""

import aiohttp
import datetime
import itertools
import numpy
import os
import pprint
import requests
import shutil
import sys
import urllib.parse

from bs4 import BeautifulSoup
from collections import OrderedDict
from flask import Flask, request, redirect, jsonify, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

app = Flask(__name__)
"""
 * Serving Flask app "hello.py" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 150-239-588
"""

LINE_BOT_ACCESS_TOKEN = os.getenv("LINE_BOT_ACCESS_TOKEN", None)
LINE_BOT_CHANNEL_SECRET = os.getenv("LINE_BOT_CHANNEL_SECRET", None)

HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME", None)
HEROKU_IMAGE_DOWNDLOADS_DIR = os.getenv("HEROKU_IMAGE_DOWNDLOADS_DIR", "static")

# class IllegalParameter(HTTPException):
#     code = 400
#     description = 'ILLIGAL PARAMETER'

linebot_api = LineBotApi(LINE_BOT_ACCESS_TOKEN)
handler = WebhookHandler(LINE_BOT_CHANNEL_SECRET)
if LINE_BOT_ACCESS_TOKEN is None or LINE_BOT_CHANNEL_SECRET is None:
    app.logger.warn("Error : not set token...")
    sys.exit(1)


class self_logger(object):
    """
    Logging class for normal processing of flasks.
    Check heroku log as standard output is picked up.
    """

    def __init__(self, log_level, message):
        self.log_level = log_level
        self.message = message

    def log_print(self):
        log = f"{[self.log_level]}: {message}"
        print(log)


def call_func_time(func):
    """
    Collator for measuring function call time.
    """

    def _wrapLog(*args, **kwargs):
        print(
            datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
            "call : ",
            func.__name__,
        )
        func(*args, **kwargs)

    return _wrapLog


@call_func_time
def exec_http_requests(url: str, headers: dict = {}):
    """
    A function for issuing http requests.
    Responsibility is sent to the caller since only 404 is handled after execution.
    """
    app.logger.info("request url " + url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5)",
        "Keep-Alive": {"timeout": 15, "max": 100},
    }
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 404:
            return 1
        parse_html_file(res.text)
    except requests.exceptions.MissingSchema:
        return 1


@call_func_time
def parse_html_file(res, name="阿部 寛"):
    soup = BeautifulSoup(res, "lxml")
    image_list_org = soup.find_all("a", attrs={"class": "image"})
    image_list = [
        image_path for image_path in image_list_org if image_path.get("title") == name
    ]
    print("img", image_list)

    if image_list is not None:
        image_url = image_list[0].find("img").get("srcset").split(",")[1].split()
        url = "https:" + image_url[0]
        print(url)
        down_load_image(url)
    else:
        print("No such image file...")


@call_func_time
def down_load_image(url: str):
    self_logger("INFO", url)
    image_bin = requests.get(url, stream=True)

    # response = requests.get(url, allow_redirects=False, timeout=timeout)
    # if response.status_code != 200:
    #     e = Exception("HTTP status: " + response.status_code)
    #     raise e


    if image_bin.status_code == 200:
        # Download in raw.
        with open("static/test.jpg", "wb") as f:
            image_bin.raw.decode_content = True
            shutil.copyfileobj(image_bin.raw, f)
    else:
        """
        Traceback (most recent call last):
          File "requests/models.py", line 832, in raise_for_status
            raise http_error
        requests.exceptions.HTTPError: 404 Client Error

        If the request exceeds the configured maximum number of redirects,
        a TooManyRedirects exception is raised.
        """
        abort(400)


def make_filename(base_dir, number, url):
    """
    Create a file name to save the file.
    Todo: generate a file name that matches the extension
    """
    ext = os.path.splitext(url)[1]
    filename = number + ext

    fullpath = os.path.join(base_dir, filename)
    return fullpath


def decorate_args(func):
    """
    Decorator that removes the space between the last name and the name.
    """

    def or_dec_sepalate(*args, **kwargs):
        try:
            names = str(args[0]).replace(" ", "")
            names_enc = urllib.parse.quote(names)
            func(names_enc)
        except Exception:
            abort(404)

    return or_dec_sepalate


@decorate_args
def url_generator(name: str):
    base_url = "https://ja.wikipedia.org/wiki"
    url = f"{base_url}/{name}"
    print(url)
    if exec_http_requests(url) == 1:
        abort(404)


@app.route("/_check/status")
@call_func_time
def status_check():
    """
    Endpoint for life and death monitoring.
    """
    status = {
        "date": datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
        "status": "ok",
    }
    app.logger.info(status["status"])
    return jsonify(OrderedDict(status))


@app.route("/callback", methods=["POST"])
def callback():
    """
    Callback function for sending a message.
    """
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
    """
    Linebot's main processing function.
    Searching and saving images are processed in different places.
    """
    rev_message = url_generator(event.message.text)
    app.logger.info("Recv message " + event.message.text)

    # linebot_api.reply_message(
    #     event.reply_token, TextSendMessage(text="aaa")
    # )

    url_generator("阿部 寛")

    image = {
        "image_url": f"{HEROKU_APP_NAME}/static/test.jpg",
        "preview_image_url": f"{HEROKU_APP_NAME}/static/test.jpg",
    }

    image_message = ImageSendMessage(
        original_content_url=image["image_url"],
        preview_image_url=image["preview_image_url"],
    )

    linebot_api.reply_message(event.reply_token, image_message)


@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
def no_such_human_pages(error):
    """
    Error handling process when 404 occurs.
    """
    return "No such file or direcotory"

def __init(obj, org, bk):
    pass
    # with open(urls_txt, "r") as fin:
    #     for line in fin:
    #         url = line.strip()
    #         filename = make_filename(images_dir, idx, url)

    #         print "%s" % (url)
    #         try:
    #             image = download_image(url)
    #             save_image(filename, image)
    #             idx += 1
    #         except KeyboardInterrupt:
    #             break
    #         except Exception as err:
    #             print "%s" % (err)


if __name__ == "__main__":
    FLASK_HOST = str(os.getenv("FLASK_HOST", "0.0.0.0"))
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG_MODE = True

    # app.logger.disabled = False
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG_MODE)

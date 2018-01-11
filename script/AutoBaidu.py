#!/usr/bin/env  python
# coding=utf8

import os
import sys
import imp

imp.reload(sys)

import subprocess
import pytesseract
import urllib
from PIL import Image, ImageOps

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))

MAX_RETRY_TIME = 3

SCREEN_SHOT_PATH = "/storage/sdcard0/Pictures/hero/screenshot.png"

LOCAL_SCREEN_PATH = '{}/shot.png'.format(ROOT)
#

# 百万英雄
MILLION_HERO = 1

# 芝士超人
CHESS_HERO = 2

# 冲顶大会
GO_TOP = 3

MODE = MILLION_HERO


def run_command(cmd):
    retry = 0
    while retry < MAX_RETRY_TIME:
        status, output = subprocess.getstatusoutput(cmd)
        if status != 0:
            retry += 1
            continue
        return status, output


def mac_capture():
    if (MODE == MILLION_HERO):
        # # 百万英雄
        cmd = "screencapture -R 500,165,410,390 {}".format(LOCAL_SCREEN_PATH)
    elif (MODE == GO_TOP):

        cmd = "screencapture -R 500,175,410,360 {}".format(LOCAL_SCREEN_PATH)
    else:
        # # 芝士超人
        cmd = "screencapture -R 500,170,410,360 {}".format(LOCAL_SCREEN_PATH)

    status, output = run_command(cmd)
    return status


def recognition():
    file = Image.open(LOCAL_SCREEN_PATH)
    question_box = file.crop((0, 10, file.size[0], file.size[1]))
    question = pytesseract.image_to_string(question_box, lang='chi_sim')
    if (MODE != CHESS_HERO):
        question = question[question.index(u'.') + 1:]
    return question, file


# def baidu_recognize():
#     image = get_file_content()
#     options = {}
#     options["language_type"] = "CHN_ENG"
#     options["detect_direction"] = "true"
#     options["detect_language"] = "true"
#     options["probability"] = "true"
#
#     """ 带参数调用通用文字识别, 图片参数为本地图片 """
#     return client.basicGeneral(image, options)
#
#
# def get_file_content():
#     with open(LOCAL_SCREEN_PATH, 'rb') as fp:
#         return fp.read()


def splitQA(question, aNum=3):
    # print(question)
    questions = question.splitlines()
    res = []
    for i in questions:
        if (i == '' or i == '\n'):
            continue
        res.append(i)
    q = ""
    answer = []
    res_len = len(res)
    for index in range(res_len):
        if (aNum - 1 - index >= 0):
            str = res[res_len - 1 - index]
            answer.append(str.replace("_", "一").replace(" ", ""))
        else:
            q = (res[res_len - 1 - index] + q).replace(" ", "")
    answer.reverse()
    return q, answer


def search(question):
    params = {'wd': question}

    url = u"https://www.baidu.com/s?" + urllib.parse.urlencode(params)
    cmd = u'open "{}"'.format(url)
    run_command(cmd=cmd)


def analyze(question, answers):
    '''
    分析答案概率
    '''
    url = u"http://www.baidu.com/s?wd={}".format(question)
    res = requests.get(url)
    res.raise_for_status()

    answer_res = []
    search_res = res.text.replace("<em>", "").replace("</em>", "")
    # str(time.time())
    #fo = open("log.txt", "wb")
    #fo.write(search_res.encode())
    #fo.close()
    for answer in answers:
        if (answer == '' or answer == '\n'):
            continue
        print(answer + " : " + str(search_res.count(answer)))
    return answer_res


def main():
    import time

    begin = time.time() * 1000

    mac_capture()

    captime = time.time() * 1000

    question, file = recognition()

    recotime = time.time() * 1000

    q, anwser = splitQA(question)

    search(q)

    print(q)

    analyze(question, anwser)

    analtime = time.time() * 1000

    end = time.time() * 1000

    # print(" cap time: ", (captime - begin), " ms")
    #
    # print("reco time: ", (recotime - begin), " ms")
    #
    # print("anal time: ", (analtime - begin), " ms")

    print("cost time: ", (end - begin), " ms")


if __name__ == '__main__':
    main()

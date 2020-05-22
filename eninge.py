#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import sys
import base64
import time

IS_PY3 = sys.version_info.major == 3

if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    timer = time.perf_counter
else:
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode
    if sys.platform == "win32":
        timer = time.clock
    else:
        # On most other platforms the best timer is time.time()
        timer = time.time

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

#填写百度控制台中相关开通了“音频文件转写”接口的应用的的API_KEY及SECRET_KEY
API_KEY = 'uhqDHRX4SeG3qKDeKK4QDMk5'
SECRET_KEY = 'pFqlRIpbegdClyyVth0kAsw5mIgpGriS'

"""  获取请求TOKEN start 通过开通音频文件转写接口的百度应用的API_KEY及SECRET_KEY获取请求token"""

class DemoError(Exception):
    pass

TOKEN_URL = 'https://openapi.baidu.com/oauth/2.0/token'
# SCOPE = 'brain_bicc'  # 有此scope表示有asr能力，没有请在网页里勾选 bicc
#SCOPE = 'brain_asr_async'  # 有此scope表示有asr能力，没有请在网页里勾选
SCOPE = 'brain_enhanced_asr'  # 有此scope表示有asr能力，没有请在网页里勾选

#待进行语音识别的音频文件url地址，需要可公开访问。建议使用百度云对象存储（https://cloud.baidu.com/product/bos.html）
speech_url_list = [
    "https://voicefile.su.bcebos.com/电话(1).m4a?authorization=bce-auth-v1/4ff1bb40ff1a4430a82b59c291ee9d73/2020-05-21T07:36:17Z/300/host/28bd07886011a76aab76fb0301ea5afc12d7e13c7894b97cc6f5081e469ffec2"
    ]
#转写任务id列表，task_id是通过创建音频转写任务时获取到的，每个音频任务对应的值

headers = {'content-type': "application/json"}


def writdoc(name,doc):
    # 打开「detail_content」文件
    fout = open(name, 'w', encoding='utf8')
    # 写入文件内容
    fout.write(doc)
    #关闭文件
    fout.close()

class baiduenigne():
    """  发送查询结果请求 """
    def __init__(self,speech_url_list):
        self.speech_url_list = speech_url_list
        self.temp = ""
        self.result = ""
        self.task_id_list = []


    def fetch_token(self):
        params = {'grant_type': 'client_credentials',
                  'client_id': API_KEY,
                  'client_secret': SECRET_KEY}
        post_data = urlencode(params)
        if (IS_PY3):
            post_data = post_data.encode( 'utf-8')
        req = Request(TOKEN_URL, post_data)
        try:
            f = urlopen(req)
            result_str = f.read()
        except URLError as err:
            print('token http response http code : ' + str(err.code))
            result_str = err.read()
        if (IS_PY3):
            result_str = result_str.decode()
        result = json.loads(result_str)
        if ('access_token' in result.keys() and 'scope' in result.keys()):
            if not SCOPE in result['scope'].split(' '):
                raise DemoError('scope is not correct')
    #        print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
            return result['access_token']
        else:
            raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

    """  获取鉴权结束，TOKEN end """

    """  发送识别请求 """
    def creat_task(self,af):
        for speech_url in self.speech_url_list:
            url = 'https://aip.baidubce.com/rpc/2.0/aasr/v1/create'  # 创建音频转写任务请求地址
            body = {
                "speech_url": speech_url,
                "format": af,        #音频格式，支持pcm,wav,mp3，音频格式转化可通过开源ffmpeg工具（https://ai.baidu.com/ai-doc/SPEECH/7k38lxpwf）或音频处理软件
                "pid": 1537,        #模型pid，1537为普通话输入法模型，1737为英语模型
                "rate": 16000       #音频采样率，支持16000采样率，音频格式转化可通过开源ffmpeg工具（https://ai.baidu.com/ai-doc/SPEECH/7k38lxpwf）或音频处理软件
            }
            token = {"access_token": self.fetch_token()}
            response = requests.post(url, params=token, data=json.dumps(body), headers=headers)
            # 返回请求结果信息，获得task_id，通过识别结果查询接口，获取识别结果
            result = json.loads(response.text)
            self.task_id_list= []
            self.task_id_list.append(result['task_id'])
            # 返回响应头
            # print response.status_code
            # print token

    def query_result(self):
        for task_id in self.task_id_list:
            url = 'https://aip.baidubce.com/rpc/2.0/aasr/v1/query'  # 查询音频任务转写结果请求地址
            body = {
                "task_ids": [task_id],
            }
            token = {"access_token": self.fetch_token()}
            response = requests.post(url,params=token,data = json.dumps(body), headers = headers)
            result = json.loads(response.text)
            while(result['tasks_info'][0]['task_status'] == "Running"):
                response = requests.post(url, params=token, data=json.dumps(body), headers=headers)
                result = json.loads(response.text)
                time.sleep(1)
            print("这里")
            if (result['tasks_info'][0]['task_status'] == "Failure"):
                self.temp = result['tasks_info'][0]['task_result']['err_msg']
                print("sdfs",self.temp)
                self.result = [self.temp]
                return False
            # writdoc('音频文件内容.txt', result['tasks_info'][0]['task_result']['result'])
            self.result =""
            self.result = result['tasks_info'][0]['task_result']['result']
            print("sdsdffs",self.result)
            return True

    def get_result(self):
        if self.result[0] == "":
            return ["请选择合适的格式"]
        elif self.result:
            return self.result
        else:
            return ["出错了！！未获取到结果"]




if "__main__" == __name__:
    a = baiduenigne(speech_url_list,"mp3")
    b = a.get_result()
    print(b)
    pass
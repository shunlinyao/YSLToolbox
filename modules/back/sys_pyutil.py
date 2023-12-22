# -*- coding:utf-8 -*-

#python2.7升级到python3以后的语法修改
import logging
from hashlib import md5
import urllib.request
import json
import time
import requests
import uuid
import base64
import os
import signal

logging.getLogger("request").setLevel(logging.WARNING)
#print 语法修改

#平台所用加密算法
def platform_md5(passwd, passsalt):
    res = py3_md5(py3_md5(py3_md5(passwd))+passsalt)
    return res
#ygy
def ygy_md5(passwd,passsalt):
    res = py3_md5(py3_md5(passwd)+passsalt)
    return res

#md5加密修改
def py3_md5(paramstr):
    return md5(paramstr.encode("utf-8")).hexdigest()

#request has_key修改
def request_haskey(paramreq, paramkey):
    return paramkey in paramreq.request.arguments

#dict has_key修改
def dict_haskey(paramdict, paramkey):
    return paramkey in paramdict

#tornado 获取cookie值多了个b, bytes类型转换decode
def get_safe_cookie(paramreq, cookiekey):
    value = paramreq.get_secure_cookie(cookiekey)
    resVal = "" if value == None else value.decode()
    return resVal

#py3字节转换
def change_to_decode(value):
    if not value:
        return ""
    if value == "undefined" or value == None:
        return ""
    if type(value).__name__ == "str":
        return value
    return value.decode()

#post请求外网
def post_requests(url, dataObj, headers={}):
    res = requests.post(url, data=json.dumps(dataObj), headers=headers)
    data = urllib.request.urlopen(res, None, 3)
    dataRes = data.read()
    if dataRes != None:
        dataRes = dataRes.decode("utf-8")
    return dataRes
def post_requests_timeout(url, dataObj, headers={}, timeout=2):
    try:
        res = requests.post(url, data=json.dumps(dataObj), headers=headers, timeout=timeout)
        data = urllib.request.urlopen(res, None, 3)
        dataRes = data.read()
        if dataRes != None:
            dataRes = dataRes.decode("utf-8")
        return dataRes
    except Exception as e:
        print("request error:",url, dataObj)
    return {}
#get请求外网
def get_requests_timeout(url, params=None, headers={}, timeout=2):
    try:
        res = requests.get(url, params=params, headers=headers, timeout=timeout)
        if res.status_code == 200: 
            dataRes = res.text
            return dataRes
        else:
            print("Request failed with status code:", res.status_code)
    except Exception as e:
        print("request error:", url, params)
    return {}
#post请求外网
def post_url(url, dataObj, headers={}):
    try:
        res = urllib.request.Request(url, data=json.dumps(dataObj).encode(encoding='UTF8'), headers=headers)
        data = urllib.request.urlopen(res, None, 3)
        dataRes = data.read()
        if dataRes != None:
            dataRes = dataRes.decode("utf-8")
        return dataRes
    except Exception as e:
        print("ERROR====>",e,e.__traceback__,e.__traceback__.tb_lineno)
    return None;

#get请求外网
def get_url(url):
    res = urllib.request.urlopen(url)
    data = res.read()    #读取全部
    return data

#http 请求相关接口
def http_request(method, url, headers, params):
    reqRes = None
    try:
        if "GET" == method:
            reqRes = requests.request("GET", url, headers=headers)
        elif "PUT" == method:
            reqRes = requests.put(url, json=params, headers=headers)
        elif  "POST" == method:
            reqRes = requests.post(url, json=params, headers=headers)
    except Exception as e:
        print("requests_put ERROR = ", e)
        return None
    return reqRes
def http_request_get(url, headers):
    return http_request("GET", url, headers, None)

def http_request_put(url, headers, params):
    return http_request("PUT", url, headers, params)

def http_request_post(url, headers, params):
    return http_request("POST", url, headers, params)



#python3中json的中文防止转义
def json_dumps(djson):
    return json.dumps(djson, ensure_ascii=False)

def json_loads_param(djson, param):
    if param in djson:
        djson[param] = json.loads(djson[param])
    return djson

#python3中b64encode
def b64encode(value):
    return base64.b64encode(value)

#python3中b64decode
def b64decode(value):
    return base64.b64decode(value)

#python3中json, 仅map,每个字段前多了b，转义
def json_decode_map(json):
    newJson = {}
    for i, v in json.items():
        newJson[i.decode()] = v.decode()
    return newJson

#PC游客unionid生成
def visitor_unionid():
    uid = "yk_" + str(uuid.uuid1())[:25]
    return uid

def remove_file(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)
        return {"status": 1, "msg": "删除成功"}
    else:
        return {"status": 0, "msg": "文件不存在"}

def kill(pid):
    print('pid', pid)
    a = os.kill(pid, signal.SIGKILL)
    print('已杀死pid为%s的进程,　返回值是:%s' % (pid, a))

# 杀掉重复的进程
def kill_repeat_target(target, include_str):
    cmd_run = "ps aux | grep {}".format(target)
    out = os.popen(cmd_run).read()
    # print("out === ", out)
    _index = 0
    for line in out.splitlines():
        # print("line = ",line)
        # 另外判断杀死进行所在的路径
        if include_str in line:
            _index += 1
            if _index > 1:
                pid = int(line.split()[1])
                # print("pid = ", pid)
                kill(pid)

# importing the main event loop
import uuid
from datetime import datetime, timedelta

def uuid1(uuidStr=""):
    id = uuid.uuid1();
    
    return id.hex
def sys_get_value(data, name, default = ""):
    if None == data:
        return default

    if name in data:
        return data[name]
    return default
def make_return_data(status, data, msg ="执行成功"):
    retData = {"status": status, "msg": msg, "res":data}
    #print(json.dumps(retData))
    return retData

def cal_expire_data(seconds):
    now = datetime.now()
    expire_time = now + timedelta(seconds=seconds)
    return expire_time.strftime("%Y-%m-%d %H:%M:%S")
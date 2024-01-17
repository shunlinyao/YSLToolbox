# -*- coding:utf-8 -*-
# 百度云bos相关对接
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.services.bos.bos_client import BosClient
from urllib.parse import unquote
import time
import modules.back.common_api as common_api
# from modules.config import CONFIG


class CSYBosPlugin():
    # https://cloud.baidu.com/doc/BOS/s/Ekc4epj6m#%E5%93%8D%E5%BA%94%E5%85%83%E7%B4%A0
    # https://cloud.baidu.com/doc/BOS/s/sjwvyrg3l#%E4%B8%8B%E8%BD%BD%E6%96%87%E4%BB%B6
    # 本接口用于获得指定Bucket的Object信息列表。

    def __init__(self, end_point, bos_config):
        self.bos_client = self.init_bj_bosclient(end_point, bos_config)
    def ListObjects(self):
        try:
            # 指定最大返回条数为500
            max_keys = 500
            objRet = self.makeRetObject();             
            self.enumObjs("luzhi2", "APK/test/Shineon", 0, False, objRet)

        except Exception as e:
            print ("ListObjects Error :=====>", e)
    def enumObjs(self, bucket, path, level, bChildDir, retObj):
        sLog = ""
        for i in range(level) :
            sLog = sLog + "----"
        sLog = sLog + path
        print(sLog)
      
        objRet = {};
        objRet["marker"] = None;
        while True:
            objRet = self.GetChildObject(bucket, path,objRet["marker"]);

            if bChildDir:
                for obj in objRet["dirs"]:
                    print(sLog, obj["name"])  
                    self.enumObjs(bucket, obj["key"], level+1, bChildDir, retObj);

            for obj in objRet["files"]:
                print(sLog, obj["name"]," size:",obj["size"])                 
                meta = self.GetMetadata(bucket,  obj["key"]);
                print(meta);
            retObj["bucket"] = retObj["bucket"]
            retObj["dirs"]   = retObj["dirs"] + objRet["dirs"] 
            retObj["files"]  = retObj["files"] + objRet["files"]   

            if None == objRet["marker"]:
                break;

    # 获取下载url
    def get_url(self,bucket,object_key, expiration_in_seconds=-1):
        timestamp=int(time.time())
        url = self.bos_client.generate_pre_signed_url(bucket, object_key, timestamp, expiration_in_seconds)
        urlRet = url.decode('utf-8');
        return urlRet
    def get_url_cdn(self, bucket, object_key):
        url = "https://{}.cdn.bcebos.com/{}".format(bucket, object_key)
        return url;
    # 获取文件的metadata
    def GetMetadata(self, bucket, object_key):
        response = self.bos_client.get_object_meta_data(bucket_name = bucket, key = object_key)
        print(response)
        if None == response:
            return None;      
        metadata = response.metadata;
        return self.makeObject(self.getName(object_key), object_key, metadata.content_length, metadata.last_modified, False, "");
    #初始化bosclient
    
    def get_bucket_end_point(self, bucket):
        end_point = {
            "luzhi2":"bj.bcebos.com",
            "web-taiyuan":"bj.bcebos.com",
            "webvideo-rec":"bj.bcebos.com",
            "shineonimg":"bd.bcebos.com",
            "sywebimg":"bd.bcebos.com",
            "webvideo":"bd.bcebos.com",
            "luzhitest":"bd.bcebos.com",
            "shineon-rec":"bj.bcebos.com",
        }
        endPoint = common_api.sys_get_value(end_point, bucket, None)
        if None == endPoint:
            endPoint = "bj.bcebos.com";
        return endPoint;

    def delete_file_by_key(self, bucket, object_key):
        obj = CSYBosPlugin("");  
        ret = obj.delete_file(bucket, object_key)
        return ret;
        
    def delete_file_url(self, url):
         
        #url = "https://{}.cdn.bcebos.com/{}".format(bucket, object_key)                   
        bucketTemp = url.split('.cdn.bcebos.com/')[:1][0]

        if "https://" in bucketTemp:
            bucket = bucketTemp.split('https://')[1:][0] 
        elif "http://" in bucketTemp:
            bucket = bucketTemp.split('http://')[1:][0]  

        if ".cdn.bcebos.com/v1/" in url:
            object_key = url.split('.cdn.bcebos.com/v1/')[1:][0]
        elif ".cdn.bcebos.com/" in url:
            object_key = url.split('.cdn.bcebos.com/')[1:][0]             
        try:            
            end_point = self.get_bucket_end_point(bucket); 
        except print("end_point error!"):
            pass     
        if end_point==None:
            return None
          
        obj = CSYBosPlugin(end_point);  
        obj.delete_file(bucket, object_key)

        return 1;

    def set_download_flag(self, bucket, object_key):

        conten_type = "application/octet-stream";     
         
        self.SetMetadata(bucket, object_key, conten_type)
       
    
    def set_object_acl(self, bucket_name, object_key, value):       
        from baidubce.services.bos import canned_acl 
        object_key = unquote(object_key, "utf-8");
        acl = canned_acl.PUBLIC_READ;
        if 0 == value:
            acl = canned_acl.PRIVATE;
        try:
            self.bos_client.set_object_canned_acl(bucket_name, object_key, canned_acl=acl)
            obj_acl = self.bos_client.get_object_acl(bucket_name, object_key);
        
            print(obj_acl);
        except Exception as e:
            print("set_object_acl error:", bucket_name, object_key)
            return False;
        return True;
    def SetMetadata(self, butcket, object_key, conten_type, user_metadata = None):
        
        if None == user_metadata:
            user_metadata ={            
            }
        object_key = unquote(object_key, "utf-8")
        
        try:
            ret = self.bos_client.copy_object(source_bucket_name = butcket, 
                        source_key = object_key, 
                        target_bucket_name = butcket,                        
                        content_type=conten_type,
                        target_key = object_key, 
                        user_metadata = user_metadata)     
        except Exception as e:
            print ("SetMetadata Error :=====>", e)   
            return False
        return True;
    
    def get_folder_value(self, bucket_name, object_key):        
        prefix = object_key
        if object_key[-1] != "/":
            prefix = "{}/".format(object_key)
        
        # 递归列出fun目录下的所有文件
        
        objValue = {
            "size":0,
            "count":0,
        }          
        
        isTruncated = True
        marker = None
        while isTruncated:
            response = self.bos_client.list_objects(bucket_name,max_keys=500, prefix = prefix, marker=marker)
            for obj in response.contents:
                print(obj.key,"  size", obj.size)
                objValue["size"] += obj.size;
            objValue["count"] += len(response.contents);
            isTruncated = response.is_truncated
            marker = getattr(response,'next_marker',None)
            
        log = "*******get_folder_value: {} size:{} count:{}".format(bucket_name, objValue["size"], objValue["count"])
        print(log)    
        return objValue;
    
    def init_bj_bosclient(self, end_point, config):
        access_key_id = config["ak"]
        secret_access_key = config["sk"]
        if "" == end_point:
            end_point = config["bos_end_point"]

        config = BceClientConfiguration(credentials=BceCredentials(access_key_id, secret_access_key), endpoint=end_point)
        bos_client = BosClient(config)
        return bos_client
    # 根据指定路径查找目录下的文件
    def FindObject(self,bucket, path, filter, bResource):
        findPath = path+filter;

        try:
            # 指定最大返回条数为500
            max_keys = 500
            objRet = self.makeRetObject();             
            self.enumObjs(bucket, findPath, 0, False, objRet)

        except Exception as e:
            print ("FindObject Error :=====>", e)
    # 获取指定目录下的文件和目录
    def GetChildObject(self,bucket, path, marker=None):
        objRet = self.makeRetObject();       
        objRet["bucket"]=bucket;
           
        delimiter="/"
       
        response = self.bos_client.list_objects(bucket, max_keys=20, prefix=path, delimiter=delimiter,marker=marker)
        if None != response.contents:
            for obj in response.contents:         
                object = self.makeObject(self.getName(obj.key), obj.key, obj.size, obj.last_modified, False, "");
                objRet["files"].append(object);

        if None != response.common_prefixes:
            for obj in response.common_prefixes:
                object = self.makeObject(self.getName(obj.prefix), obj.prefix, 0, "", True,"");
                objRet["dirs"].append(object);
        if response.is_truncated:
            objRet["marker"] = getattr(response,'next_marker',None)      
      
        return objRet;

    def makeObject(self, name, key, size, time, isDir, url):
        obj = {};
        obj["name"] = name;
        obj["key"] = key;
        obj["url"] = url;
        obj["size"]= size;
        obj["modify_time"]=time;
        obj["isDir"] = isDir;
        return obj;
    def makeRetObject(self):
        objRet = {};       
        objRet["bucket"]="";
        objRet["marker"]=None
        objRet["files"] = []
        objRet["dirs"] = [] 
        return objRet;
    #获取文件名
    def getName(self, key):

        nPos = key.rfind("/")
        if nPos != -1:
            return key[nPos+1:]
        return key;
        #获取文件名
    def put_file(self, bucket, objectKey, file):
        try:
            ret =  self.bos_client.put_object_from_file(bucket, objectKey, file)
        except Exception as e:
            print ("put_file Error :=====>", e)
            return False
        #SYBosPlugin.instance().put_file("luzhi2", "/upload/test.jpg", "fdfd2.jpg")
        return ret;
    def put_string(self, bucket, objectKey, string):
        ret =  self.bos_client.put_object_from_string(bucket, objectKey, string)
        #SYBosPlugin.instance().put_file("luzhi2", "/upload/test.jpg", "fdfd2.jpg")
        return ret;
    def put_string2(self, bucket, objectKey, string, content_type=None, user_metadata=None):
        ret =  self.bos_client.put_object_from_string(bucket, objectKey, string,content_type = content_type,user_metadata=user_metadata )
        #SYBosPlugin.instance().put_file("luzhi2", "/upload/test.jpg", "fdfd2.jpg")
        return ret;
    def put_file2(self, bucket, objectKey, file, content_type=None, user_metadata=None):
        ret =  self.bos_client.put_object_from_file(bucket, objectKey, file,content_type = content_type,user_metadata=user_metadata)
        #SYBosPlugin.instance().put_file("luzhi2", "/upload/test.jpg", "fdfd2.jpg")
        return ret;
    def delete_file(self, bucket, objectKey):
        ret = 0
        try:
            ret = self.bos_client.delete_object(bucket, objectKey)
        except Exception as e:
            print("delete file error", bucket, objectKey)     
        
        if 0 == ret:
            return False;
        
        return True

def instance(endpoint = "", bos_config = None):
    return CSYBosPlugin(endpoint, bos_config);



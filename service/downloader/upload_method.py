import requests
import json
import os
import hashlib

class Upload_Function():
    def __init__(self):
        pass

    def get_config(self, url):
        body = json.dumps({'cmd': 'get_config'})
        print("get_config", url, body)
        try:
            response = self.http_request_post(url + '/upload/api/get_config', {'Content-Type':'application/json'}, body)
            return {"status": 1, "message": "Get config success."}
            print (response)
        except Exception as e:
            print("get_config ERROR====>",e,e.__traceback__,e.__traceback__.tb_lineno)
            return {"status": 0, "message": "Get config failed."}
    
    def prepare_upload(self, file_path, target_url, filename):
        print("prepare_upload", file_path, target_url)
        try:
            json_data = json.dumps({'filename': filename, 'cmd': 'file_prepare'})
            response = self.http_request_post(target_url + '/upload/file', {'Content-Type':'application/json'}, json_data)
            if 'res' in response:
                file_size = os.path.getsize(file_path)
                response['res']['file_size'] = file_size
                return response['res']
            return response
        except Exception as e:
            print("prepare_upload ERROR====>",e,e.__traceback__,e.__traceback__.tb_lineno)
            return {"status": 0, "message": "Prepare upload failed."}

    def uploading_file(self, file_path, target_url, rt_file_info, chunk_size=5*1024*1024):  # 3MB chunk size
        print("uploading_file", file_path, target_url)
        try:
            file_name = os.path.basename(file_path)
            url = f"{target_url}/upload/file"
            chunk_start = 0

            with open(file_path, 'rb') as f:
                while True:
                    # Read a chunk of the file
                    file_content = f.read(chunk_size)
                    if not file_content:
                        break  # End of file

                    files = {'file': (file_name, file_content)}
                    data = {
                        "upload_id": rt_file_info['upload_id'],
                        "object_key": rt_file_info['object_key'],
                        "chunk_start": chunk_start,
                        "cmd": "file_data"
                    }

                    response = requests.post(url, files=files, data=data)

                    # Update the chunk_start for the next chunk
                    chunk_start += len(file_content)
            return self.end_upload_file(file_path, target_url, rt_file_info)
            return {"status": 1, "message": "File uploaded successfully"}
        except Exception as e:
            print("uploading_file ERROR====>", e, e.__traceback__, e.__traceback__.tb_lineno)
            return {"status": 0, "message": "Uploading file failed."}

    def end_upload_file(self, file_path, target_url, rt_file_info):
        object_key = rt_file_info['object_key']
        print("end_upload_file", file_path, target_url)
        try:
            json_data = json.dumps({'object_key':object_key, 'cmd':'file_end'})
            response = self.http_request_post(target_url + '/upload/file', {'Content-Type':'application/json'}, json_data)
            if 'res' in response:
                response['res']['id'] = rt_file_info['upload_id']
                return response['res']
            return response
        except Exception as e:
            print("end_upload_file ERROR====>",e,e.__traceback__,e.__traceback__.tb_lineno)
            return {"status": 0, "message": "End upload file failed."}

    def http_request_post(self, url, headers, params):
        reqRes = None
        dict_object = {}
        if headers['Content-Type'] == 'application/x-www-form-urlencoded':
            reqRes = requests.post(url, data=params, headers=headers)
        elif headers['Content-Type'] == 'application/json':
            reqRes = requests.post(url, headers=headers, data=params)
        if reqRes != None:
            str_object = reqRes.content.decode('utf-8')
            dict_object = json.loads(str_object)
        return dict_object

    def get_md5_code(self, file_path):
        md5_code = ''
        try:
            with open(file_path, 'rb') as f:
                md5_code = hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print("get_md5_code ERROR====>",e,e.__traceback__,e.__traceback__.tb_lineno)
        return md5_code

def instance():
    return Upload_Function()
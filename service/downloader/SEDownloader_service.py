import os
import tornado.ioloop
import tornado.web
import json
import requests
import threading
import service.downloader.upload_method as upload_method

class CSYDownloaderService():

    def __init__(self):
        self.upload_method = upload_method.instance()
        pass

    def start_upload_folder_helper(self, path):
        downlaod_json = self.get_downloader_json()
        target_url = downlaod_json['target_url']
        path_tree = self.get_path_tree(path)
        out_file_json = {}
        for file_path in path_tree:
            rt_file_info = self.start_upload_file_helper(file_path, target_url)
            out_file_json[file_path] = rt_file_info
        print(out_file_json)
    
    def start_upload_file_helper(self, file_path, target_url):
        print("start_upload_file_helper", file_path)
        thread = threading.Thread(target=self.upload_file, args=(file_path,target_url))
        thread.start()
        return 

    def upload_file(self, file_path, target_url):
        file_name = os.path.basename(file_path)
        rt_config = self.upload_method.get_config(target_url)
        if rt_config['status'] == 0:
            return rt_config
        rt_file_info = self.upload_method.prepare_upload(file_path, target_url, file_name)
        if 'status'in rt_file_info and rt_file_info['status'] == 0:
            return rt_file_info
        rs_id = self.create_new_resource(rt_file_info, target_url, file_name)
        rt_uploading = self.upload_method.uploading_file(file_path, target_url, rt_file_info)
        print("rt_uploading", rt_uploading)
        return rt_uploading
        

    def http_request_post(self, url, headers, params):
        reqRes = None
        if headers['Content-Type'] == 'application/x-www-form-urlencoded':
            reqRes = requests.post(url, data=params, headers=headers)
        elif headers['Content-Type'] == 'application/json':
            reqRes = requests.post(url, json=params, headers=headers)
        
        return reqRes

    def get_path_tree(self, path):
        path_tree = []
        for root, dirs, files in os.walk(path):
            for name in files:
                path_tree.append(os.path.join(root, name))
        return path_tree

    def update_downloader_json(self, key, value):
        downloader_json = self.get_downloader_json()
        downloader_json[key] = value
        self.set_downloader_json(downloader_json)

    def get_downloader_json(self):
        with open('doc/downloader/download_path.json', 'r') as f:
            downloader_json = json.load(f)
        return downloader_json

    def set_downloader_json(self, downloader_json):
        with open('doc/downloader/download_path.json', 'w') as f:
            json.dump(downloader_json, f)

    def create_new_resource(self, file_info, target_url, filename, rs_type):
        input_url = target_url + '/resource/api?command=getresourcedata'
        param = {
            'type': 'add',
            'content': {
                'id': file_info['upload_id'],
                'resource_name': filename,
                'type': rs_type,
                'filesize': 0,
                'file': '',
                'name': filename,
                'icon': '',
                'upload_status': 'started',
                'source': '发布中心',
                'bucket_name': file_info.bucket_name,
                'object_key': file_info.object_key
            }
        };
        response = self.http_request_post(input_url, {'Content-Type' : 'application/json'}, param)
        print (response)

def instance():
    return CSYDownloaderService()
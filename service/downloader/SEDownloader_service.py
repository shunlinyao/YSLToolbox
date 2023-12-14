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
        download_json = self.get_downloader_json()
        target_url = download_json['target_url']
        type_path_tree = self.get_folder_same_level(path)
        out_file_json = {}
        
        for type_folder_path in type_path_tree:
            rs_type = os.path.basename(path)
            type_file_tree = self.get_path_same_level(type_folder_path)
            for file_path in type_file_tree:
                self.start_upload_file_helper(file_path, target_url, rs_type, type_folder_path)
    
    def start_upload_file_helper(self, file_path, target_url,rs_type, path):
        print("start_upload_file_helper", file_path)
        thread = threading.Thread(target=self.upload_file, args=(file_path,target_url, rs_type, path))
        thread.start()
        return 

    def upload_file(self, file_path, target_url, rs_type, local_path):
        file_name = os.path.basename(file_path)
        rt_config = self.upload_method.get_config(target_url)
        if rt_config['status'] == 0:
            return rt_config
        
        rt_file_info = self.upload_method.prepare_upload(file_path, target_url, file_name)
        if 'status'in rt_file_info and rt_file_info['status'] == 0:
            return rt_file_info

        rs_return = self.create_new_resource(rt_file_info, target_url, file_name, rs_type)

        rt_uploading = self.upload_method.uploading_file(file_path, target_url, rt_file_info)
        if 'status'in rt_uploading and rt_uploading['status'] == 0:
            return rt_uploading
        icon_url = self.bind_file_icon(file_name, target_url, local_path)
        finish_rt = self.update_new_resource(rt_uploading, target_url, icon_url)
        print("resouce finished uploading", file_name, rt_uploading)
        return rt_uploading
    
    def bind_file_icon(self, file_name, target_url, local_path):
        new_icon_url = ''
        icon_path = local_path + '/icon'
        new_icon_path = ''

        file_base_name, _  = os.path.splitext(file_name)
        if os.path.exists(icon_path):
            path_tree = self.get_path_same_level(icon_path)
            for file in path_tree:
                if file_base_name in file:
                    new_icon_path = file
                    break
            if new_icon_path != '':
                new_icon_url = self.upload_icon(new_icon_path, target_url, 'image')
            if 'status' in new_icon_url and new_icon_url['status'] == 0:
                return ''
        return new_icon_url
    
    def upload_icon(self, file_path, target_url, folder_name):
        file_name = os.path.basename(file_path)
        rt_config = self.upload_method.get_config(target_url)
        if rt_config['status'] == 0:
            print('ICON get config failed', file_name)
            return rt_config
        
        rt_file_info = self.upload_method.prepare_upload(file_path, target_url, file_name)
        if 'status'in rt_file_info and rt_file_info['status'] == 0:
            print('ICON prepare_upload failed', file_name)
            return rt_file_info
        rs_type = folder_name
        rs_return = self.create_new_resource(rt_file_info, target_url, file_name, rs_type)

        rt_uploading = self.upload_method.uploading_file(file_path, target_url, rt_file_info)
        if 'status'in rt_uploading and rt_uploading['status'] == 0:
            print('ICON upload failed', file_name)
            return rt_uploading
        finish_rt = self.update_new_resource(rt_uploading, target_url, rt_uploading['url'])
        print("finished icon uploading", file_name, rt_uploading)
        return rt_uploading['url']

    def http_request_post(self, url, headers, params):
        reqRes = None
        if headers['Content-Type'] == 'application/x-www-form-urlencoded':
            reqRes = requests.post(url, data=params, headers=headers)
        elif headers['Content-Type'] == 'application/json':
            reqRes = requests.post(url, json=params, headers=headers)
        
        return reqRes

    def get_file_tag_info(self, type):
        tag_file_relation = self.get_tag_file_relation()
        file_tag_info = {'tag_list':[], 'file_json':{}}
        file_tag_info['tag_list'] = tag_file_relation['resouce_tag'][type]
        file_tag_info['file_json'] = tag_file_relation['resource_tag_relation'][type]
        return file_tag_info
    
    def get_path_tree(self, path):
        path_tree = []
        for root, dirs, files in os.walk(path):
            for name in files:
                path_tree.append(os.path.join(root, name))
        return path_tree

    def get_path_same_level(self, path):
        path_tree = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                path_tree.append(full_path)
        return path_tree

    def get_folder_same_level(self, path):
        path_tree = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                path_tree.append(full_path)
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

    def update_tag_file_relation(self, type, value):
        tag_file_relation = self.get_tag_file_relation()
        tag_file_relation['resource_tag_relation'][type] = value
        self.set_tag_file_relation(tag_file_relation)

    def get_tag_file_relation(self):
        with open('doc/downloader/tag_file_match.json', 'r') as f:
            tag_file_relation = json.load(f)
        return tag_file_relation
    
    def set_tag_file_relation(self, tag_file_relation):
        with open('doc/downloader/tag_file_match.json', 'w') as f:
            json.dump(tag_file_relation, f)

    def create_new_resource(self, file_info, target_url, filename, rs_type):
        input_url = target_url + '/resource/api?command=getresourcedata'
        param = {
            'type': 'add',
            'content': {
                'id': file_info['upload_id'],
                'resource_name': filename,
                'type': rs_type,
                'filesize': file_info['file_size'],
                'file': '',
                'name': filename,
                'icon': '',
                'upload_status': 'started',
                'source': '资源中心',
                'bucket_name': file_info['bucket_name'],
                'object_key': file_info['object_key']
            }
        };
        response = self.http_request_post(input_url, {'Content-Type' : 'application/json'}, param)
        return response

    def update_new_resource(self, file_info, target_url, icon_url):
        input_url = target_url + '/resource/api?command=getresourcedata'
        param = {
            'type': 'update',
            'content': {
                'id': file_info['id'],
                'file': file_info['url'],
                'upload_status': 'finished'
            }
        };
        if icon_url != '':
            param['content']['icon'] = icon_url
        response = self.http_request_post(input_url, {'Content-Type' : 'application/json'}, param)
        return response

def instance():
    return CSYDownloaderService()
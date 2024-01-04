import os
import tornado.ioloop
import tornado.web
import json
import requests
import threading
import service.downloader.upload_method as upload_method
import modules.back.common_api as common_api
from tornado.ioloop import IOLoop

class CSYDownloaderService():
    main_obj = None
    def __init__(self):
        self.upload_method = upload_method.instance()
        self.upload_config = {}
        pass

    def start_upload_folder_helper(self, path):
        download_json = self.get_downloader_json()
        target_url = download_json['target_url']
        self.upload_config = download_json['upload_param']
        type_path_tree = self.get_folder_same_level(path)
        out_file_json = {}
        
        for type_folder_path in type_path_tree:
            if os.path.basename(type_folder_path) == 'icon':
                continue            
            rs_type = os.path.basename(type_folder_path)
            strong_tag_list = []
            for folder_tag_path in self.get_folder_same_level(type_folder_path):
                if os.path.basename(folder_tag_path) == 'icon':
                    continue
                folder_tag_tree = self.get_path_same_level(folder_tag_path)
                if len(folder_tag_tree) != 0:
                    strong_tag_list.append(os.path.basename(folder_tag_path))
                for file_path in folder_tag_tree:
                    self.start_upload_file_helper(file_path, target_url, rs_type, folder_tag_path)
            self.add_multi_strong_tag_request(target_url, strong_tag_list, rs_type)
    def start_upload_file_helper(self, file_path, target_url,rs_type, path):
        print("start_upload_file_helper", file_path)
        thread = threading.Thread(target=self.upload_file, args=(file_path,target_url, rs_type, path))
        thread.start()
        self.websocket.write_message(json.dumps({'cmd': 'finished_upload', 'message': {'file_path': file_path, 'status': 0, 'message': 'Resource already exist.'}}))
        return 

    def upload_file(self, file_path, target_url, rs_type, local_path):
        file_name = os.path.basename(file_path)
        upload_mode = 0
        rt_file_info = {}
        if self.upload_config['type'] == 0:
            upload_mode = 0
        else:
            upload_mode = 1 
        rt_config = self.upload_method.get_config(target_url)
        if rt_config['status'] == 0:
            return rt_config
        if upload_mode == 0:
            rt_file_info = self.upload_method.prepare_upload(file_path, target_url, file_name)
            
        
        if 'status'in rt_file_info and rt_file_info['status'] == 0:
            return rt_file_info
        md5_code = self.upload_method.get_md5_code(file_path)
        md5_exist_b = self.check_if_md5_exist(md5_code, target_url)
        if md5_exist_b == False:
            if upload_mode == 1:
                rt_file_info = self.upload_method.bos_prepare_upload(file_path, file_name, self.upload_config['baidu_cloud'])
            rs_return = self.create_new_resource(rt_file_info, target_url, file_name, rs_type, md5_code)
            tag_list = self.get_file_tag_list(rs_type, file_path)
            tag_return = self.add_resource_tag_request(rt_file_info, target_url, tag_list, rs_type)
            if upload_mode == 0:
                rt_uploading = self.upload_method.uploading_file(file_path, target_url, rt_file_info)
            else:
                rt_uploading = self.upload_method.bos_uploading_file(rt_file_info)
            if 'status'in rt_uploading and rt_uploading['status'] == 0:
                return rt_uploading
            
            icon_info = self.bind_file_icon(file_name, target_url, local_path)
            finish_rt = self.update_new_resource(rt_uploading, target_url, icon_info,tag_list)
            print("resouce finished uploading", file_name, rt_uploading)
            # self.websocket.write_message(json.dumps({'cmd': 'finished_upload', 'message': {'file_name': file_name, 'status': 0, 'message': 'File uploaded successfully'}}))
            return rt_uploading
        else:
            print("resouce already exist", file_name)
            # self.websocket.write_message(json.dumps({'cmd': 'finished_upload', 'message': {'file_name': file_name, 'status': 3, 'message': 'Resource already exist.'}}))
            return {"status": 1, "message": "Resource already exist."}
    
    def bind_file_icon(self, file_name, target_url, local_path):
        new_icon_url = ''
        icon_path = local_path + '/icon'
        new_icon_path = ''
        icon_info = {}
        file_base_name, _  = os.path.splitext(file_name)
        if os.path.exists(icon_path):
            path_tree = self.get_path_same_level(icon_path)
            for file in path_tree:
                if file_base_name in file:
                    new_icon_path = file
                    break
            if new_icon_path != '':
                icon_info = self.upload_icon(new_icon_path, target_url, 'image')
            if 'status' in icon_info and icon_info['status'] == 0:
                return ''
        return icon_info
    
    def upload_icon(self, file_path, target_url, folder_name):
        file_name = os.path.basename(file_path)
        rt_config = self.upload_method.get_config(target_url)
        if rt_config['status'] == 0:
            print('ICON get config failed', file_name)
            return rt_config
        if self.upload_config['type'] == 0:
            rt_file_info = self.upload_method.prepare_upload(file_path, target_url, file_name)
        else:
            rt_file_info = self.upload_method.bos_prepare_upload(file_path, file_name, self.upload_config['baidu_cloud'])
        if 'status'in rt_file_info and rt_file_info['status'] == 0:
            print('ICON prepare_upload failed', file_name)
            return rt_file_info
        rs_type = folder_name
        # rs_return = self.create_new_resource(rt_file_info, target_url, file_name, rs_type, [], '')
        if self.upload_config['type'] == 0:
            rt_uploading = self.upload_method.uploading_file(file_path, target_url, rt_file_info, self.upload_config['type'])
        else:
            rt_uploading = self.upload_method.bos_uploading_file(rt_file_info)
        if 'status'in rt_uploading and rt_uploading['status'] == 0:
            print('ICON upload failed', file_name)
            return rt_uploading
        icon_info = {'url': rt_uploading['url'], 'bucket_name': rt_file_info['bucket_name'], 'object_key': rt_file_info['object_key']}
        # finish_rt = self.update_new_resource(rt_uploading, target_url, rt_uploading['url'])
        print("finished icon uploading", file_name, rt_uploading)
        return icon_info

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
        with open('doc/downloader/download_path.json', 'r', encoding='utf-8') as f:
            downloader_json = json.load(f)
        return downloader_json

    def set_downloader_json(self, downloader_json):
        with open('doc/downloader/download_path.json', 'w', encoding='utf-8') as f:
            json.dump(downloader_json, f)

    def update_tag_file_relation(self, type, value):
        tag_file_relation = self.get_tag_file_relation()
        tag_file_relation['resource_tag_relation'][type] = value
        self.set_tag_file_relation(tag_file_relation)
    
    def update_tag_list(self, type, value):
        tag_file_relation = self.get_tag_file_relation()
        if value not in tag_file_relation['resouce_tag'][type]:
            tag_file_relation['resouce_tag'][type].append(value)
        self.set_tag_file_relation(tag_file_relation)

    def get_tag_file_relation(self):
        with open('doc/downloader/tag_file_match.json', 'r', encoding='utf-8') as f:
            tag_file_relation = json.load(f)
        return tag_file_relation
    
    def get_file_tag_list(self, type, file_path):
        tag_file_relation = self.get_tag_file_relation()
        if file_path not in tag_file_relation['resource_tag_relation'][type]:
            tag_file_relation['resource_tag_relation'][type][file_path] = []
            return []
        tag_list = tag_file_relation['resource_tag_relation'][type][file_path]
        return tag_list

    def set_tag_file_relation(self, tag_file_relation):
        with open('doc/downloader/tag_file_match.json', 'w', encoding='utf-8') as f:
            json.dump(tag_file_relation, f)

    def create_new_resource(self, file_info, target_url, filename, rs_type, md5_code):
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
        if md5_code != '':
            param['content']['md5'] = md5_code
        response = self.http_request_post(input_url, {'Content-Type' : 'application/json'}, param)
        return response

    def update_new_resource(self, file_info, target_url, icon_info,tag_list):
        input_url = target_url + '/resource/api?command=getresourcedata'
        param = {
            'type': 'update',
            'content': {
                'id': file_info['upload_id'],
                'file': file_info['url'],
                'upload_status': 'finished'
            }
        };
        if len(tag_list) > 0:
            stringfy_tag_list = ''
            stringfy_tag_list = ','.join(tag_list)
            param['content']['tag'] = stringfy_tag_list
        if icon_info != {}:
            param['content']['icon'] = icon_info['url']
            param['content']['icon_bucket_name'] = icon_info['bucket_name']
            param['content']['icon_object_key'] = icon_info['object_key']
        response = self.http_request_post(input_url, {'Content-Type' : 'application/json'}, param)
        return response

    def add_resource_tag_request(self, file_info, target_url, tag_list, rs_type):
        input_url = target_url + '/resource/api?command=getresourcesub'
        param = {
            'type': 'add_multi_tag',
            'content': {
                'rs_id': file_info['upload_id'],
                'tag_list': tag_list,
                'type': rs_type
            }
        };
        response = self.http_request_post(input_url, {'Content-Type' : 'application/json'}, param)
        return response

    def add_multi_strong_tag_request(self, target_url, tag_list, rs_type):
        input_url = target_url + '/resource/api?command=getresourcesub'
        param = {
            'type': 'add_multi_strong_tag',
            'content': {
                'tag_list': tag_list,
                'type': rs_type
            }
        };
        response = self.http_request_post(input_url, {'Content-Type' : 'application/json'}, param)
        return response

    def check_if_md5_exist(self, md5_code, target_url):
        input_url = target_url + '/resource/api?command=getresourcedata'
        param = {
            'type': 'check_md5',
            'content': {
                'md5': md5_code
            }
        };
        response = self.http_request_post(input_url, {'Content-Type' : 'application/json'}, param)
        str_object = response.content.decode('utf-8')
        dict_object = json.loads(str_object)
        if 'if_exist' in dict_object:
            if dict_object['if_exist'] == True:
                return True
        return False

    def local_path_organizer(self, path):
        root_folder_name = os.path.basename(path)
        if root_folder_name != 'file':
            #return error
            return {"status": 0, "message": "wrong root path"}
        type_path_tree = self.get_folder_same_level(path)
        for type_folder_path in type_path_tree:
            folder_tag_path_tree = self.get_folder_same_level(type_folder_path)
            rs_type = os.path.basename(type_folder_path)
            for folder_tag_path in folder_tag_path_tree:
                file_path_tree = self.get_path_same_level(folder_tag_path)
                
                folder_tag = os.path.basename(folder_tag_path)
                if folder_tag == 'icon':
                    continue
                self.update_tag_list(rs_type, folder_tag)
                if len(file_path_tree) == 0:
                    continue
                for file_path in file_path_tree:
                    file_name = os.path.basename(file_path)
                    tag_list = self.get_file_tag_list(rs_type, file_path)
                    if folder_tag not in tag_list: 
                        tag_list.append(folder_tag)
                        self.update_tag_file_relation(rs_type, {file_path: tag_list})
        return {"status": 1, "message": "Path do exist."}
    
    def register_websocket(self, websocket):
        self.websocket = websocket

    def send_message_to_websocket(handler, message):
        if not handler.ws_connection:
            return  # Check if WebSocket is still open

        handler.write_message(message)

def instance():
    if None == CSYDownloaderService.main_obj:
        CSYDownloaderService.main_obj = CSYDownloaderService()
    return CSYDownloaderService.main_obj
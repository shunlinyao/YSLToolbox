from modules.back.base_request import VMRequestHandler
import service.downloader.SEDownloader_service as SEDownloader_service
import modules.back.sys_pyutil as sys_pyutil
import tornado.websocket as websocket
import json
import os

class VMDownloaderPageHandler(VMRequestHandler):
    def get(self):
        self.render("downloader/index.html")

class VMDownloaderAPIHandler(VMRequestHandler):
    def get(self):
        self.write("Hello, World!") 

    def post(self):
        command = self.get_argument("command", "")
        if command == "test_connection":
            self.test_connection_helper()
        if command == "local_path_check":
            self.local_path_check_helper()
        if command == "local_path_tree":
            self.local_path_tree_helper()
        if command == "start_upload":
            self.start_upload_helper()
        if command == "add_tag":
            self.add_tag_helper()

    def test_connection_helper(self):
        args = json.loads(self.request.body.decode("utf-8"))
        print('request message')
        try:
            input_url = args['content']['url'] + '/resource/api?command=test_connection'
            response = SEDownloader_service.instance().http_request_post(input_url, args['content']['header'], args['content']['body'])
            str_object = response.content.decode('utf-8')
            dict_object = json.loads(str_object)
            response_json = dict_object
            SEDownloader_service.instance().update_downloader_json('target_url', args['content']['url'])
            self.write(response_json)
        except Exception as e:
            print("ERROR====>",e,e.__traceback__,e.__traceback__.tb_lineno)
            self.write({"status": 0, "message": "Connection failed."})
            
    def local_path_check_helper(self):
        args = json.loads(self.request.body.decode("utf-8"))
        try:
            if os.path.exists(args['content']['path']):
                SEDownloader_service.instance().update_downloader_json('target_path', args['content']['path'])
                self.write({"status": 1, "message": "Path exists."})
            else:
                self.write({"status": 0, "message": "Path does not exist."})
        except Exception as e:
            print("ERROR====>",e,e.__traceback__,e.__traceback__.tb_lineno)
            self.write({"status": 0, "message": "Path does not exist."})

    def local_path_tree_helper(self):
        args = json.loads(self.request.body.decode("utf-8"))
        try:
            if os.path.exists(args['content']['path']):
                path_tree = SEDownloader_service.instance().get_path_same_level(args['content']['path'])
                file_tag_relation = SEDownloader_service.instance().get_file_tag_info(args['content']['rs_type'])
                self.write({"status": 1, "message": "Path exists.", "path_tree": path_tree, "file_tag_relation":file_tag_relation})
            else:
                self.write({"status": 0, "message": "Path does not exist."})
        except Exception as e:
            print("ERROR====>",e,e.__traceback__,e.__traceback__.tb_lineno)
            self.write({"status": 0, "message": "Path does not exist."})       

    def start_upload_helper(self):
        args = json.loads(self.request.body.decode("utf-8"))
        path = args['content']['path']
        SEDownloader_service.instance().start_upload_folder_helper(path)
        self.write({"status": 1, "message": "Upload started."})

    def add_tag_helper(self):
        args = json.loads(self.request.body.decode("utf-8"))
        SEDownloader_service.instance().update_tag_list(args['content']['resource_type'], args['content']['tag_name'])
        self.write({"status": 1, "message": "Tag added."})
    # def sent_request_helper(self):
    #     args = json.loads(self.request.body.decode("utf-8"))
    #     if args['cmd'] == 'GET':
    #         # log_out = new_log(args['key'])
    #         response = sys_pyutil.http_request_get(args['url'], args['header'])
    #         str_object = response.content.decode('utf-8')
    #         dict_object = json.loads(str_object)
    #     if args['cmd'] == 'POST':
    #         # log_out = new_log(args['key'])
    #         response = SEDownloader_service.instance().http_request_post(args['url'], args['header'], args['body'])
    #         str_object = response.content.decode('utf-8')
    #         dict_object = json.loads(str_object)
    #     response_json = dict_object
    #     self.write(response_json)


class VMDownloaderWebsocketHandler(websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        data = json.loads(message)
        if data['cmd'] == 'bind_tag':
            SEDownloader_service.instance().update_tag_file_relation(data['content']['resource_type'], data['content']['relation'])
        print("WebSocket received message")

    def on_close(self):
        
        print("WebSocket closed")
    
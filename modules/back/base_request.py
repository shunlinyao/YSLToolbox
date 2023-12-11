import tornado
import tornado.web
class VMRequestHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'authorization, Authorization, Content-Type, Access-Control-Allow-Origin, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')
        
    def initialize(self, static_path):
        self.static_path = static_path
    def get_template_path(self):
        return self.static_path
    def get_post_argument(self,key,default_value):
        if key not in self.post_data.keys():
            return default_value
        return self.post_data[key]
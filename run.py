import os
import tornado.ioloop
import tornado.web
import debugpy
from tornado.web import StaticFileHandler
from request.VMDownloader_handler import VMDownloaderAPIHandler, VMDownloaderPageHandler, VMDownloaderWebsocketHandler

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        print("Request received")
        self.write("Hello, World!")

def make_app():
    static_path = os.path.join(os.path.dirname(__file__), "static")
    return tornado.web.Application([
        (r"/toolbox/tool_downloader", VMDownloaderPageHandler, {'static_path': static_path}),
        (r"/toolbox/tool_downloader/api", VMDownloaderAPIHandler, {'static_path': static_path}),
        (r"/toolbox/tool_downloader/websocket/dd", VMDownloaderWebsocketHandler),
        (r"/toolbox/app2", MainHandler),
        (r"/toolbox/static/(.*?)$", StaticFileHandler, {'path': static_path})
    ], debug=True)  # Set debug mode

if __name__ == "__main__":
    # Start a debugpy listener
    debugpy.listen(('localhost', 5678))
    print("Waiting for debugger attach")
    debugpy.wait_for_client()
    debugpy.breakpoint()
    print("Debugger attached")

    port = 8888
    app = make_app()
    app.listen(port)
    print(f"Server started at port {port}")
    tornado.ioloop.IOLoop.current().start()

import os
import sys
import tornado.ioloop
import signal
import tornado.web
import debugpy
from tornado.web import StaticFileHandler
from request.VMDownloader_handler import VMDownloaderAPIHandler, VMDownloaderPageHandler, VMDownloaderWebsocketHandler, VMDownloaderIconHandler

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        print("Request received")
        self.write("Hello, World!")

def signal_handler(sig, frame):
    tornado.ioloop.IOLoop.current().stop()
    print("Server stopped")

def make_app():
    static_path = os.path.join(os.path.dirname(__file__), "static")
    #outside the project folder
    file_root_path = os.path.dirname(os.path.dirname(__file__))
    print("static_path", static_path)
    print("root_path", file_root_path)
    return tornado.web.Application([
        (r"/toolbox/tool_downloader", VMDownloaderPageHandler, {'static_path': static_path}),
        (r"/toolbox/tool_downloader/api", VMDownloaderAPIHandler, {'static_path': static_path}),
        (r"/toolbox/tool_downloader/websocket/dd", VMDownloaderWebsocketHandler),
        (r"/toolbox/app2", MainHandler),
        (r"/toolbox/rs_icon/(.*?)$", VMDownloaderIconHandler, {'static_path': file_root_path}),
        (r"/toolbox/static/(.*?)$", StaticFileHandler, {'path': static_path})
    ], debug=True)  # Set debug mode

if __name__ == "__main__":
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"

    if debug_mode:
        # Start a debugpy listener
        import tornado.autoreload
        tornado.autoreload.start()
        debugpy.listen(('localhost', 5678))
        print("Debug server running on port 5678")

    port = 8888
    app = make_app()
    app.listen(port)
    print(f"Server started at port {port}")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    tornado.ioloop.IOLoop.current().start()

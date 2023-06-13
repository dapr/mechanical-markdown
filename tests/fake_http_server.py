

from threading import Thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class EmptyReplyHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def do_GET(self):
        self.send_response(next(self.server.response_code_generator))
        self.send_header('Content-Length', 0)
        self.end_headers()


class FakeHttpServer(Thread):
    def __init__(self):
        super().__init__()
        self.server = ThreadingHTTPServer(('localhost', 0), EmptyReplyHandler)
        self.response_codes = []

    def set_response_codes(self, codes):
        def response_code_generator():
            for response_code in codes:
                yield response_code
        self.server.response_code_generator = response_code_generator()

    def get_port(self):
        return self.server.socket.getsockname()[1]

    def shutdown_server(self, timeout=5):
        self.server.shutdown()
        self.server.socket.close()
        self.join(timeout=timeout)

    def run(self):
        self.server.serve_forever()

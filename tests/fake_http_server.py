

from threading import Thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class EmptyReplyHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def _send_code(self, generator):
        self.send_response(next(generator))
        self.send_header('Content-Length', 0)
        self.end_headers()

    def do_GET(self):
        self._send_code(self.server.get_response_code_generator)

    def do_HEAD(self):
        self._send_code(self.server.head_response_code_generator)


class FakeHttpServer(Thread):
    def __init__(self):
        super().__init__()
        self.server = ThreadingHTTPServer(('localhost', 0), EmptyReplyHandler)

    def set_response_codes(self, codes, head_codes=None):
        def make_generator(c):
            for code in c:
                yield code
        self.server.get_response_code_generator = make_generator(codes)
        self.server.head_response_code_generator = make_generator(head_codes if head_codes is not None else codes)

    def get_port(self):
        return self.server.socket.getsockname()[1]

    def shutdown_server(self, timeout=5):
        self.server.shutdown()
        self.server.socket.close()
        self.join(timeout=timeout)

    def run(self):
        self.server.serve_forever()

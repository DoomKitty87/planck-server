from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostname = "localhost"
port = "80"

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(f"Server started! Current Unix time is {time.time()}")

if __name__ == "__main__":        
    web_server = HTTPServer((hostname, port), Server)
    print(f"Server started! Current Unix time is {time.time()}")

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print("Server stopped.")
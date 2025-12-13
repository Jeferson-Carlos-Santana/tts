
import os
import json, asyncio, uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
import edge_tts

BASE_DIR = r"/usr/local/lsws/Example/html/fyninglez/media/cache"
os.makedirs(BASE_DIR, exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length"))
        data = json.loads(self.rfile.read(length))
        text = data.get("text", "")

        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(BASE_DIR, filename)

        async def run():
            await edge_tts.Communicate(
                text=text,
                voice="en-US-AvaNeural"
            ).save(filepath)

        asyncio.run(run())

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"file": filename}).encode())

server = HTTPServer(("127.0.0.1", 9000), Handler)
print("TTS em http://127.0.0.1:9000")
server.serve_forever()

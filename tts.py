
import os
import json, asyncio, hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import edge_tts

BASE_DIR = r"/usr/local/lsws/Example/html/demo/media/cache"
os.makedirs(BASE_DIR, exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length"))
        data = json.loads(self.rfile.read(length))
        text = data.get("text", "").strip()

        if not text:
            self.send_response(400)
            self.end_headers()
            return

        # 🔑 NOME DETERMINÍSTICO (CACHE)
        filename = hashlib.md5(text.encode("utf-8")).hexdigest() + ".mp3"
        filepath = os.path.join(BASE_DIR, filename)

        # ✅ SE JÁ EXISTE, NÃO GERA DE NOVO
        if not os.path.exists(filepath):
            async def run():
                await edge_tts.Communicate(
                    text=text,
                    voice="en-US-AvaNeural"
                ).save(filepath)

            asyncio.run(run())

        # resposta (igual ao antigo)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"file": filename}).encode()
        )

# server = HTTPServer(("127.0.0.1", 9000), Handler)
server = HTTPServer(("0.0.0.0", 9000), Handler)
print("TTS em http://127.0.0.1:9000")
server.serve_forever()


# import os
# import json, asyncio, uuid
# from http.server import BaseHTTPRequestHandler, HTTPServer
# import edge_tts

# BASE_DIR = r"/usr/local/lsws/Example/html/demo/media/cache"

# os.makedirs(BASE_DIR, exist_ok=True)

# class Handler(BaseHTTPRequestHandler):
#     def do_POST(self):
#         length = int(self.headers.get("Content-Length"))
#         data = json.loads(self.rfile.read(length))
#         text = data.get("text", "")

#         filename = f"{uuid.uuid4()}.mp3"
#         filepath = os.path.join(BASE_DIR, filename)

#         async def run():
#             await edge_tts.Communicate(
#                 text=text,
#                 voice="en-US-AvaNeural"
#             ).save(filepath)

#         asyncio.run(run())

#         self.send_response(200)
#         self.send_header("Content-Type", "application/json")
#         self.end_headers()
#         self.wfile.write(json.dumps({"file": filename}).encode())

# # server = HTTPServer(("127.0.0.1", 9000), Handler)
# server = HTTPServer(("0.0.0.0", 9000), Handler)
# print("TTS em http://127.0.0.1:9000")
# server.serve_forever()

import os
import json, asyncio, hashlib, shutil
from http.server import BaseHTTPRequestHandler, HTTPServer
import edge_tts

BASE_DIR = r"/usr/local/lsws/Example/html/demo/media/cache"
CACHE_DIR = os.path.join(BASE_DIR, "_tts_cache")

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

VOICE = "en-US-AvaNeural"

def gerar_audio_cache(texto, arquivo_saida):
    key = hashlib.md5(f"{texto}_{VOICE}".encode("utf-8")).hexdigest()
    cache_file = os.path.join(CACHE_DIR, f"{key}.mp3")

    # ✅ CACHE HIT
    if os.path.exists(cache_file):
        shutil.copy(cache_file, arquivo_saida)
        return

    # ❌ CACHE MISS → gera UMA VEZ
    async def run():
        await edge_tts.Communicate(
            text=texto,
            voice=VOICE
        ).save(cache_file)

    asyncio.run(run())
    shutil.copy(cache_file, arquivo_saida)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length"))
        data = json.loads(self.rfile.read(length))
        text = data.get("text", "").strip()

        if not text:
            self.send_response(400)
            self.end_headers()
            return

        # arquivo FINAL (sempre único por request)
        filename = hashlib.md5(text.encode("utf-8")).hexdigest() + ".mp3"
        out_path = os.path.join(BASE_DIR, filename)

        gerar_audio_cache(text, out_path)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"file": filename}).encode())

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

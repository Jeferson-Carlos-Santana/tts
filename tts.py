import os
import json
import asyncio
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import edge_tts

BASE_DIR = r"/usr/local/lsws/Example/html/demo/media/cache"
os.makedirs(BASE_DIR, exist_ok=True)

# ✅ mantém comportamento atual (default)
VOICE_DEFAULT = "en-US-AvaNeural"

# ✅ novas vozes por idioma (você pode trocar depois)
VOICE_EN = "en-GB-RyanNeural"
VOICE_PT = "pt-BR-AntonioNeural"

RATE_PT = "+25%"
RATE_EN = "-7%"

def filename_from_text(texto: str, voice: str) -> str:
    # 🔥 mesmo padrão (hash), só que agora inclui a voz escolhida
    # (assim não mistura PT e EN no mesmo arquivo)
    key = hashlib.md5(f"{texto}_{voice}".encode("utf-8")).hexdigest()
    return f"{key}.mp3"

# def gerar_audio(texto: str, voice: str) -> str:
#     filename = filename_from_text(texto, voice)
#     out_path = os.path.join(BASE_DIR, filename)

#     # ✅ se já existe, não gera de novo
#     if os.path.exists(out_path):
#         return filename

#     async def run():
#         await edge_tts.Communicate(text=texto, voice=voice).save(out_path)

#     asyncio.run(run())
#     return filename

# def escolher_voz(data: dict) -> str:
#     # prioridade: voice explícita > lang > default
#     voice = (data.get("voice") or "").strip()
#     if voice:
#         return voice

#     lang = (data.get("lang") or "").strip().lower()
#     if lang == "pt":
#         return VOICE_PT
#     if lang == "en":
#         return VOICE_EN

#     return VOICE_DEFAULT

def gerar_audio(texto: str, voice: str, rate: str | None) -> str:
    key = hashlib.md5(f"{texto}_{voice}_{rate}".encode("utf-8")).hexdigest()
    filename = f"{key}.mp3"
    out_path = os.path.join(BASE_DIR, filename)

    if os.path.exists(out_path):
        return filename

    async def run():
        if rate:
            await edge_tts.Communicate(
                text=texto,
                voice=voice,
                rate=rate
            ).save(out_path)
        else:
            await edge_tts.Communicate(
                text=texto,
                voice=voice
            ).save(out_path)

    asyncio.run(run())
    return filename

def escolher_voz(data: dict):
    voice = (data.get("voice") or "").strip()
    if voice:
        return voice, None  # rate opcional

    lang = (data.get("lang") or "").strip().lower()
    if lang == "pt":
        return VOICE_PT, RATE_PT
    if lang == "en":
        return VOICE_EN, RATE_EN

    return VOICE_DEFAULT, None


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        data = json.loads(self.rfile.read(length) or b"{}")
        text = (data.get("text") or "").strip()
        
        with open("/tmp/tts_debug.log", "a", encoding="utf-8") as f:
            f.write(f"TTS_RECV -> text={text!r} lang={data.get('lang')}\n")

        if not text:
            self.send_response(400)
            self.end_headers()
            return

        voice, rate = escolher_voz(data)
        filename = gerar_audio(text, voice, rate)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"file": filename}).encode())

server = HTTPServer(("0.0.0.0", 9000), Handler)
print("TTS em http://127.0.0.1:9000")
server.serve_forever()


# SEGUNDA VERSAO
# import os
# import json
# import asyncio
# import hashlib
# from http.server import BaseHTTPRequestHandler, HTTPServer
# import edge_tts

# BASE_DIR = r"/usr/local/lsws/Example/html/demo/media/cache"
# os.makedirs(BASE_DIR, exist_ok=True)

# VOICE = "en-US-AvaNeural"

# def filename_from_text(texto: str) -> str:
#     # 🔥 um único padrão de nome (sempre o mesmo)
#     key = hashlib.md5(f"{texto}_{VOICE}".encode("utf-8")).hexdigest()
#     return f"{key}.mp3"

# def gerar_audio(texto: str) -> str:
#     filename = filename_from_text(texto)
#     out_path = os.path.join(BASE_DIR, filename)

#     # ✅ se já existe, não gera de novo
#     if os.path.exists(out_path):
#         return filename

#     async def run():
#         await edge_tts.Communicate(text=texto, voice=VOICE).save(out_path)

#     asyncio.run(run())
#     return filename

# class Handler(BaseHTTPRequestHandler):
#     def do_POST(self):
#         length = int(self.headers.get("Content-Length", "0"))
#         data = json.loads(self.rfile.read(length) or b"{}")
#         text = (data.get("text") or "").strip()

#         if not text:
#             self.send_response(400)
#             self.end_headers()
#             return

#         filename = gerar_audio(text)

#         self.send_response(200)
#         self.send_header("Content-Type", "application/json")
#         self.end_headers()
#         self.wfile.write(json.dumps({"file": filename}).encode())

# server = HTTPServer(("0.0.0.0", 9000), Handler)
# print("TTS em http://127.0.0.1:9000")
# server.serve_forever()





# PRIMEIRA VERSAO
# import os
# import json, asyncio, hashlib, shutil, time
# from http.server import BaseHTTPRequestHandler, HTTPServer
# import edge_tts

# BASE_DIR = r"/usr/local/lsws/Example/html/demo/media/cache"
# CACHE_DIR = os.path.join(BASE_DIR, "_tts_cache")

# os.makedirs(BASE_DIR, exist_ok=True)
# os.makedirs(CACHE_DIR, exist_ok=True)

# VOICE = "en-US-AvaNeural"

# def gerar_audio_cache(texto):
#     key = hashlib.md5(f"{texto}_{VOICE}".encode("utf-8")).hexdigest()
#     cache_file = os.path.join(CACHE_DIR, f"{key}.mp3")
#     out_path = os.path.join(BASE_DIR, f"{key}.mp3")

#     if not os.path.exists(cache_file):
#         async def run():
#             await edge_tts.Communicate(text=texto, voice=VOICE).save(cache_file)
#         asyncio.run(run())

#     shutil.copy(cache_file, out_path)
#     return f"{key}.mp3"

# class Handler(BaseHTTPRequestHandler):
#     def do_POST(self):
#         length = int(self.headers.get("Content-Length"))
#         data = json.loads(self.rfile.read(length))
#         text = data.get("text", "").strip()

#         if not text:
#             self.send_response(400)
#             self.end_headers()
#             return

#         filename = hashlib.md5(text.encode("utf-8")).hexdigest() + ".mp3"
#         out_path = os.path.join(BASE_DIR, filename)

#         gerar_audio_cache(text, out_path)

#         self.send_response(200)
#         self.send_header("Content-Type", "application/json")
#         self.end_headers()
#         self.wfile.write(json.dumps({"file": filename}).encode())

# server = HTTPServer(("0.0.0.0", 9000), Handler)
# print("TTS em http://127.0.0.1:9000")
# server.serve_forever()

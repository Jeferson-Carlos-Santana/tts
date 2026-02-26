import os
import json
import asyncio
import hashlib
import multiprocessing
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import edge_tts

BASE_DIR = r"/usr/local/lsws/Example/html/demo/media/cache"
BASE_FIXOS = os.path.join(BASE_DIR, "fixos")
BASE_TMP   = os.path.join(BASE_DIR, "tmp")
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(BASE_FIXOS, exist_ok=True)
os.makedirs(BASE_TMP, exist_ok=True)

# mantém comportamento atual (default)
VOICE_DEFAULT = "en-US-AvaNeural"

# novas vozes por idioma (você pode trocar depois)
# VOICE_EN = "en-GB-RyanNeural"
# VOICE_PT = "pt-BR-AntonioNeural"

VOICE_EN_GB = "en-GB-SoniaNeural"
VOICE_EN_US = "en-US-GuyNeural"

VOICE_EN = "en-GB-SoniaNeural"
VOICE_PT = "pt-BR-FranciscaNeural"

RATE_PT = "+25%"
RATE_EN = "-20%"

def filename_from_text(texto: str, voice: str) -> str:
    # (assim não mistura PT e EN no mesmo arquivo)
    key = hashlib.md5(f"{texto}_{voice}".encode("utf-8")).hexdigest()
    return f"{key}.mp3"

def gerar_audio(texto: str, voice: str, rate: str | None, fixed: bool = False) -> str:
    key = hashlib.md5(f"{texto}_{voice}_{rate}".encode("utf-8")).hexdigest()
    filename = f"{key}.mp3"

    base = BASE_FIXOS if fixed else BASE_TMP
    out_path = os.path.join(base, filename)

    rel_path = f"fixos/{filename}" if fixed else f"tmp/{filename}"

    if os.path.exists(out_path):
        return rel_path

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
    return rel_path

# def escolher_voz(data: dict):
#     voice = (data.get("voice") or "").strip()
#     if voice:
#         return voice, None  # rate opcional

#     lang = (data.get("lang") or "").strip().lower()
#     if lang == "pt":
#         return VOICE_PT, RATE_PT
#     if lang == "en":
#         return VOICE_EN, RATE_EN

#     return VOICE_DEFAULT, None

def escolher_voz(data: dict):
    voice = (data.get("voice") or "").strip()
    if voice:
        return voice, None

    lang = (data.get("lang") or "").strip().lower()

    if lang == "pt":
        return VOICE_PT, RATE_PT

    if lang == "en":
        variant = (data.get("english_variant") or "uk").lower()

        if variant == "us":
            return VOICE_EN_US, RATE_EN
        else:
            return VOICE_EN_GB, RATE_EN

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
        # filename = gerar_audio(text, voice, rate)
        fixed = bool(data.get("fixed"))
        filename = gerar_audio(text, voice, rate, fixed=fixed)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"file": filename}).encode())

# RETORNA PARA UMA VERSAO ESTAVEL DESCOMENTE B789
# server = ThreadingHTTPServer(("0.0.0.0", 9000), Handler)
# print("TTS em http://127.0.0.1:9000")
# server.serve_forever()

# RETORNA PARA UMA VERSAO ESTAVEL COMENTE DAQUI PRA BAIXO B789
def start_server(port):
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"TTS rodando na porta {port}")
    server.serve_forever()

if __name__ == "__main__":
    ports = [9000]  # alimentar aqui PORTS = [9000,9001,9002,9003,9004,9005,9006,9007]

    processes = []
    for port in ports:
        p = multiprocessing.Process(target=start_server, args=(port,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


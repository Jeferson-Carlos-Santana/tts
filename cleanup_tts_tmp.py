import os
import time

TMP_DIR = "/usr/local/lsws/Example/html/demo/media/cache/tmp"
TTL = 10080 * 60  # * 60 significa vezes  segundos(60)

now = time.time()

for fname in os.listdir(TMP_DIR):
    path = os.path.join(TMP_DIR, fname)
    if not os.path.isfile(path):
        continue

    age = now - os.path.getmtime(path)
    if age > TTL:
        try:
            os.remove(path)
        except:
            pass

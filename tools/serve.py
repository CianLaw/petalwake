#!/usr/bin/env python3
"""Static dev server with caching off, plus a local-only endpoint the game's debug hook uses to
save full-resolution frame captures into .shots/ (POST /__save/<name>).

    python3 tools/serve.py [port] [host]        default: port 6280 on 127.0.0.1 (this machine only)

Pass 0.0.0.0 as the host to reach it from other devices on your network. Hidden files and folders
(.git, .shots, ...) are never served, and captures are only accepted from a page this server itself
served to a browser on this machine.
"""
import functools, http.server, os, re, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, ".shots")
MAX_SAVE = 64 << 20          # bytes: the largest capture accepted
LOCAL = ("localhost", "127.0.0.1", "[::1]")


class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".js": "text/javascript", ".mjs": "text/javascript",
                      ".glb": "model/gltf-binary", ".bin": "application/octet-stream",
                      ".u16": "application/octet-stream", ".wasm": "application/wasm"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_head(self):
        path = urllib.parse.unquote(self.path.split("?")[0].split("#")[0])
        if any(part.startswith(".") for part in path.replace("\\", "/").split("/") if part not in ("", ".")):
            self.send_error(404)
            return None
        return super().send_head()

    def do_POST(self):
        name = os.path.basename(self.path.split("?")[0])
        host = self.headers.get("Host", "")
        origin = self.headers.get("Origin")
        try:
            size = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            size = -1
        ok = (self.path.startswith("/__save/")
              and self.client_address[0] in ("127.0.0.1", "::1")
              and host.rsplit(":", 1)[0] in LOCAL
              and origin in (None, "http://" + host)       # not a form on some other site
              and 0 < size <= MAX_SAVE
              and re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,79}\.(png|jpg|json)", name))
        if not ok:
            self.send_error(404)
            return
        data = self.rfile.read(size)
        os.makedirs(SHOTS, exist_ok=True)
        with open(os.path.join(SHOTS, name), "wb") as f:
            f.write(data)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *a):  # keep the preview log readable
        pass


port = int(sys.argv[1]) if len(sys.argv) > 1 else 6280
host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
print(f"Petalwake: http://{'localhost' if host == '127.0.0.1' else host}:{port}/", flush=True)
http.server.ThreadingHTTPServer((host, port), functools.partial(H, directory=ROOT)).serve_forever()

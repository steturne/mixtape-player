#!/usr/bin/env python3
"""Mixtape search helper: YouTube search with no API key and no quota, using yt-dlp.

Run it and leave it open while you use Mixtape:   python mixtape_search.py
(first time: pip install yt-dlp; keep it fresh with: pip install -U yt-dlp)

Mixtape asks it:  http://127.0.0.1:8765/search?q=daft+punk+one+more+time&n=10
and gets back:    {"ok":true,"items":[{"id","title","author","dur","thumb"}, ...]}
It only finds video IDs; the Mixtape player still plays them through YouTube's own embed.
It listens on this computer only (127.0.0.1), so nothing else on your network can use it.
"""
import json, sys, time, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

try:
    import yt_dlp
except ImportError:
    sys.exit("yt-dlp is missing. Install it with:  pip install yt-dlp")

PORT = 8765
CACHE_SECONDS = 3 * 24 * 3600          # the same search again within 3 days is answered from memory
cache, lock = {}, threading.Lock()
YDL = {"quiet": True, "no_warnings": True, "skip_download": True, "extract_flat": "in_playlist"}


def search(q, n):
    key = (q.lower(), n)
    with lock:
        hit = cache.get(key)
        if hit and time.time() - hit[0] < CACHE_SECONDS:
            return hit[1]
    with yt_dlp.YoutubeDL(YDL) as ydl:
        info = ydl.extract_info(f"ytsearch{n}:{q}", download=False)
    items = []
    for e in info.get("entries") or []:
        if not e or not e.get("id") or e.get("ie_key") not in (None, "Youtube"):
            continue                    # skip channels/playlists that sometimes show up in results
        thumbs = e.get("thumbnails") or []
        items.append({
            "id": e["id"],
            "title": e.get("title") or "",
            "author": e.get("channel") or e.get("uploader") or "",
            "dur": e.get("duration"),   # seconds, or null for live streams
            "thumb": thumbs[-1]["url"] if thumbs else f"https://i.ytimg.com/vi/{e['id']}/hqdefault.jpg",
        })
    with lock:
        cache[key] = (time.time(), items)
    return items


class Handler(BaseHTTPRequestHandler):
    def _head(self, code):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")            # Mixtape is opened from a file, so its origin is "null"
        self.send_header("Access-Control-Allow-Private-Network", "true")  # lets Chrome/Edge pages reach 127.0.0.1
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self._head(204)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/ping":
            return self._send(200, {"ok": True, "yt_dlp": yt_dlp.version.__version__})
        if u.path != "/search":
            return self._send(404, {"ok": False, "error": "not found"})
        p = parse_qs(u.query)
        q = (p.get("q") or [""])[0].strip()[:200]
        try:
            n = max(1, min(25, int((p.get("n") or ["10"])[0])))
        except ValueError:
            n = 10
        if not q:
            return self._send(400, {"ok": False, "error": "empty search"})
        try:
            self._send(200, {"ok": True, "items": search(q, n)})
        except Exception as e:          # usually YouTube changed something: pip install -U yt-dlp
            self._send(502, {"ok": False, "error": str(e)[:300]})

    def _send(self, code, obj):
        self._head(code)
        self.wfile.write(json.dumps(obj).encode())

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"Mixtape search helper running on http://127.0.0.1:{PORT}  (close this window to stop it)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

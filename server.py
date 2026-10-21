#!/usr/bin/env python3
"""DDL.MISSION local server: static files + /api/tasks JSON store."""
import json
import os
import subprocess
import tempfile
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'tasks.json')
SETTINGS = os.path.join(ROOT, 'settings.json')
LOCK = threading.Lock()


ALLOWED_ORIGIN_PREFIXES = ('http://127.0.0.1', 'http://localhost')
ALLOWED_ORIGINS = ('https://zc-ruc.github.io',)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, fmt, *args):
        pass

    def _cors_origin(self):
        origin = self.headers.get('Origin') if self.headers else None
        if origin == 'null' or origin in ALLOWED_ORIGINS or \
                (origin and origin.startswith(ALLOWED_ORIGIN_PREFIXES)):
            return origin
        return None

    def _send_cors(self):
        o = self._cors_origin()
        if o:
            self.send_header('Access-Control-Allow-Origin', o)
            self.send_header('Access-Control-Allow-Private-Network', 'true')
            self.send_header('Vary', 'Origin')

    def do_OPTIONS(self):
        self.send_response(204)
        o = self._cors_origin()
        if o:
            self.send_header('Access-Control-Allow-Origin', o)
            self.send_header('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Access-Control-Allow-Private-Network', 'true')
            self.send_header('Vary', 'Origin')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self._send_cors()
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/api/tasks':
            with LOCK:
                try:
                    with open(DATA, encoding='utf-8') as f:
                        data = json.load(f)
                except Exception:
                    data = []
            self._send_json(data if isinstance(data, list) else [])
        elif path == '/api/settings':
            with LOCK:
                try:
                    with open(SETTINGS, encoding='utf-8') as f:
                        data = json.load(f)
                except Exception:
                    data = {}
            self._send_json(data if isinstance(data, dict) else {})
        else:
            super().do_GET()

    def do_PUT(self):
        path = self.path.split('?')[0]
        if path == '/api/tasks':
            try:
                n = int(self.headers.get('Content-Length') or 0)
                data = json.loads(self.rfile.read(n) or b'[]')
                if not isinstance(data, list):
                    raise ValueError('not a list')
            except Exception:
                self._send_json({'ok': False}, 400)
                return
            with LOCK:
                fd, tmp = tempfile.mkstemp(dir=ROOT, suffix='.json')
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)
                os.replace(tmp, DATA)
            self._send_json({'ok': True})
        elif path == '/api/settings':
            try:
                n = int(self.headers.get('Content-Length') or 0)
                data = json.loads(self.rfile.read(n) or b'{}')
                if not isinstance(data, dict):
                    raise ValueError('not a dict')
            except Exception:
                self._send_json({'ok': False}, 400)
                return
            with LOCK:
                try:
                    with open(SETTINGS, encoding='utf-8') as f:
                        cur = json.load(f)
                except Exception:
                    cur = {}
                if not isinstance(cur, dict):
                    cur = {}
                cur.update(data)
                fd, tmp = tempfile.mkstemp(dir=ROOT, suffix='.json')
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(cur, f, ensure_ascii=False)
                os.replace(tmp, SETTINGS)
            self._send_json({'ok': True})
        else:
            self.send_error(404)


NOTIFY_STATE = os.path.join(ROOT, 'notify-state.json')
THRESHOLDS = {86400: 'T-24h', 3600: 'T-1h', 0: '已逾期'}


def _load_notify_state():
    try:
        with open(NOTIFY_STATE, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save_notify_state(s):
    try:
        with open(NOTIFY_STATE, 'w', encoding='utf-8') as f:
            json.dump(s, f)
    except Exception:
        pass


def _notify(title, body):
    def q(s):
        return str(s).replace('\\', '\\\\').replace('"', '\\"')
    try:
        subprocess.run(
            ['osascript', '-e',
             'display notification "%s" with title "%s" sound name "Ping"' % (q(body), q(title))],
            timeout=10, capture_output=True)
    except Exception:
        pass


def _fmt_remain(sec):
    overdue = sec < 0
    sec = abs(int(sec))
    d, sec = divmod(sec, 86400)
    h, sec = divmod(sec, 3600)
    m = sec // 60
    core = '%dd %02d:%02d' % (d, h, m) if d else '%02d:%02d' % (h, m)
    return ('T+' if overdue else 'T-') + core


def notifier_loop():
    while True:
        try:
            with LOCK:
                try:
                    with open(DATA, encoding='utf-8') as f:
                        tasks = json.load(f)
                except Exception:
                    tasks = []
            now = time.time()
            state = _load_notify_state()
            changed = False
            for t in tasks:
                if not isinstance(t, dict) or t.get('done') or not t.get('due'):
                    continue
                due = t['due'] / 1000.0
                passed = [th for th in THRESHOLDS if now >= due - th]
                unfired = [th for th in passed
                           if '%s:%s:%s' % (t.get('id'), t.get('due'), th) not in state]
                if not unfired:
                    continue
                th = min(unfired)
                for p in passed:
                    state['%s:%s:%s' % (t.get('id'), t.get('due'), p)] = int(now)
                changed = True
                _notify('DDL %s' % THRESHOLDS[th],
                        '%s（%s）' % (t.get('title', ''), _fmt_remain(due - now)))
            if changed:
                _save_notify_state(state)
        except Exception:
            pass
        time.sleep(60)


if __name__ == '__main__':
    threading.Thread(target=notifier_loop, daemon=True).start()
    ThreadingHTTPServer(('0.0.0.0', 8791), Handler).serve_forever()

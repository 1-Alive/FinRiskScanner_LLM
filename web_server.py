"""Local web UI for the Indonesian app classification agent."""

import json
import mimetypes
import os
from argparse import Namespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from app_classifier_agent import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    ClassificationError,
    classify,
    load_json_value,
)


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"


class AppClassifierHandler(BaseHTTPRequestHandler):
    server_version = "AppClassifierWeb/1.0"

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.serve_file(STATIC_DIR / "index.html")
            return
        if path.startswith("/static/"):
            relative = path.removeprefix("/static/").lstrip("/")
            self.serve_file(STATIC_DIR / relative)
            return
        self.send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        if urlparse(self.path).path != "/api/classify":
            self.send_json({"error": "Not found"}, status=404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            request_payload = json.loads(body)
            app_json = request_payload.get("input_json", "")
            payload = load_json_value(app_json)
            args = Namespace(
                api_key=request_payload.get("api_key") or None,
                base_url=request_payload.get("base_url") or DEFAULT_BASE_URL,
                model=request_payload.get("model") or DEFAULT_MODEL,
                temperature=float(request_payload.get("temperature", 0.0)),
                batch_size=max(1, int(request_payload.get("batch_size", 20))),
                timeout=max(10, int(request_payload.get("timeout", DEFAULT_TIMEOUT))),
                retries=max(0, int(request_payload.get("retries", 2))),
            )
            result = classify(payload, args)
            self.send_json({"result": result})
        except (ClassificationError, json.JSONDecodeError, ValueError) as exc:
            self.send_json({"error": str(exc)}, status=400)
        except Exception as exc:
            self.send_json({"error": f"服务异常: {exc}"}, status=500)

    def serve_file(self, path):
        try:
            resolved = path.resolve()
            try:
                resolved.relative_to(STATIC_DIR.resolve())
            except ValueError:
                self.send_json({"error": "Forbidden"}, status=403)
                return
            if not resolved.is_file():
                self.send_json({"error": "Not found"}, status=404)
                return
            content_type = mimetypes.guess_type(str(resolved))[0] or "application/octet-stream"
            data = resolved.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except OSError as exc:
            self.send_json({"error": str(exc)}, status=500)

    def send_json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))


def main():
    host = os.getenv("APP_CLASSIFIER_HOST", "127.0.0.1")
    port = int(os.getenv("APP_CLASSIFIER_PORT", "8765"))
    server = ThreadingHTTPServer((host, port), AppClassifierHandler)
    print(f"App 分类打标工具已启动: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

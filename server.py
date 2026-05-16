from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import os
import sys
import subprocess
import webbrowser


ROOT = Path(__file__).resolve().parent
BAT_FILE = ROOT / "WoreSearch" / "Get_News.bat"


class NewsHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)

        if url.path == "/api/search":
            self.handle_search(url.query)
            return

        if url.path.startswith("/api/"):
            self.write_json({"ok": False, "error": "API path not found.", "results": []}, 404)
            return

        if url.path in ("/", "/web"):
            self.path = "/index.html"

        super().do_GET()

    def handle_search(self, query_string):
        params = parse_qs(query_string)
        query = (params.get("q", [""])[0] or "").strip()

        if not query:
            self.write_json({"ok": False, "error": "Search text is required.", "results": []}, 400)
            return

        try:
            env = os.environ.copy()
            env["PYGETDATE_QUERY"] = query
            completed = subprocess.run(
                ["cmd", "/d", "/c", "call", str(BAT_FILE)],
                cwd=str(BAT_FILE.parent),
                capture_output=True,
                env=env,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            self.write_json({"ok": False, "error": "Search timed out.", "results": []}, 504)
            return

        output = completed.stdout.strip()

        try:
            payload = json.loads(output)
        except json.JSONDecodeError:
            payload = {
                "ok": False,
                "error": "The batch file did not return valid JSON.",
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "results": [],
            }

        status = 200 if payload.get("ok") else 502
        self.write_json(payload, status)

    def write_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def start_server():
    requested_port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    should_open = "--open" in sys.argv
    ports = [requested_port, 8080, 3000, 5000, 49152, 51000, 55000]
    seen = set()

    for port in ports:
        if port in seen:
            continue
        seen.add(port)

        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), NewsHandler)
        except OSError as error:
            print(f"Port {port} is not available: {error}")
            continue

        url = f"http://127.0.0.1:{port}/web"
        print(f"Open {url}")
        if should_open:
            webbrowser.open(url)
        server.serve_forever()
        return

    raise SystemExit("No local port was available. Try running: python server.py 56000")


if __name__ == "__main__":
    start_server()

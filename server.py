import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from builder import TreeBuilder

STATIC = Path(__file__).parent / "static"
TREE = TreeBuilder.default()


class ApiHandler(SimpleHTTPRequestHandler):
    """Serves the frontend and a tiny JSON API over the decision tree."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def do_GET(self):
        url = urlparse(self.path)
        if not url.path.startswith("/api/"):
            return super().do_GET()
        params = {key: values[0] for key, values in parse_qs(url.query).items()}
        try:
            self.send_json(self.route(url.path.removeprefix("/api/"), params))
        except (KeyError, ValueError) as error:
            self.send_json({"error": str(error)}, status=404)

    @staticmethod
    def route(name: str, params: dict):
        if name == "tree":
            return {"tree": TREE.root.to_dict(), "stats": TREE.stats()}
        if name == "traverse":
            return [node.id for node in TREE.traverse(params.get("mode", "bfs"))]
        if name == "step":
            return TREE.step(params["id"], params["answer"] == "yes").to_dict(deep=False)
        raise KeyError(f"unknown endpoint: {name}")

    def send_json(self, payload, status: int = 200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("Triage Tree running at http://127.0.0.1:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), ApiHandler).serve_forever()

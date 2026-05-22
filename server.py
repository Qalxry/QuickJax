#!/usr/bin/env python3
"""QuickJax HTTP API server.

启动：
    python server.py --host 127.0.0.1 --port 8000

接口：
    GET  /health                     健康检查
    POST /render                     渲染 LaTeX，返回 JSON（含 SVG 字段）
    GET  /render?latex=...           同上，GET 方式
    POST /render/svg                 渲染 LaTeX，直接返回原始 SVG
    GET  /render/svg?latex=...       同上，GET 方式
    POST /svg                        渲染 LaTeX，直接返回原始 SVG（短别名）
    GET  /svg?latex=...              同上，GET 方式（短别名）

示例：
    curl -X POST http://127.0.0.1:8000/render \
      -H 'Content-Type: application/json' \
      -d '{"latex":"E = mc^2", "display":true}'

    curl -X POST http://127.0.0.1:8000/render/svg \
      -H 'Content-Type: application/json' \
      -d '{"latex":"E = mc^2"}' > equation.svg
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from quickjax import MathJaxRenderError, MathJaxRenderer, __version__


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
MAX_BODY_BYTES = 1024 * 1024


class RendererService:
    """Thread-safe wrapper around one reusable MathJax renderer."""

    def __init__(self) -> None:
        self._renderer = MathJaxRenderer()
        self._lock = threading.Lock()

    def render(self, latex: str, *, display: bool = True) -> str:
        # quickjs.Context is not guaranteed to be thread-safe. Keep one warm
        # MathJax context and serialize access to it.
        with self._lock:
            return self._renderer.render(latex, display=display)


class QuickJaxRequestHandler(BaseHTTPRequestHandler):
    """Small JSON API for rendering LaTeX to MathJax SVG."""

    server_version = f"QuickJaxHTTP/{__version__}"

    @property
    def renderer_service(self) -> RendererService:
        return self.server.renderer_service  # type: ignore[attr-defined]

    def do_OPTIONS(self) -> None:
        self._send_empty(HTTPStatus.NO_CONTENT)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "service": "quickjax",
                    "version": __version__,
                },
            )
            return

        if parsed.path in ("/render",):
            params = parse_qs(parsed.query, keep_blank_values=True)
            latex = self._first(params, "latex", "tex", "q")
            display = self._parse_bool(self._first(params, "display"), default=True)
            if latex is None:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": "Missing query parameter: latex"},
                )
                return
            self._render_and_send(latex, display=display)
            return

        if parsed.path in ("/render/svg", "/svg"):
            params = parse_qs(parsed.query, keep_blank_values=True)
            latex = self._first(params, "latex", "tex", "q")
            display = self._parse_bool(self._first(params, "display"), default=True)
            if latex is None:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": "Missing query parameter: latex"},
                )
                return
            self._render_and_send_svg(latex, display=display)
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "Not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        # Determine if this is a raw-SVG request
        is_svg = parsed.path in ("/render/svg", "/svg")

        if parsed.path not in ("/render", "/render/svg", "/svg"):
            self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "Not found"})
            return

        try:
            payload = self._read_json_body()
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return

        latex = payload.get("latex", payload.get("tex"))
        display = self._parse_bool(payload.get("display"), default=True)

        if not isinstance(latex, str):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "error": "JSON field 'latex' must be a string"},
            )
            return

        if is_svg:
            self._render_and_send_svg(latex, display=display)
        else:
            self._render_and_send(latex, display=display)

    def _render_and_send(self, latex: str, *, display: bool) -> None:
        start = time.perf_counter()
        try:
            svg = self.renderer_service.render(latex, display=display)
        except MathJaxRenderError as exc:
            self._send_json(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {"ok": False, "error": str(exc)},
            )
            return
        except Exception as exc:  # Defensive: keep server alive on unexpected errors.
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"ok": False, "error": f"Unexpected server error: {exc}"},
            )
            return

        elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "svg": svg,
                "display": display,
                "elapsed_ms": elapsed_ms,
            },
        )

    def _read_json_body(self) -> dict[str, Any]:
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            raise ValueError("Content-Type must be application/json")

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Invalid Content-Length") from exc

        if content_length <= 0:
            raise ValueError("Request body is empty")
        if content_length > MAX_BODY_BYTES:
            raise ValueError(f"Request body is too large; limit is {MAX_BODY_BYTES} bytes")

        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid JSON body: {exc}") from exc

        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_common_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_svg(self, status: HTTPStatus, svg: str) -> None:
        body = svg.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_common_headers()
        self.end_headers()
        self.wfile.write(body)

    def _render_and_send_svg(self, latex: str, *, display: bool) -> None:
        start = time.perf_counter()
        try:
            svg = self.renderer_service.render(latex, display=display)
        except MathJaxRenderError as exc:
            self._send_json(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {"ok": False, "error": str(exc)},
            )
            return
        except Exception as exc:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"ok": False, "error": f"Unexpected server error: {exc}"},
            )
            return

        elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
        self.log_message(f"SVG rendered in {elapsed_ms}ms")
        self._send_svg(HTTPStatus.OK, svg)

    def _send_empty(self, status: HTTPStatus) -> None:
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self._send_common_headers()
        self.end_headers()

    def _send_common_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")

    def log_message(self, format: str, *args: Any) -> None:
        # Keep the default useful access log, but prefix it clearly.
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}")

    @staticmethod
    def _first(params: dict[str, list[str]], *names: str) -> str | None:
        for name in names:
            values = params.get(name)
            if values:
                return values[0]
        return None

    @staticmethod
    def _parse_bool(value: Any, *, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "y", "on"}:
                return True
            if normalized in {"0", "false", "no", "n", "off", "inline"}:
                return False
        return default


class QuickJaxHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], handler_class: type[BaseHTTPRequestHandler]) -> None:
        print("Initializing MathJax renderer...")
        self.renderer_service = RendererService()
        super().__init__(server_address, handler_class)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QuickJax MathJax SVG HTTP API server")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Bind host, default: {DEFAULT_HOST}")
    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help=f"Bind port, default: {DEFAULT_PORT}")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = QuickJaxHTTPServer((args.host, args.port), QuickJaxRequestHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"QuickJax API server listening on {url}")
    print("Endpoints:")
    print("  JSON:   GET /health, POST|GET /render")
    print("  SVG:    POST|GET /render/svg, POST|GET /svg")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

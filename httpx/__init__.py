"""Minimal async HTTPX client stubs for tests.

The real ``httpx`` package is not available in the sandboxed execution
environment, so these classes provide the subset of functionality required by
the repository's test-suite: an ``ASGITransport`` capable of dispatching
requests directly to the in-process ASGI application and an ``AsyncClient``
wrapper that exposes ``request``/context manager APIs. Responses support the
``json`` and ``text`` helpers used by tests.
"""

from __future__ import annotations

import json
from typing import Any, Dict
from urllib.parse import urljoin, urlparse


class Response:
    def __init__(self, status_code: int, headers: Dict[str, str], body: bytes):
        self.status_code = status_code
        self.headers = {k.lower(): v for k, v in headers.items()}
        self._body = body

    @property
    def content(self) -> bytes:
        return self._body

    @property
    def text(self) -> str:
        return self._body.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.text or "null")


class ASGITransport:
    def __init__(self, app: Any):
        self.app = app

    async def handle_async_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        data: bytes,
    ) -> Response:
        parsed = urlparse(url)
        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": method.upper(),
            "path": parsed.path or "/",
            "raw_path": (parsed.path or "/").encode("utf-8"),
            "query_string": (parsed.query or "").encode("utf-8"),
            "headers": [
                (key.lower().encode("latin-1"), value.encode("latin-1"))
                for key, value in headers.items()
            ],
        }
        received = False

        async def receive() -> Dict[str, Any]:
            nonlocal received
            if received:
                return {"type": "http.disconnect"}
            received = True
            return {
                "type": "http.request",
                "body": data,
                "more_body": False,
            }

        messages = []

        async def send(message: Dict[str, Any]) -> None:
            messages.append(message)

        await self.app(scope, receive, send)

        status_code = 500
        response_headers: Dict[str, str] = {}
        body = b""
        for message in messages:
            if message["type"] == "http.response.start":
                status_code = int(message.get("status", 500))
                raw_headers = message.get("headers", [])
                response_headers = {
                    key.decode("latin-1"): value.decode("latin-1")
                    for key, value in raw_headers
                }
            elif message["type"] == "http.response.body":
                body += message.get("body", b"")
        return Response(status_code, response_headers, body)


class AsyncClient:
    def __init__(
        self,
        *,
        transport: ASGITransport,
        base_url: str = "",
    ) -> None:
        self._transport = transport
        self._base_url = base_url.rstrip("/")

    async def __aenter__(self) -> "AsyncClient":  # pragma: no cover - trivial
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - trivial
        return None

    async def request(self, method: str, url: str, **kwargs: Any) -> Response:
        headers = {"host": "testserver"}
        data = b""
        if "json" in kwargs:
            headers["content-type"] = "application/json"
            data = json.dumps(kwargs["json"]).encode("utf-8")
        elif "data" in kwargs:
            data = kwargs["data"] if isinstance(kwargs["data"], bytes) else str(kwargs["data"]).encode("utf-8")
        elif "content" in kwargs:
            data = kwargs["content"]
        target = urljoin(self._base_url + "/", url)
        return await self._transport.handle_async_request(method, target, headers, data)


__all__ = ["ASGITransport", "AsyncClient", "Response"]

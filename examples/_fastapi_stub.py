"""Minimal FastAPI-compatible stubs used when FastAPI isn't installed.

These implementations provide the subset of FastAPI's behaviour required by
the test suite. They support route registration via ``@app.get``/``@app.post``
decorators, HTTP middleware hooks, exception handlers for Pydantic
``ValidationError`` and request validation errors, and JSON/bytes responses.

The goal is not to be feature complete, only to mimic the specific semantics
used by ``examples.fastapi_mcp_integration`` so the reference server remains
testable without pulling the heavy ``fastapi`` dependency into the execution
environment.
"""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Tuple, Type, Union

from pydantic import BaseModel, ValidationError


__all__ = [
    "Body",
    "CORSMiddleware",
    "FastAPI",
    "JSONResponse",
    "Request",
    "RequestValidationError",
    "Response",
    "status",
]


class _Status(SimpleNamespace):
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_404_NOT_FOUND = 404
    HTTP_500_INTERNAL_SERVER_ERROR = 500


status = _Status()


class RequestValidationError(Exception):
    """Mirror FastAPI's request validation error container."""

    def __init__(self, errors: Iterable[Dict[str, Any]]):
        super().__init__("Request validation failed")
        self._errors = list(errors)

    def errors(self) -> List[Dict[str, Any]]:
        return list(self._errors)


class _URL:
    def __init__(self, path: str):
        self.path = path


class Request:
    """Lightweight request object compatible with the reference server."""

    def __init__(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: bytes,
    ) -> None:
        self.method = method.upper()
        self.headers = headers
        self.url = _URL(path)
        self._body = body
        self._json_cache: Any = _UNSET

    @property
    def body(self) -> bytes:
        return self._body

    def json(self) -> Any:
        return self._ensure_json()

    async def json_async(self) -> Any:
        return self._ensure_json()

    def _ensure_json(self) -> Any:
        if self._json_cache is _UNSET:
            if not self._body:
                self._json_cache = {}
            else:
                try:
                    text = self._body.decode("utf-8")
                    self._json_cache = json.loads(text or "null")
                    if self._json_cache is None:
                        self._json_cache = {}
                except json.JSONDecodeError as exc:
                    raise RequestValidationError(
                        [
                            {
                                "loc": ("body",),
                                "msg": str(exc),
                                "type": "value_error.jsondecode",
                            }
                        ]
                    ) from exc
        return self._json_cache


class Response:
    """ASGI response container."""

    def __init__(
        self,
        content: Union[str, bytes],
        *,
        status_code: int = status.HTTP_200_OK,
        media_type: str = "application/json",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        if isinstance(content, str):
            body = content.encode("utf-8")
        else:
            body = content
        self.body = body
        self.status_code = status_code
        self.media_type = media_type
        self.headers = {"content-type": media_type}
        if headers:
            self.headers.update(headers)


class JSONResponse(Response):
    def __init__(self, content: Any, *, status_code: int = status.HTTP_200_OK):
        body = json.dumps(content, ensure_ascii=False).encode("utf-8")
        super().__init__(body, status_code=status_code, media_type="application/json")
        self.content = content


def Body(default: Any = ..., **_: Any) -> Any:  # pragma: no cover - trivial
    return default


class CORSMiddleware:  # pragma: no cover - behaviourless shim
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs


@dataclass
class _Route:
    path: str
    methods: Tuple[str, ...]
    endpoint: Callable[..., Any]

    def match(self, method: str, path: str) -> Optional[Dict[str, str]]:
        if method.upper() not in self.methods:
            return None
        if self.path == path:
            return {}
        template_parts = [part for part in self.path.strip("/").split("/") if part]
        path_parts = [part for part in path.strip("/").split("/") if part]
        if len(template_parts) != len(path_parts):
            return None
        params: Dict[str, str] = {}
        for template, value in zip(template_parts, path_parts):
            if template.startswith("{") and template.endswith("}"):
                params[template[1:-1]] = value
            elif template != value:
                return None
        return params


class FastAPI:
    """Very small FastAPI-like ASGI application."""

    def __init__(self, *, title: str, version: str, description: str = "") -> None:
        self.title = title
        self.version = version
        self.description = description
        self._routes: List[_Route] = []
        self._http_middlewares: List[Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]] = []
        self._exception_handlers: Dict[Type[BaseException], Callable[[Request, BaseException], Awaitable[Response]]] = {}

    # Route registration -------------------------------------------------
    def add_api_route(self, path: str, endpoint: Callable[..., Any], methods: Iterable[str]) -> None:
        methods_tuple = tuple(method.upper() for method in methods)
        self._routes.append(_Route(path=path, methods=methods_tuple, endpoint=endpoint))

    def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, ["GET"])
            return func

        return decorator

    def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, ["POST"])
            return func

        return decorator

    # Middleware + exception handlers -----------------------------------
    def middleware(self, middleware_type: str) -> Callable[[Callable[..., Awaitable[Response]]], Callable[..., Awaitable[Response]]]:
        if middleware_type != "http":  # pragma: no cover - not needed in tests
            raise ValueError("Only 'http' middleware is supported in the stub")

        def decorator(func: Callable[..., Awaitable[Response]]) -> Callable[..., Awaitable[Response]]:
            self._http_middlewares.append(func)
            return func

        return decorator

    def add_middleware(self, _middleware: Type[Any], **_kwargs: Any) -> None:  # pragma: no cover - shim
        # Middleware arguments are ignored; behaviour is covered by explicit middleware decorators.
        return None

    def exception_handler(self, exc_type: Type[BaseException]) -> Callable[[Callable[..., Awaitable[Response]]], Callable[..., Awaitable[Response]]]:
        def decorator(func: Callable[..., Awaitable[Response]]) -> Callable[..., Awaitable[Response]]:
            self._exception_handlers[exc_type] = func
            return func

        return decorator

    # ASGI integration ---------------------------------------------------
    async def __call__(self, scope: Dict[str, Any], receive: Callable[[], Awaitable[Dict[str, Any]]], send: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        if scope.get("type") != "http":  # pragma: no cover - safety
            raise RuntimeError("Only HTTP scopes are supported")

        body = b""
        more = True
        while more:
            message = await receive()
            body += message.get("body", b"")
            more = message.get("more_body", False)

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        request = Request(scope.get("method", "GET"), scope.get("path", "/"), headers, body)

        route, path_params = self._match_route(request.method, request.url.path)
        if route is None:
            response = JSONResponse({"detail": "Not Found"}, status_code=status.HTTP_404_NOT_FOUND)
        else:
            response = await self._dispatch(request, route.endpoint, path_params)

        await send(
            {
                "type": "http.response.start",
                "status": response.status_code,
                "headers": [
                    (name.encode("latin-1"), value.encode("latin-1"))
                    for name, value in response.headers.items()
                ],
            }
        )
        await send({"type": "http.response.body", "body": response.body, "more_body": False})

    # Internal helpers ---------------------------------------------------
    def _match_route(self, method: str, path: str) -> Tuple[Optional[_Route], Dict[str, str]]:
        for route in self._routes:
            params = route.match(method, path)
            if params is not None:
                return route, params
        return None, {}

    async def _dispatch(self, request: Request, endpoint: Callable[..., Any], path_params: Dict[str, str]) -> Response:
        async def call_handler(req: Request) -> Response:
            return await self._call_endpoint(endpoint, req, path_params)

        handler = call_handler
        for middleware in reversed(self._http_middlewares):
            next_handler = handler

            async def wrapper(req: Request, _middleware=middleware, _next=next_handler) -> Response:
                return await _middleware(req, _next)

            handler = wrapper

        try:
            return await handler(request)
        except ValidationError as exc:
            handler_fn = self._exception_handlers.get(ValidationError)
            if handler_fn is None:
                raise
            return await handler_fn(request, exc)
        except RequestValidationError as exc:
            handler_fn = self._exception_handlers.get(RequestValidationError)
            if handler_fn is None:
                raise
            return await handler_fn(request, exc)

    async def _call_endpoint(self, endpoint: Callable[..., Any], request: Request, path_params: Dict[str, str]) -> Response:
        sig = inspect.signature(endpoint)
        bound: Dict[str, Any] = {}
        json_data: Any = _UNSET

        def ensure_json() -> Any:
            nonlocal json_data
            if json_data is _UNSET:
                json_data = request.json()
            return json_data

        for name, param in sig.parameters.items():
            annotation = param.annotation
            if annotation is Request:
                bound[name] = request
            elif name in path_params:
                raw_value = path_params[name]
                if annotation not in (inspect._empty, str):
                    try:
                        bound[name] = annotation(raw_value)
                        continue
                    except Exception:  # pragma: no cover - fallback to raw string
                        pass
                bound[name] = raw_value
            elif self._is_pydantic_model(annotation):
                try:
                    bound[name] = annotation(**ensure_json())
                except ValidationError:
                    raise
            else:
                data = ensure_json()
                bound[name] = data

        result = endpoint(**bound)
        if inspect.iscoroutine(result):
            result = await result
        if isinstance(result, Response):
            return result
        return JSONResponse(result)

    @staticmethod
    def _is_pydantic_model(annotation: Any) -> bool:
        return isinstance(annotation, type) and issubclass(annotation, BaseModel)


_UNSET = object()

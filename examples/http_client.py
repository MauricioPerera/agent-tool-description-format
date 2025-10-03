"""Lightweight HTTP helpers for ATDF examples.

These wrappers ensure every request includes a sane timeout so Bandit checks
recognize them as safe, while allowing callers to override the defaults when
needed.
"""

from __future__ import annotations

from typing import Any

import requests

_DEFAULT_TIMEOUT = (3.05, 15.0)


def _inject_timeout(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of *kwargs* that always defines ``timeout``."""
    if "timeout" not in kwargs:
        kwargs = {**kwargs, "timeout": _DEFAULT_TIMEOUT}
    return kwargs


def get(url: str, **kwargs: Any) -> requests.Response:
    """Perform a ``GET`` request with a default timeout."""
    return requests.get(url, **_inject_timeout(kwargs))


def post(url: str, **kwargs: Any) -> requests.Response:
    """Perform a ``POST`` request with a default timeout."""
    return requests.post(url, **_inject_timeout(kwargs))


def delete(url: str, **kwargs: Any) -> requests.Response:
    """Perform a ``DELETE`` request with a default timeout."""
    return requests.delete(url, **_inject_timeout(kwargs))


__all__ = ["get", "post", "delete"]

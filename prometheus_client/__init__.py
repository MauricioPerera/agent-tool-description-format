"""Minimal Prometheus client stubs for offline testing.

Only the features exercised by the test-suite are implemented: counters,
gauges, histograms, a ``generate_latest`` helper, and the content type
constant used by the metrics endpoint. Metrics are tracked in-memory without
exposure to the broader Prometheus text format, but the behaviour is
compatible with the expectations of the reference FastAPI implementation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"


@dataclass
class _MetricHandle:
    metric: "_Metric"
    label_key: Tuple[str, ...]

    def inc(self, amount: float = 1.0) -> None:
        self.metric._values[self.label_key] = self.metric._values.get(self.label_key, 0.0) + amount

    def observe(self, value: float) -> None:
        self.inc(value)


class _Metric:
    def __init__(self, name: str, documentation: str, labelnames: Iterable[str] = ()):  # pragma: no cover - trivial init
        self.name = name
        self.documentation = documentation
        self.labelnames = tuple(labelnames)
        self._values: Dict[Tuple[str, ...], float] = {}

    def labels(self, **labels: str) -> _MetricHandle:
        key = tuple(str(labels.get(label, "")) for label in self.labelnames)
        return _MetricHandle(self, key)

    def samples(self) -> Dict[str, float]:
        if not self.labelnames:
            return {self.name: self._values.get((), 0.0)}
        formatted: Dict[str, float] = {}
        for key, value in self._values.items():
            label_suffix = ",".join(f"{label}=\"{val}\"" for label, val in zip(self.labelnames, key))
            formatted[f"{self.name}{{{label_suffix}}}"] = value
        return formatted

    # Convenience helpers for unlabeled metrics
    def inc(self, amount: float = 1.0) -> None:
        self.labels().inc(amount)

    def dec(self, amount: float = 1.0) -> None:
        self.inc(-amount)

    def observe(self, value: float) -> None:
        self.inc(value)


def generate_latest() -> bytes:
    payload = {}
    for metric in _METRICS:
        payload.update(metric.samples())
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


_METRICS: Tuple[_Metric, ...] = ()


def _register(metric: _Metric) -> _Metric:
    global _METRICS
    _METRICS = (*_METRICS, metric)
    return metric


def Counter(name: str, documentation: str, labelnames: Iterable[str] = ()):  # type: ignore[override]
    metric = _Metric(name, documentation, labelnames)
    return _register(metric)


def Gauge(name: str, documentation: str, labelnames: Iterable[str] = ()):  # type: ignore[override]
    metric = _Metric(name, documentation, labelnames)
    return _register(metric)


def Histogram(name: str, documentation: str, labelnames: Iterable[str] = ()):  # type: ignore[override]
    metric = _Metric(name, documentation, labelnames)
    return _register(metric)


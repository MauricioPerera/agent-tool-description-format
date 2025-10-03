"""Performance test suite for selector latency/throughput.
Generated for BMAD workflow task T3 (Performance Testing).
"""

import time
import statistics
import requests

SELECTOR_URL = "http://127.0.0.1:8050/recommend"

PAYLOAD = {
    "query": "Necesito reservar un hotel en Madrid",
    "language": "es",
    "top_n": 1,
    "servers": ["http://127.0.0.1:8001/tools"],
    "allowed_tools": ["hotel_reservation"],
}


def measure_latency(samples: int = 10):
    durations = []
    for _ in range(samples):
        start = time.perf_counter()
        response = requests.post(SELECTOR_URL, json=PAYLOAD, timeout=5)
        response.raise_for_status()
        durations.append(time.perf_counter() - start)
    return durations


def main():
    durations = measure_latency()
    stats = {
        "samples": len(durations),
        "min_ms": round(min(durations) * 1000, 2),
        "max_ms": round(max(durations) * 1000, 2),
        "avg_ms": round(statistics.mean(durations) * 1000, 2),
        "p95_ms": round(statistics.quantiles(durations, n=20)[18] * 1000, 2),
    }
    print(stats)


if __name__ == "__main__":
    main()

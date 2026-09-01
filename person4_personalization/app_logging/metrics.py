import time
from collections import defaultdict
from typing import Any, Dict


class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.status_codes = defaultdict(int)
        self.endpoint_latencies = defaultdict(list)
        self.agent_runs = defaultdict(int)
        self.error_count = 0

    def record_request(self, endpoint: str, status_code: int, duration_ms: float):
        self.total_requests += 1
        self.status_codes[status_code] += 1
        self.endpoint_latencies[endpoint].append(duration_ms)
        # Keep maximum 500 samples per endpoint to prevent memory bloat
        if len(self.endpoint_latencies[endpoint]) > 500:
            self.endpoint_latencies[endpoint].pop(0)
        if status_code >= 400:
            self.error_count += 1

    def record_agent_run(self, agent_name: str):
        self.agent_runs[agent_name] += 1

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        uptime_seconds = round(time.time() - self.start_time, 2)
        latencies_summary = {}
        for endpoint, lats in self.endpoint_latencies.items():
            if lats:
                latencies_summary[endpoint] = {
                    "count": len(lats),
                    "avg_ms": round(sum(lats) / len(lats), 2),
                    "min_ms": round(min(lats), 2),
                    "max_ms": round(max(lats), 2),
                }

        return {
            "uptime_seconds": uptime_seconds,
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "status_codes": dict(self.status_codes),
            "agent_runs": dict(self.agent_runs),
            "endpoint_latencies": latencies_summary,
        }


metrics_collector = MetricsCollector()

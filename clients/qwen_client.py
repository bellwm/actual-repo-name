import os, requests, time, logging
from typing import Optional, Dict, Any

logger = logging.getLogger("clients.qwen")

class QwenClient:
    def __init__(self,
                 api_key: Optional[str]=None,
                 base_url: Optional[str]=None,
                 timeout: int=10,
                 max_retries: int=3,
                 metrics_hook=None):
        self.api_key = api_key or os.getenv("QWEN_API_KEY")
        self.base_url = base_url or os.getenv("QWEN_BASE_URL", "https://api.qwen.example")
        self.timeout = timeout
        self.max_retries = max_retries
        self.metrics_hook = metrics_hook

    def _record_metrics(self, **kwargs):
        if callable(self.metrics_hook):
            try:
                self.metrics_hook(kwargs)
            except Exception:
                logger.exception("metrics_hook failed")

    def _request(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}{path}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(self.max_retries):
            start = time.time()
            try:
                r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                latency = int((time.time() - start) * 1000)
                self._record_metrics(service="qwen", endpoint=path, latency_ms=latency, status=r.status_code)
                if 200 <= r.status_code < 300:
                    return {"ok": True, "status": r.status_code, "data": r.json(), "error": None, "latency_ms": latency}
                if 500 <= r.status_code < 600:
                    backoff = 2 ** attempt
                    logger.warning("qwen server error %s, retrying after %s s", r.status_code, backoff)
                    time.sleep(backoff)
                    continue
                return {"ok": False, "status": r.status_code, "data": None, "error": r.text, "latency_ms": latency}
            except requests.RequestException as e:
                latency = int((time.time() - start) * 1000)
                logger.warning("qwen request exception: %s", e)
                self._record_metrics(service="qwen", endpoint=path, latency_ms=latency, status=None, error=str(e))
                time.sleep(2 ** attempt)
        return {"ok": False, "status": None, "data": None, "error": "request_failed", "latency_ms": None}

    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        payload = {"prompt": prompt}
        payload.update(kwargs)
        return self._request("/v1/generate", payload)

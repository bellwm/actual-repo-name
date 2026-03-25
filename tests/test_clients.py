import json
import responses
from clients.qwen_client import QwenClient
from clients.deepseek_client import DeepseekClient
from clients.memory_client import MemoryClient

@responses.activate
def test_qwen_generate_success():
    responses.add(
        responses.POST,
        "http://localhost:5001/v1/generate",
        json={"id":"mock-qwen-1","ok":True,"result":"ok"},
        status=200
    )
    c = QwenClient(api_key="x", base_url="http://localhost:5001", max_retries=1)
    r = c.generate("hello")
    assert r["ok"] is True
    assert r["status"] == 200
    assert "result" in r["data"]

@responses.activate
def test_deepseek_search_success():
    responses.add(
        responses.GET,
        "http://localhost:5002/v1/search",
        json={"ok":True,"hits":[]},
        status=200
    )
    c = DeepseekClient(api_key="x", base_url="http://localhost:5002", max_retries=1)
    r = c.search("q")
    assert r["ok"] is True
    assert r["status"] == 200

@responses.activate
def test_memory_store_success():
    responses.add(
        responses.POST,
        "http://localhost:8000/v1/store",
        json={"ok":True,"stored_key":"k"},
        status=200
    )
    c = MemoryClient(base_url="http://localhost:8000", max_retries=1)
    r = c.store("k", {"a":1})
    assert r["ok"] is True
    assert r["data"]["stored_key"] == "k"

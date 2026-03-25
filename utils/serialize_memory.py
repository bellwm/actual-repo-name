from typing import Any, Dict

SENSITIVE_KEYS = {"ssn", "password", "credit_card", "token"}

def adapt_memory_for_report(mem: Dict[str, Any]) -> Dict[str, Any]:
    """
    将 memory 中的任意结构适配为报告可接受的稳定结构。
    - 扁平化常见字段
    - 移除敏感字段
    - 将复杂对象序列化为简单 dict/primitive
    """
    out: Dict[str, Any] = {}

    if not isinstance(mem, dict):
        return out

    # 常见扁平字段
    if "preferred_name" in mem:
        out["preferred_name"] = str(mem.get("preferred_name"))

    # preferences 保留为 dict（但只保留简单键值）
    prefs = mem.get("preferences")
    if isinstance(prefs, dict):
        out["preferences"] = {k: v for k, v in prefs.items() if k not in SENSITIVE_KEYS}

    # 其他非敏感键，按需保留但限制深度为一层
    for k, v in mem.items():
        if k in {"preferred_name", "preferences"}:
            continue
        if k in SENSITIVE_KEYS:
            continue
        if isinstance(v, (str, int, float, bool, type(None))):
            out[k] = v
        elif isinstance(v, dict):
            out[k] = {kk: vv for kk, vv in v.items() if kk not in SENSITIVE_KEYS and isinstance(vv, (str, int, float, bool, type(None)))}
        else:
            out[k] = str(v)
    return out

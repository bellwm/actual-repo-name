#!/usr/bin/env python3
import sys, json, os
from jsonschema import Draft7Validator

def infer_type(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"

def infer_schema_from_instance(instance):
    if isinstance(instance, dict):
        props = {}
        required = []
        for k, v in instance.items():
            props[k] = infer_schema_from_instance(v)
            required.append(k)
        return {"type":"object", "properties": props, "required": required, "additionalProperties": True}
    if isinstance(instance, list):
        if not instance:
            return {"type":"array", "items": {}}
        item_schemas = [infer_schema_from_instance(i) for i in instance]
        return {"type":"array", "items": item_schemas[0]}
    t = infer_type(instance)
    return {"type": t}

def generate_schema_from_samples(paths, out_path="schema_generated.json"):
    samples = []
    for p in paths:
        if os.path.isdir(p):
            for fn in os.listdir(p):
                if fn.endswith(".json"):
                    with open(os.path.join(p, fn), "r", encoding="utf-8") as f:
                        samples.append(json.load(f))
        else:
            with open(p, "r", encoding="utf-8") as f:
                samples.append(json.load(f))
    if not samples:
        print("No JSON samples found to generate schema.")
        return None
    schema = infer_schema_from_instance(samples[0])
    schema["additionalProperties"] = True
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
    print(f"Generated schema written to {out_path}")
    return out_path

FALLBACK_SCHEMA = {
  "type": "object",
  "required": ["id", "symbol", "analysis", "timestamp"],
  "properties": {
    "id": {"type": "string"},
    "symbol": {"type": "string"},
    "analysis": {"type": "object"},
    "timestamp": {"type": "string"}
  },
  "additionalProperties": True
}

def load_schema(schema_path=None, strict=False):
    if strict and schema_path and os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    if os.path.exists("schema_generated.json"):
        with open("schema_generated.json", "r", encoding="utf-8") as f:
            s = json.load(f)
            if strict:
                # in strict mode, remove additionalProperties at top-level if present
                s.pop("additionalProperties", None)
            return s
    return FALLBACK_SCHEMA

def validate_file(path, schema):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        print(f"[FAIL] {path}")
        for e in errors:
            loc = ".".join([str(x) for x in e.path]) or "<root>"
            print(f" - {loc}: {e.message}")
        return False
    print(f"[OK] {path}")
    return True

def main(argv):
    if len(argv) < 2:
        print("Usage:")
        print("  python validate_output.py <file-or-dir> [...]")
        print("  python validate_output.py --generate-from <sample.json|dir>")
        print("  python validate_output.py --strict <file-or-dir> [...]  # strict mode")
        sys.exit(1)
    if argv[1] == "--generate-from":
        if len(argv) < 3:
            print("Provide sample file or directory to generate schema from.")
            sys.exit(1)
        generate_schema_from_samples([argv[2]])
        sys.exit(0)
    strict = False
    if argv[1] == "--strict":
        strict = True
        argv = [argv[0]] + argv[2:]
        if len(argv) < 2:
            print("Provide files or dirs to validate in strict mode.")
            sys.exit(1)
    schema = load_schema(None, strict=strict)
    ok = True
    for p in argv[1:]:
        if os.path.isdir(p):
            for fn in os.listdir(p):
                if fn.endswith(".json"):
                    ok = validate_file(os.path.join(p, fn), schema) and ok
        else:
            ok = validate_file(p, schema) and ok
    if not ok:
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv)

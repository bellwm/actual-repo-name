#!/usr/bin/env python3
import json, sys, os
from datetime import datetime
from pathlib import Path

def ensure_meta(report, outpath):
    report.setdefault("file_id", report.get("file_id") or report.get("id") or os.path.splitext(os.path.basename(outpath))[0])
    report.setdefault("generated_at", datetime.utcnow().isoformat() + "Z")
    report.setdefault("source", report.get("source") or report.get("metadata", {}).get("source", "qwen_pipeline_v1"))
    report.setdefault("version", report.get("version") or report.get("metadata", {}).get("version", "v0.1"))
    return report

def process_file(path, outpath=None, in_place=False):
    p = Path(path)
    if not p.exists():
        print(f"SKIP: {path} (not found)")
        return False
    outpath = outpath or (path if in_place else str(p.with_suffix('.meta.json')))
    with p.open('r', encoding='utf-8') as f:
        report = json.load(f)
    report = ensure_meta(report, outpath)
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"WROTE: {outpath}")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: ensure_meta.py <report.json> [<report2.json> ...]  (use --in-place to overwrite)")
        sys.exit(1)
    args = sys.argv[1:]
    in_place = False
    if "--in-place" in args:
        in_place = True
        args.remove("--in-place")
    for p in args:
        process_file(p, in_place=in_place)

if __name__ == '__main__':
    main()

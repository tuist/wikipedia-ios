#!/usr/bin/env python3
"""Turn Once build and test logs into a job summary and a JSON record."""

import argparse
import collections
import json
import re
from pathlib import Path

ACTION = re.compile(r"^\s+[✓✗]\s+(\S+)\s+(\S+)\s+(\S+)\s*$")


def duration_seconds(value):
    match = re.fullmatch(r"([\d.]+)(ms|s|m)", value)
    if not match:
        return 0.0
    number, unit = float(match.group(1)), match.group(2)
    return {"ms": number / 1000, "s": number, "m": number * 60}[unit]


def parse(path):
    statuses = collections.Counter()
    seconds = collections.Counter()
    actions = []
    log = Path(path) if path else None
    if not log or not log.is_file():
        return {"statuses": {}, "action_seconds": {}, "slowest": [], "trailer": None}
    trailer = None
    for line in log.read_text(errors="replace").splitlines():
        match = ACTION.match(line)
        if match:
            name, status, duration = match.groups()
            statuses[status] += 1
            seconds[status] += duration_seconds(duration)
            actions.append((duration_seconds(duration), name, status))
        elif re.match(r"^\s+(Done|Failed)\s", line) or line.startswith("once: ran "):
            trailer = line.strip()
    actions.sort(reverse=True)
    return {
        "statuses": dict(statuses),
        "action_seconds": {k: round(v, 1) for k, v in seconds.items()},
        "slowest": [{"name": n, "status": s, "seconds": round(d, 1)} for d, n, s in actions[:10]],
        "trailer": trailer,
    }


def minutes(value):
    return f"{int(value) / 60:.1f} min" if value else "n/a"


def main():
    parser = argparse.ArgumentParser()
    for flag in ["os", "sha", "remote-cache", "graph-seconds", "build-seconds",
                 "test-seconds", "test-status", "build-log", "test-log", "json"]:
        parser.add_argument(f"--{flag}", default="")
    args = parser.parse_args()

    build, test = parse(args.build_log), parse(args.test_log)
    record = {
        "os": args.os,
        "sha": args.sha,
        "remote_cache": args.remote_cache == "true",
        "graph_seconds": int(args.graph_seconds or 0),
        "build_seconds": int(args.build_seconds or 0),
        "test_seconds": int(args.test_seconds or 0),
        "test_status": args.test_status,
        "build": build,
        "test": test,
    }
    if args.json:
        Path(args.json).write_text(json.dumps(record, indent=2))

    def counts(section):
        found = ", ".join(f"{v} {k}" for k, v in sorted(section["statuses"].items()))
        return found or section["trailer"] or "n/a"

    print(f"## Once on `{args.os}` for wikimedia/wikipedia-ios@{args.sha[:10]}\n")
    print(f"Remote cache: **{'on' if record['remote_cache'] else 'off (cold baseline)'}**\n")
    print("| Phase | Wall time | Actions |")
    print("| --- | --- | --- |")
    print(f"| Graph load | {minutes(args.graph_seconds)} | |")
    print(f"| `once build` | {minutes(args.build_seconds)} | {counts(build)} |")
    print(f"| `once test` | {minutes(args.test_seconds)} | {counts(test)} |")
    if args.test_status not in ("", "0"):
        print(f"\n`once test` exited with status {args.test_status}.")
    for title, section in [("build", build), ("test", test)]:
        if section["slowest"]:
            print(f"\n<details><summary>Slowest {title} actions</summary>\n")
            print("| Action | Status | Seconds |\n| --- | --- | --- |")
            for item in section["slowest"]:
                print(f"| `{item['name']}` | {item['status']} | {item['seconds']} |")
            print("\n</details>")


if __name__ == "__main__":
    main()

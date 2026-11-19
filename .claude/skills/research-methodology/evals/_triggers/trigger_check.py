"""Check which skills a real `claude -p` session in this repo loads for each query.

Windows-safe (threads, no select). Runs in the repo root so CLAUDE.md and the
installed skills are the real ones. A query passes when the expected skill is
(or, for should_trigger=false, is not) loaded before the session ends or times out.

usage: uv run python -X utf8 trigger_check.py <eval_set.json> <out.json> [timeout_s] [workers]
"""
import json, os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

REPO = str(__import__("pathlib").Path(__file__).resolve().parents[5])  # repo root


def run(item, timeout):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    cmd = ["claude", "-p", item["query"], "--output-format", "stream-json", "--verbose",
           "--include-partial-messages", "--disallowedTools", "Bash,PowerShell,Write,Edit,Agent,mcp__multiomics-kg"]
    p = subprocess.Popen(cmd, cwd=REPO, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, shell=(os.name == "nt"))
    skills, tools, done = [], [], threading.Event()

    def reader():
        for raw in p.stdout:
            try:
                ev = json.loads(raw.decode("utf-8", "replace"))
            except json.JSONDecodeError:
                continue
            if ev.get("type") != "assistant":
                continue
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") != "tool_use":
                    continue
                tools.append(block.get("name"))
                if block.get("name") == "Skill":
                    s = block.get("input", {}).get("skill", "")
                    skills.append(s)
                    if s.split(":")[-1] == item["skill"]:
                        done.set()
        done.set()

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    start = time.time()
    done.wait(timeout)
    if p.poll() is None:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
    hit = any(s.split(":")[-1] == item["skill"] for s in skills)
    return {**item, "triggered": hit, "passed": hit == item["should_trigger"],
            "skills_loaded": skills, "first_tools": tools[:6], "seconds": round(time.time() - start)}


def main():
    items = json.load(open(sys.argv[1], encoding="utf-8"))
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    with ThreadPoolExecutor(workers) as ex:
        results = list(ex.map(lambda it: run(it, timeout), items))
    json.dump(results, open(sys.argv[2], "w", encoding="utf-8"), indent=2)
    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        print(f"{mark}  [{r['skill']} expect={r['should_trigger']}] loaded={r['skills_loaded']}  :: {r['query'][:80]}")
    print(f"{sum(r['passed'] for r in results)}/{len(results)} passed")


if __name__ == "__main__":
    main()

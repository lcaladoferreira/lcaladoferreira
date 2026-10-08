"""Offline reliability lab. Python 3.11+. Synthetic actions only."""
import argparse
import hashlib
import json
import sqlite3
import tempfile
import time
from pathlib import Path

class ContractError(ValueError):
    pass

class ConflictError(ValueError):
    pass

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def validate_task(task):
    if not isinstance(task, dict) or set(task) != {"task_id", "tenant", "customer", "amount_cents"}:
        raise ContractError("task fields")
    for field in ("task_id", "tenant", "customer"):
        if not isinstance(task[field], str) or not task[field].strip() or len(task[field]) > 80:
            raise ContractError(field)
    if type(task["amount_cents"]) is not int or not 0 < task["amount_cents"] <= 5000:
        raise ContractError("amount_cents must be an integer from 1 to 5000")

def validate_proposal(proposal, task):
    validate_task(task)
    if not isinstance(proposal, dict) or set(proposal) != {"tool", "arguments"}:
        raise ContractError("proposal fields")
    if proposal["tool"] != "issue_credit":
        raise ContractError("tool not allowed")
    expected = {k: task[k] for k in ("tenant", "customer", "amount_cents")}
    if not isinstance(proposal["arguments"], dict) or canonical(proposal["arguments"]) != canonical(expected):
        raise ContractError("proposal does not match authorized task")
    return expected

class Ledger:
    """Synthetic effect and idempotency record share one local transaction."""
    def __init__(self, path):
        self.db = sqlite3.connect(str(path), timeout=10, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS actions(
          action_key TEXT PRIMARY KEY, payload TEXT NOT NULL, receipt TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS credits(
          action_key TEXT PRIMARY KEY, tenant TEXT NOT NULL,
          customer TEXT NOT NULL, amount_cents INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS events(
          seq INTEGER PRIMARY KEY AUTOINCREMENT,
          task_id TEXT NOT NULL, stage TEXT NOT NULL, outcome TEXT NOT NULL);
        """)

    def close(self):
        self.db.close()

    def event(self, task_id, stage, outcome):
        self.db.execute("INSERT INTO events(task_id,stage,outcome) VALUES(?,?,?)",
                        (task_id, stage, outcome))

    def apply(self, key, payload, fail_after_commit=False):
        encoded = canonical(payload)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self.db.execute(
                "SELECT payload,receipt FROM actions WHERE action_key=?", (key,)).fetchone()
            if existing:
                if existing[0] != encoded:
                    raise ConflictError("idempotency key reused with different payload")
                receipt = json.loads(existing[1])
            else:
                receipt = {"receipt_id": hashlib.sha256(key.encode()).hexdigest()[:16],
                           "status": "applied", "amount_cents": payload["amount_cents"]}
                self.db.execute("INSERT INTO credits VALUES(?,?,?,?)",
                                (key, payload["tenant"], payload["customer"], payload["amount_cents"]))
                self.db.execute("INSERT INTO actions VALUES(?,?,?)",
                                (key, encoded, canonical(receipt)))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        if fail_after_commit:
            raise TimeoutError("synthetic response lost after commit")
        return receipt

    def count(self):
        return self.db.execute("SELECT COUNT(*) FROM credits").fetchone()[0]

    def total(self):
        return self.db.execute("SELECT COALESCE(SUM(amount_cents),0) FROM credits").fetchone()[0]

    def trace(self, task_id):
        return self.db.execute(
            "SELECT stage,outcome FROM events WHERE task_id=? ORDER BY seq", (task_id,)).fetchall()

def scripted_proposal(task):
    """Deterministic fixture, not an LLM."""
    return {"tool": "issue_credit",
            "arguments": {k: task[k] for k in ("tenant", "customer", "amount_cents")}}

def run_task(ledger, task, proposal=None, fail_first=False, max_attempts=2,
             deadline_seconds=5, clock=time.monotonic, after_effect=None):
    validate_task(task)
    if type(max_attempts) is not int or not 1 <= max_attempts <= 5:
        raise ContractError("max_attempts")
    if type(deadline_seconds) not in (int, float) or not 0 < deadline_seconds <= 60:
        raise ContractError("deadline_seconds")
    payload = validate_proposal(scripted_proposal(task) if proposal is None else proposal, task)
    key = canonical([task["tenant"], task["task_id"], "issue_credit:v1"])
    started = clock()
    for attempt in range(1, max_attempts + 1):
        if clock() - started >= deadline_seconds:
            ledger.event(task["task_id"], "deadline", "exhausted")
            raise TimeoutError("task budget exhausted")
        ledger.event(task["task_id"], "attempt", str(attempt))
        try:
            receipt = ledger.apply(key, payload, fail_after_commit=fail_first and attempt == 1)
        except TimeoutError:
            ledger.event(task["task_id"], "tool", "response_lost")
            if attempt == max_attempts:
                raise
            continue
        if after_effect is not None:
            after_effect()
        ledger.event(task["task_id"], "complete", receipt["receipt_id"])
        return receipt
    raise AssertionError("unreachable")

def broken_retry(amount_cents=1000):
    effects = []
    for attempt in range(2):
        effects.append(amount_cents)
        try:
            if attempt == 0:
                raise TimeoutError("response lost")
            return {"effects": len(effects), "total_cents": sum(effects)}
        except TimeoutError:
            continue

def demo():
    task = {"task_id": "credit-001", "tenant": "demo", "customer": "synthetic-001", "amount_cents": 1000}
    with tempfile.TemporaryDirectory() as tmp:
        ledger = Ledger(Path(tmp) / "ledger.db")
        try:
            receipt = run_task(ledger, task, fail_first=True)
            return {"scenario": "timeout_after_commit", "broken": broken_retry(),
                    "fixed": {"effects": ledger.count(), "total_cents": ledger.total(),
                              "receipt": receipt, "trace": ledger.trace(task["task_id"])},
                    "model": "scripted_fixture", "api_cost_usd": 0,
                    "scope": "local atomic transaction; no remote exactly-once guarantee"}
        finally:
            ledger.close()

def evaluate():
    task = {"task_id": "eval-001", "tenant": "demo", "customer": "synthetic-001", "amount_cents": 1000}
    cases = [
        ("valid", scripted_proposal(task), True),
        ("unknown_tool", {"tool": "delete_customer", "arguments": {}}, False),
        ("wrong_customer", {"tool": "issue_credit", "arguments": {
            "tenant": "demo", "customer": "other", "amount_cents": 1000}}, False),
        ("wrong_tenant", {"tool": "issue_credit", "arguments": {
            "tenant": "other", "customer": "synthetic-001", "amount_cents": 1000}}, False),
        ("inflated_amount", {"tool": "issue_credit", "arguments": {
            "tenant": "demo", "customer": "synthetic-001", "amount_cents": 5000}}, False),
        ("extra_argument", {"tool": "issue_credit", "arguments": {
            "tenant": "demo", "customer": "synthetic-001", "amount_cents": 1000,
            "approval": True}}, False),
    ]
    results = []
    for name, proposal, expected_accept in cases:
        try:
            validate_proposal(proposal, task)
            accepted = True
        except ContractError:
            accepted = False
        results.append({"case": name, "accepted": accepted,
                        "expected_accept": expected_accept, "pass": accepted == expected_accept})
    return {"dataset": "synthetic_contract_v1", "cases": results,
            "passed": sum(r["pass"] for r in results), "total": len(results),
            "limitation": "deterministic contracts; not live-model task success"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["demo", "evaluate"])
    args = parser.parse_args()
    report = demo() if args.command == "demo" else evaluate()
    print(json.dumps(report, indent=2))
    if args.command == "evaluate" and report["passed"] != report["total"]:
        raise SystemExit(1)

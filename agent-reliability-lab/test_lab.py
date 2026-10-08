import concurrent.futures
import tempfile
import unittest
from pathlib import Path
from lab import (Ledger, run_task, scripted_proposal, validate_task,
                 validate_proposal, ContractError, ConflictError, demo, evaluate)

class ReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "ledger.db"
        self.ledger = Ledger(self.path)
        self.task = {"task_id": "t1", "tenant": "a", "customer": "c1", "amount_cents": 1000}

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def test_normal_effect(self):
        self.assertEqual(run_task(self.ledger, self.task)["status"], "applied")
        self.assertEqual(self.ledger.total(), 1000)

    def test_timeout_after_commit(self):
        run_task(self.ledger, self.task, fail_first=True)
        self.assertEqual(self.ledger.count(), 1)
        self.assertEqual(self.ledger.total(), 1000)
        self.assertIn(("tool", "response_lost"), self.ledger.trace("t1"))

    def test_retry_exhaustion_preserves_effect(self):
        with self.assertRaises(TimeoutError):
            run_task(self.ledger, self.task, fail_first=True, max_attempts=1)
        self.assertEqual(self.ledger.count(), 1)

    def test_rerun_after_lost_response(self):
        with self.assertRaises(TimeoutError):
            run_task(self.ledger, self.task, fail_first=True, max_attempts=1)
        run_task(self.ledger, self.task)
        self.assertEqual(self.ledger.count(), 1)

    def test_crash_after_effect_then_resume(self):
        def crash():
            raise RuntimeError("worker stopped")
        with self.assertRaises(RuntimeError):
            run_task(self.ledger, self.task, after_effect=crash)
        self.ledger.close()
        self.ledger = Ledger(self.path)
        run_task(self.ledger, self.task)
        self.assertEqual(self.ledger.count(), 1)

    def test_changed_payload_rejected(self):
        run_task(self.ledger, self.task)
        with self.assertRaises(ConflictError):
            run_task(self.ledger, dict(self.task, amount_cents=2000))
        self.assertEqual(self.ledger.total(), 1000)

    def test_two_distinct_tasks(self):
        run_task(self.ledger, self.task)
        run_task(self.ledger, dict(self.task, task_id="t2"))
        self.assertEqual(self.ledger.count(), 2)

    def test_tenant_keys_distinct(self):
        run_task(self.ledger, self.task)
        run_task(self.ledger, dict(self.task, tenant="b"))
        self.assertEqual(self.ledger.count(), 2)

    def test_invalid_amounts(self):
        for value in (True, False, 0, -1, 5001, "1000", 1.5, None):
            with self.subTest(value=value), self.assertRaises(ContractError):
                validate_task(dict(self.task, amount_cents=value))

    def test_missing_extra_fields(self):
        with self.assertRaises(ContractError):
            validate_task({"task_id": "t1"})
        with self.assertRaises(ContractError):
            validate_task(dict(self.task, privileged=True))

    def test_unknown_tool(self):
        with self.assertRaises(ContractError):
            run_task(self.ledger, self.task, {"tool": "delete_all", "arguments": {}})
        self.assertEqual(self.ledger.count(), 0)

    def test_wrong_tenant_before_effect(self):
        proposal = scripted_proposal(self.task)
        proposal["arguments"]["tenant"] = "b"
        with self.assertRaises(ContractError):
            run_task(self.ledger, self.task, proposal)
        self.assertEqual(self.ledger.count(), 0)

    def test_wrong_customer(self):
        proposal = scripted_proposal(self.task)
        proposal["arguments"]["customer"] = "c2"
        with self.assertRaises(ContractError):
            validate_proposal(proposal, self.task)

    def test_extra_arguments(self):
        proposal = scripted_proposal(self.task)
        proposal["arguments"]["approval"] = True
        with self.assertRaises(ContractError):
            validate_proposal(proposal, self.task)

    def test_deadline_prevents_effect(self):
        ticks = iter([0.0, 6.0])
        with self.assertRaises(TimeoutError):
            run_task(self.ledger, self.task, clock=lambda: next(ticks))
        self.assertEqual(self.ledger.count(), 0)

    def test_invalid_retry_budget(self):
        for count in (0, 6, True):
            with self.assertRaises(ContractError):
                run_task(self.ledger, self.task, max_attempts=count)

    def test_concurrent_same_key(self):
        def worker(_):
            ledger = Ledger(self.path)
            try:
                return run_task(ledger, self.task)["receipt_id"]
            finally:
                ledger.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            receipts = list(pool.map(worker, range(8)))
        self.assertEqual(len(set(receipts)), 1)
        self.assertEqual(self.ledger.count(), 1)

    def test_demo_baseline(self):
        report = demo()
        self.assertEqual(report["broken"]["effects"], 2)
        self.assertEqual(report["fixed"]["effects"], 1)

    def test_eval(self):
        report = evaluate()
        self.assertEqual(report["passed"], report["total"])

    def test_trace_excludes_customer(self):
        run_task(self.ledger, self.task)
        self.assertNotIn("c1", str(self.ledger.trace("t1")))

if __name__ == "__main__":
    unittest.main()

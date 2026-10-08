# AI Agent Reliability Engineering — free incident lab

By Leandro Calado Ferreira. Companion for the forthcoming book:
**AI Agent Reliability Engineering: A Hands-On Python Guide to Testing, Evaluating, Debugging, and Recovering Production Agents**.

## Run

Python 3.11+ with SQLite support. No pip packages, accounts, API keys, cloud resources or model calls.

```sh
cd agent-reliability-lab
python -m unittest -v
python lab.py demo
python lab.py evaluate
```

The deliberately broken baseline duplicates a synthetic credit when the response is lost after the first effect.
The corrected runner uses a stable operation key, checks the authorized task and reuses the committed receipt.

Expected invariants: broken effects = 2; corrected effects = 1; corrected total = 1000 cents.
Expected evaluation: six contract fixtures pass. Actual execution is recorded in GitHub Actions.

## Covered failures

Timeout after commit; worker restart; duplicate delivery; concurrent calls; changed payload under an old key;
wrong tenant/customer; unapproved amount; unknown tool; extra arguments; deadline and retry exhaustion.

## Scope

This is a scripted fixture, not a language-model evaluation.
Atomicity covers the synthetic effect and receipt inside one SQLite database.
It does not guarantee exactly-once behavior across a remote API or two databases.
The deadline check cannot interrupt a blocking remote call.
Repeated completion events are possible; one domain effect is the invariant.

A production extension needs a separately evaluated model adapter plus provider idempotency and reconciliation.
Do not connect the synthetic lab directly to real credits.

## Book status

Manuscript in preparation. No purchase link until a published Amazon listing is verified.

## References

- https://docs.python.org/3/library/sqlite3.html
- https://www.sqlite.org/lang_transaction.html
- https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices

## License

Source and tests: MIT. Editorial text: copyright Leandro Calado Ferreira.

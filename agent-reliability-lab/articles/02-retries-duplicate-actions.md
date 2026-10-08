# Why Retries Create Duplicate Agent Actions

A timeout does not prove that an action failed.

Suppose a tool commits a ten-dollar credit and loses its response. The caller retries. If that retry has no stable operation identity, the tool may issue another credit.

The resulting transcript can look successful while the account state is wrong.

The free incident lab reproduces this exact failure using synthetic data:

```sh
python lab.py demo
```

The deliberately broken baseline applies two effects. The corrected runner identifies one authorized intention with a stable key. Its local ledger stores the effect and receipt in one SQLite transaction. A repeated delivery returns the existing receipt.

A different payload under the same key is rejected. Automatically assigning a new key would turn a conflicting retry into a potentially new action.

The boundary matters. This local transaction does not guarantee exactly-once behavior across a remote provider and another database. A remote integration needs provider-side idempotency, lookup or reconciliation when a write's outcome is uncertain.

Bound attempts and elapsed time too. A deadline check before a call cannot interrupt a blocked request; the transport needs a timeout consistent with the remaining budget.

This is a deterministic incident demonstration, not an improvement percentage measured on production traffic.

I am developing *AI Agent Reliability Engineering* around executable failures and verified corrections. The book is not yet released.

Free source and tests:
https://github.com/lcaladoferreira/lcaladoferreira/tree/main/agent-reliability-lab

# Recovering an Agent Worker After a Committed Action

A missing completion event is not proof that a tool produced no effect.

The worker may have changed persistent state and stopped before recording completion. Recovery that blindly repeats every unfinished step can duplicate the business action.

The free incident lab includes a restart test:

```sh
python -m unittest test_lab.ReliabilityTests.test_crash_after_effect_then_resume -v
```

It interrupts execution after the synthetic effect commits, closes the database connection, opens a new one and resumes the same task.

The resumed runner finds the existing operation receipt and does not create a second credit.

The receipt and effect share one local SQLite transaction. Completion events are separate and may repeat. Domain-effect deduplication and event deduplication are different properties.

For a multi-step system, give every authorized action a stable identity. If a model regenerates the plan after restart, do not assign fresh identities to already intended effects. That can bypass deduplication.

For a remote API, a local checkpoint may not settle whether the provider committed. Use a queryable provider operation and a reconciliation rule. If evidence is contradictory, preserve the uncertainty rather than reporting success.

This test covers persistence across reconnection and a simulated worker interruption. It does not validate a distributed workflow engine.

The lab accompanies my forthcoming *AI Agent Reliability Engineering*. The book is not yet published.

Free runnable project:
https://github.com/lcaladoferreira/lcaladoferreira/tree/main/agent-reliability-lab

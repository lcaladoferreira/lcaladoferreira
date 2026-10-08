# How to Test an AI Agent's Tool Calls

A well-formed tool call can still be unauthorized. A proposal to issue a credit may contain the right fields while naming the wrong customer.

The first useful test is therefore a boundary test: submit the wrong customer and assert that the executor rejects it before changing persistent state.

In this free Python lab, the trusted task specifies tenant, customer and amount. The proposal must match those facts exactly. Generated arguments cannot supply their own approval.

Run:

```sh
cd agent-reliability-lab
python -m unittest test_lab.ReliabilityTests.test_wrong_customer -v
python -m unittest test_lab.ReliabilityTests.test_wrong_tenant_before_effect -v
```

The second test also checks that the ledger contains zero effects. This is stronger than checking only for an exception: an executor that writes first and rejects afterward would be unsafe.

Add unknown tools, extra fields, invalid amount types and changed payloads under existing operation keys to the same suite. These tests can run without a model. They exercise the execution contract regardless of who proposed the action.

For model quality, use a separate task dataset and recorded model run. Passing a deterministic validator suite does not measure how often a model proposes the correct tool.

I built this original lab as the foundation for *AI Agent Reliability Engineering*. The working book is not yet available for purchase.

Run the free lab:
https://github.com/lcaladoferreira/lcaladoferreira/tree/main/agent-reliability-lab

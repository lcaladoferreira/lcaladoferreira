# A Python Evaluation Dataset for Agent Tool Contracts

“Six tests passed” is useful only when you know what the six cases measure.

This free lab includes a small contract dataset:
- one valid proposal;
- an unknown tool;
- a wrong customer;
- a wrong tenant;
- an inflated amount;
- an extra argument pretending to carry approval.

Run:

```sh
python lab.py evaluate
```

The output reports expected acceptance, actual acceptance and pass/fail for each case. Its score describes a validator against predetermined proposals.

There are no language-model calls in this evaluation. The result cannot establish real-model task success.

That distinction helps keep evaluations useful. A contract dataset asks whether the executor handles a proposal correctly. A model dataset asks which proposals the planner produces under defined tasks and context. A domain evaluator asks whether authorized effects actually occurred.

For a future model run, preserve task version, prompt version, model configuration, tool responses and domain results. Keep development cases separate from holdout cases, and do not rerun failures until you collect a flattering score.

Also avoid counting refusals as successes simply because they produced no effect. Report coverage and whole-task success with clear denominators.

I created the lab for the forthcoming *AI Agent Reliability Engineering*. Its code and deterministic checks are available now; the full book remains in preparation.

Source:
https://github.com/lcaladoferreira/lcaladoferreira/tree/main/agent-reliability-lab

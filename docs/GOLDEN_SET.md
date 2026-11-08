# Golden set

25 incidents used to evaluate retrieval and, later, the agent.

- `dev` (15): used while tuning retrieval and prompts.
- `test` (10): held out; reported once at the end of each evaluation round, never tuned against.
- `scripted` incidents are reproduced live with `demo_app/faults.sh`; `synthetic` ones cannot be produced by the demo shop and are evaluated on retrieval and reasoning only.
- `expected_docs` must be retrieved; `also_relevant` are acceptable extras; `distractors` are look-alikes that should not outrank the expected documents.
- One incident is unanswerable on purpose: the correct behaviour is to say the evidence is insufficient.

Each file is one incident in `evals/golden_set/G-xxx.json`. The schema is in `evals/golden.py`.

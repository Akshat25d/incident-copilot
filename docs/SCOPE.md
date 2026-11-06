   # Scope

   ## Problem
   When production breaks, on-call engineers spend a long time gathering logs, metrics, recent deploys and old runbooks by hand before they can even form a hypothesis.

   ## Users
   On-call engineers on a small team. A recruiter or interviewer is the second audience, using the demo.

   ## Core flow
   1. A fault breaks the demo shop and an alert fires.
   2. A supervisor agent sends specialist agents to read logs, metrics, recent deploys and runbooks.
   3. It writes a report with ranked causes, cited evidence and a proposed fix.
   4. A human approves or rejects the fix; nothing risky runs without approval.

   ## In scope
   Demo app with fault injection, hybrid RAG, five MCP servers, multi-agent supervisor, approval gate, prompt-injection defenses, evaluation harness, tracing, CI/CD, free deployment, docs and demo video.

   ## Out of scope
   Real PagerDuty or Datadog integrations, model fine-tuning, multi-tenant auth, a polished frontend, Kubernetes.

   ## Success criteria
   - A fault injected into the demo app produces a cited incident report and a gated action.
   - Quality is measured on a golden incident set, with real results reported as they are.
   - The system is deployed and the repo has CI, docs and a demo video.

   ## Constraints
   Built entirely with free tools. About 2 to 3 hours a day alongside exam preparation.

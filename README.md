# DAG Example

A small, standalone, runnable model of a **decorator-based DAG statistical
computation engine** — the pattern used in production stats pipelines to let
callers say "give me these outputs" without knowing (or caring) what
intermediate steps produce them.

> **This is a from-scratch recreation, not production code.** It reproduces
> an architectural pattern I built at my employer using entirely generic,
> fabricated data and logic — no proprietary code, business rules, or
> internal details are included. See
> [`dag_training_example/README.md`](dag_training_example/README.md) for
> the full write-up.

## The pattern, in one paragraph

Register small functions ("nodes") with decorators. The framework inspects
each function's parameter names to automatically figure out dependencies,
builds a dependency graph with `networkx`, figures out which nodes actually
need to run for the outputs you requested, executes them in topological
order, caches shared intermediate results until every consumer has used
them, and routes each result to the right exporter.

## Get started

Everything lives in [`dag_training_example/`](dag_training_example/):

```powershell
cd dag_training_example
pip install -r requirements.txt
python run_example.py
pytest -v
```

See that folder's README for the full architecture breakdown, project
layout, and training exercises.

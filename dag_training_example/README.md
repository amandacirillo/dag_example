# DAG Training Example

A small, standalone, runnable model of the **Directed Acyclic Graph (DAG)
analysis engine** pattern used in PARSTAT's `dag_utils` / `dag_main`. It is
built from scratch (no proprietary code) purely to teach the pattern:

> Register small functions ("nodes") with decorators. The framework inspects
> each function's parameter names to automatically figure out dependencies,
> builds a graph with `networkx`, figures out which nodes actually need to
> run for the stats you want, executes them in the right order, caches
> shared results, and routes each result to the right "exporter".

## Why This Pattern?

1. **Users pick outputs, not steps.** A stat selector just says "I want
   `mean`, `std`, `correlation`" - it doesn't need to know that both depend
   on a shared cleaned dataframe, or which importer loads the raw data.
2. **The runner figures out what to run.** Only ancestors of the requested
   stats execute - request just `univariate` stats and `bivariate.correlation`
   never runs.
3. **Shared work is computed once.** `common.clean_scores` is used by both
   `univariate` and `bivariate` but only computed a single time, then cached
   until every node that needs it has consumed it, then evicted.
4. **Exporters open/close themselves.** Once every stat feeding an exporter
   has run, that exporter is automatically closed and writes its CSV.

## Project Layout

```
dag_framework/        <- the reusable engine (framework code)
    dag_types.py       Node = (module, function_name) tuple, type aliases
    register_nodes.py  RegisterNodes class + register_importer/data/stat decorators
    make_dag.py        Inspects function signatures -> builds networkx DiGraph
    runner.py          Executes nodes in topological order, caches, drives exporters
    exporters.py       Exporter base classes (Print, AccumulateAndWriteCSV)
    dag_drawer.py       Writes a Graphviz .dot file of any DAG

analysis/              <- the example "business logic" (like dag_main/ in parstat)
    register_nodes.py  a single shared `registered` instance + decorator aliases
    make_dag.py         imports every analysis module (so decorators run) and builds the DAG
    common/
        importers.py   @register_importer raw_scores  <- reads the CSV (root node)
        data.py         @register_data clean_scores     <- shared by every package
    univariate/
        data.py         @register_data grouped_by_item
        stats.py        @register_stat(UnivariateExporter) nobs / mean / std
        exporters.py    UnivariateExporter -> UNIVARIATE_OUTPUT.csv
        stat_selector.py
    bivariate/
        stats.py        @register_stat(BivariateExporter) correlation
        exporters.py    BivariateExporter -> BIVARIATE_OUTPUT.csv
        stat_selector.py

data/sample_scores.csv  <- tiny sample dataset (8 students x 3 items)
run_example.py          <- CLI: build DAG, draw it, run requested stats
tests/test_dag.py       <- pytest proving the DAG/caching/exporter behavior
```

## Try It

```powershell
cd C:\PythonProjects\dag_training_example
pip install -r requirements.txt

# Run everything (univariate + bivariate), writes output/*.csv and *.dot files
python run_example.py

# Run only univariate stats - bivariate.correlation will not execute at all
python run_example.py --packages univariate

# Run the tests
pytest -v
```

After running, check:
* `output/UNIVARIATE_OUTPUT.csv`, `output/BIVARIATE_OUTPUT.csv` - the exported results.
* `output/full_dag.dot`, `output/requested_sub_dag.dot` - render with Graphviz
  (`dot -Tpng output/full_dag.dot -o full_dag.png`) or paste into
  https://dreampuf.github.io/GraphvizOnline/ to see the graph visually.

## Exercises (for training)

1. Add a new stat, e.g. `median`, to `analysis/univariate/stats.py`. Just
   write the function and decorate it - nothing else needs to change.
2. Add a brand-new package `analysis/summary/` with a stat that depends on
   both a `univariate` result and `common.clean_scores`, to see cross-package
   dependency resolution in action.
3. Break something on purpose: register two functions with the same name in
   the same module and see the `RuntimeError`. Or make `mean` depend on
   itself and see the cycle-detection error.
4. Delete the `import analysis.bivariate.stats` line from `analysis/make_dag.py`
   and notice `correlation` silently disappears from the DAG - this
   demonstrates why "unused" imports matter in the real project.

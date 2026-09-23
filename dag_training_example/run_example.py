"""
CLI entry point that ties everything together:

    1. Build the full DAG (importing all analysis packages).
    2. Ask each package's stat_selector which stats we want.
    3. Reduce the DAG to just those stats + their ancestors.
    4. Draw that sub-DAG to a .dot file.
    5. Run it - the runner resolves dependencies, caches shared nodes
       (like `clean_scores`), and lets each package's exporter write its own
       CSV once all its stats are done.

Usage:
    python run_example.py                     # runs univariate + bivariate
    python run_example.py --packages univariate
"""
import argparse

from analysis.make_dag import make_dag
from analysis.register_nodes import registered
from analysis.univariate.stat_selector import select_stats as select_univariate_stats
from analysis.bivariate.stat_selector import select_stats as select_bivariate_stats
from dag_framework.dag_drawer import write_dag_dot
from dag_framework.make_dag import make_ancestors_dag_for_nodes
from dag_framework.runner import run

SELECTORS = {
    "univariate": select_univariate_stats,
    "bivariate": select_bivariate_stats,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the training DAG example")
    parser.add_argument(
        "--packages", nargs="+", choices=list(SELECTORS), default=list(SELECTORS),
        help="Which analysis packages' stats to run"
    )
    parser.add_argument("--csv_path", default="data/sample_scores.csv")
    parser.add_argument("--output_dir", default="output")
    args = parser.parse_args()

    full_dag, config_params_by_node = make_dag()
    print(f"Full DAG has {full_dag.number_of_nodes()} nodes, {full_dag.number_of_edges()} edges.")
    write_dag_dot(full_dag, filename="output/full_dag")

    stats_to_run = set()
    for package in args.packages:
        stats_to_run |= SELECTORS[package]()
    print(f"Requested stats: {sorted(stats_to_run)}")

    sub_dag = make_ancestors_dag_for_nodes(full_dag, stats_to_run)
    write_dag_dot(sub_dag, filename="output/requested_sub_dag")
    print(f"Sub-DAG (only what needs to run) has {sub_dag.number_of_nodes()} nodes.")

    config = {"csv_path": args.csv_path, "output_dir": args.output_dir}
    results = run(dag=sub_dag, registered=registered, stats_to_run=stats_to_run, config=config)

    print("\n--- Results summary ---")
    for node, df in results.items():
        print(f"{node}: {len(df)} rows")


if __name__ == "__main__":
    main()

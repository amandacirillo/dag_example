"""
Basic tests proving the framework's key behaviors:
    * the DAG builds without cycles and wires up `common` dependencies
      automatically.
    * running just the univariate stats does not require bivariate's
      correlation node to run.
    * the exporter automatically writes a CSV once all of its stats finish.
"""
import os

import pandas as pd
import pytest

from analysis.make_dag import make_dag
from analysis.register_nodes import registered
from analysis.univariate.stat_selector import select_stats as select_univariate_stats
from analysis.bivariate.stat_selector import select_stats as select_bivariate_stats
from dag_framework.make_dag import make_ancestors_dag_for_nodes
from dag_framework.runner import run

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_scores.csv")


@pytest.fixture(scope="module")
def full_dag():
    dag, _ = make_dag()
    return dag


def test_dag_is_acyclic(full_dag):
    assert full_dag.number_of_nodes() > 0


def test_common_node_is_shared_dependency(full_dag):
    # Both univariate's grouped_by_item and bivariate's correlation should
    # depend (directly or indirectly) on common.clean_scores.
    assert full_dag.has_edge(("common", "clean_scores"), ("univariate", "grouped_by_item"))
    assert full_dag.has_edge(("common", "clean_scores"), ("bivariate", "correlation"))


def test_univariate_subdag_excludes_bivariate(full_dag, tmp_path):
    stats = select_univariate_stats()
    sub_dag = make_ancestors_dag_for_nodes(full_dag, stats)
    assert ("bivariate", "correlation") not in sub_dag.nodes

    config = {"csv_path": CSV_PATH, "output_dir": str(tmp_path)}
    results = run(dag=sub_dag, registered=registered, stats_to_run=stats, config=config)

    assert set(results.keys()) == stats
    output_csv = tmp_path / "UNIVARIATE_OUTPUT.csv"
    assert output_csv.exists()
    df = pd.read_csv(output_csv)
    assert set(df["stat_name"]) == {"nobs", "mean", "std"}


def test_bivariate_stats_run(full_dag, tmp_path):
    stats = select_bivariate_stats()
    sub_dag = make_ancestors_dag_for_nodes(full_dag, stats)

    config = {"csv_path": CSV_PATH, "output_dir": str(tmp_path)}
    results = run(dag=sub_dag, registered=registered, stats_to_run=stats, config=config)

    df = results[("bivariate", "correlation")]
    assert "item_a" in df.columns and "item_b" in df.columns
    assert (tmp_path / "BIVARIATE_OUTPUT.csv").exists()

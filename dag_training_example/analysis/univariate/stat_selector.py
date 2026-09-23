"""
Selects every stat node belonging to this package. This mirrors
``dag_main/univariate/stat_selector.py``.
"""
from analysis.register_nodes import registered
from dag_framework.dag_types import NodeSet


def select_stats() -> NodeSet:
    return {node for node in registered.stat_to_exporter_class if node[0] == "univariate"}

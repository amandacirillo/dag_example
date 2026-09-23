"""
Executes a sub-DAG in dependency order, caching each node's result only for
as long as another queued node still needs it, and managing exporter
open/close lifecycles.

This mirrors ``dag_utils/runner.py``'s core loop, simplified for training:
    * requirement 2 (figure out which nodes must run) -> handled by
      ``make_ancestors_dag_for_nodes`` before this runs.
    * requirement 3 (cache + evict) -> ``cache`` dict + ``remaining_children``.
    * requirement 4 (open/close exporters automatically) -> ``ExporterManager``.
"""
from __future__ import annotations

import logging
from typing import Any

import networkx as nx

from dag_framework.dag_types import Node
from dag_framework.register_nodes import RegisterNodes

logger = logging.getLogger("dag_framework")


class ExporterManager:
    """
    Tracks, for each exporter class, how many of its stat nodes still need to
    run. Once that count hits zero the exporter is closed automatically -
    callers never need to remember to close anything themselves.
    """

    def __init__(self, stat_to_exporter_class: dict[Node, type], stats_to_run: set[Node], config: dict) -> None:
        self.stat_to_exporter_class = stat_to_exporter_class
        self.config = config
        self.instances: dict[type, Any] = {}
        self.remaining_stats: dict[type, set[Node]] = {}

        for node in stats_to_run:
            exporter_class = stat_to_exporter_class.get(node)
            if exporter_class is None:
                continue
            self.remaining_stats.setdefault(exporter_class, set()).add(node)

    def _get_or_create(self, exporter_class: type) -> Any:
        if exporter_class not in self.instances:
            self.instances[exporter_class] = exporter_class(**self.config)
            logger.info("Opened exporter %s", exporter_class.__name__)
        return self.instances[exporter_class]

    def send_result(self, node: Node, result: Any) -> None:
        exporter_class = self.stat_to_exporter_class.get(node)
        if exporter_class is None:
            return
        exporter = self._get_or_create(exporter_class)
        exporter.add_data(node, result)

        self.remaining_stats[exporter_class].discard(node)
        if not self.remaining_stats[exporter_class]:
            exporter.close()
            logger.info("Closed exporter %s", exporter_class.__name__)

    def force_close_all(self) -> None:
        """Safety net in case some exporter never saw all its stats."""
        for exporter_class, remaining in self.remaining_stats.items():
            if remaining and exporter_class in self.instances:
                self.instances[exporter_class].close()


def run(
    dag: nx.DiGraph,
    registered: RegisterNodes,
    stats_to_run: set[Node],
    config: dict,
) -> dict[Node, Any]:
    """
    Runs every node in `dag` (already reduced to only the stats requested plus
    their ancestors) in topological order.

    Args:
        dag: sub-DAG to execute (see make_ancestors_dag_for_nodes)
        registered: the registry holding the actual functions + exporter map
        stats_to_run: the stat nodes the caller actually wants exported
        config: run-time parameters (e.g. dataframe, thresholds, job id...)
            looked up by parameter name for anything that isn't a DAG edge.

    Returns:
        A dict of every stat node's result (handy for tests/inspection).
    """
    order = list(nx.topological_sort(dag))

    # How many not-yet-run children does each node have? Once that hits zero
    # we can safely drop it from the cache.
    remaining_children = {node: dag.out_degree(node) for node in order}

    cache: dict[Node, Any] = {}
    stat_results: dict[Node, Any] = {}
    exporter_manager = ExporterManager(registered.stat_to_exporter_class, stats_to_run, config)

    for node in order:
        func = registered.name_to_func[node]
        kwargs = {}
        for param_name in func.__code__.co_varnames[: func.__code__.co_argcount]:
            dep_node = next((p for p in dag.predecessors(node) if p[1] == param_name), None)
            if dep_node is not None:
                kwargs[param_name] = cache[dep_node]
            elif param_name in config:
                kwargs[param_name] = config[param_name]
            else:
                raise RuntimeError(f"Could not resolve parameter '{param_name}' for node {node}")

        logger.info("Running %s", node)
        result = func(**kwargs)
        cache[node] = result

        if node in registered.stat_to_exporter_class:
            stat_results[node] = result
            exporter_manager.send_result(node, result)

        # Evict finished parents from the cache to bound memory use.
        for parent in dag.predecessors(node):
            remaining_children[parent] -= 1
            if remaining_children[parent] == 0:
                cache.pop(parent, None)

    exporter_manager.force_close_all()
    return stat_results

"""
Builds a networkx DAG from the registry by inspecting each function's
parameter list.

This mirrors ``dag_utils/make_dag.py``: for every registered node we look at
its parameter names and try to match each one to another registered node
(first in its own module, then in ``common``, then anywhere else if the name
is unique). Anything left over is assumed to be a config value supplied at
run time (e.g. a threshold, a job id, etc...), not a DAG dependency.
"""
from __future__ import annotations

import inspect
from typing import Callable

import networkx as nx

from dag_framework.dag_types import Node
from dag_framework.register_nodes import RegisterNodes, get_module


def get_func_params(func: Callable, node_names: set[Node]) -> tuple[set[Node], set[str]]:
    """
    Args:
        func: node function to inspect
        node_names: every node name known to the registry

    Returns:
        (dependencies, unknown_params) - dependencies are other DAG nodes
        this function needs; unknown_params are parameter names that must be
        resolved from the config dict at run time instead.
    """
    found: set[Node] = set()
    unknown: set[str] = set()
    func_module = get_module(func)

    for name in inspect.signature(func).parameters.keys():
        if (func_module, name) in node_names:
            found.add((func_module, name))
        elif func_module != "common" and ("common", name) in node_names:
            found.add(("common", name))
        else:
            others = [n for n in node_names if n[1] == name]
            if len(others) > 1:
                raise RuntimeError(f"Ambiguous parameter '{name}' required by {func.__name__}: matches {others}")
            elif len(others) == 1:
                found.add(others[0])
            else:
                unknown.add(name)

    return found, unknown


def make_dag(registered: RegisterNodes) -> tuple[nx.DiGraph, dict[Node, set[str]]]:
    """
    Builds the full DAG containing every registered node (regardless of
    whether it will actually be run this session - that decision happens
    later, based on which stats were requested).

    Returns:
        dag: the full networkx DiGraph
        config_params_by_node: parameter names each node needs from config
    """
    dag = nx.DiGraph()
    node_names = set(registered.name_to_func.keys())

    all_nodes: list[tuple[Node, str]] = (
        [(n, "importer") for n in registered.importer_functions]
        + [(n, "data") for n in registered.data_functions]
        + [(n, "stat") for n in registered.stat_to_exporter_class]
    )

    config_params_by_node: dict[Node, set[str]] = {}

    for node, node_type in all_nodes:
        func = registered.name_to_func[node]
        dag.add_node(node, node_type=node_type)
        dependencies, unknown_params = get_func_params(func, node_names)
        config_params_by_node[node] = unknown_params
        for dep in dependencies:
            dag.add_edge(dep, node)

    if not nx.is_directed_acyclic_graph(dag):
        cycle = nx.find_cycle(dag)
        raise RuntimeError(f"Graph is not a DAG. Cycle found: {cycle}")

    return dag, config_params_by_node


def make_ancestors_dag_for_nodes(full_dag: nx.DiGraph, nodes: set[Node]) -> nx.DiGraph:
    """Returns the sub-DAG containing `nodes` plus everything they depend on."""
    nodes_used: set[Node] = set(nodes)
    for node in nodes:
        nodes_used |= nx.ancestors(full_dag, node)
    return full_dag.subgraph(nodes_used).copy()

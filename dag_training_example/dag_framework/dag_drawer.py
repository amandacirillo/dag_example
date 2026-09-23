"""
Renders a DAG to a Graphviz .dot file (text format - no external Graphviz
binary required to *generate* the file, only to render it to an image).

Mirrors ``dag_utils/dag_drawers.py``, simplified.
"""
from __future__ import annotations

from pathlib import Path

import networkx as nx

from dag_framework.dag_types import Node

NODE_COLORS = {
    "importer": "lightgreen",
    "data": "lightblue",
    "stat": "khaki",
}


def prettify_name(module: str, name: str) -> str:
    return f"{module}\\n{name}"


def write_dag_dot(dag: nx.DiGraph, filename: str = "dag") -> Path:
    """
    Writes `filename.dot` to the current directory. Render it with Graphviz
    (if installed) via: ``dot -Tpng dag.dot -o dag.png``
    """
    lines = ["digraph DAG {", '    rankdir="LR";', "    node [style=filled];"]
    for node, data in dag.nodes(data=True):
        module, name = node
        color = NODE_COLORS.get(data.get("node_type", ""), "white")
        label = prettify_name(module, name)
        node_id = f'"{module}::{name}"'
        lines.append(f'    {node_id} [label="{label}", fillcolor="{color}"];')
    for parent, child in dag.edges():
        parent_id = f'"{parent[0]}::{parent[1]}"'
        child_id = f'"{child[0]}::{child[1]}"'
        lines.append(f"    {parent_id} -> {child_id};")
    lines.append("}")

    path = Path(f"{filename}.dot")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}. Render with: dot -Tpng {path} -o {filename}.png")
    return path

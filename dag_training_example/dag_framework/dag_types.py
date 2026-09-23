"""
Shared type aliases used throughout the framework.

This mirrors the real project's ``dag_utils/dag_types.py``: nodes are always
represented as a ``(module_name, function_name)`` tuple. That is what makes
node names unique enough to build a graph without every function needing a
globally unique name.
"""
from typing import Callable

# In networkx a "node" can be anything hashable. We always use a
# (module name, function name) tuple, e.g. ("univariate", "mean").
Node = tuple[str, str]

# A set of nodes that a user (or stat_selector) wants calculated/exported.
NodeSet = set[Node]

FuncParamsByNode = dict[Node, set[Node]]

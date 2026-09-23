"""
Node registration.

Every importer, data node and stat node is registered via a decorator. The
decorators run the moment the module they're defined in gets imported - that
is why ``analysis/make_dag.py`` has a block of "unused" imports: importing a
module is what triggers its ``@register_*`` decorators to run and add
themselves to the registry below.

This mirrors ``dag_utils/register_nodes.py`` in the real project.
"""
from __future__ import annotations

from typing import Callable, Optional

from dag_framework.dag_types import Node
from dag_framework.exporters import Exporter


def get_module(func: Callable) -> str:
    """
    Returns the package name a function lives in, e.g. a function defined in
    ``analysis.univariate.stats`` returns ``"univariate"``.

    This is how the framework avoids requiring every node function across the
    whole project to have a globally unique name - "mean" can exist in both
    "univariate" and some other package, and the DAG builder tells them apart
    by module.
    """
    return func.__module__.split(".")[-2]


class RegisterNodes:
    """One instance of this is created per "family" of analyses (see
    ``analysis/register_nodes.py``). All decorators are methods on this
    instance so that different sub-projects/tests can each have an isolated
    registry.
    """

    def __init__(self) -> None:
        self.name_to_func: dict[Node, Callable] = {}
        self.importer_functions: set[Node] = set()
        self.data_functions: set[Node] = set()
        self.stat_to_exporter_class: dict[Node, type] = {}

    def _add(self, func: Callable) -> Node:
        node: Node = (get_module(func), func.__name__)
        if node in self.name_to_func:
            raise RuntimeError(f"Node {node} is already registered.")
        self.name_to_func[node] = func
        return node

    def register_importer(self, func: Callable) -> Callable:
        """For nodes that load raw data (e.g. read a CSV/DB query)."""
        node = self._add(func)
        self.importer_functions.add(node)
        return func

    def register_data(self, func: Callable) -> Callable:
        """For shared intermediate dataframes with no exporter of their own."""
        node = self._add(func)
        self.data_functions.add(node)
        return func

    def register_stat(self, exporter_class: Optional[type] = None) -> Callable:
        """For final statistics. Usage: ``@register_stat(MyExporter)``."""

        def decorator(func: Callable) -> Callable:
            node = self._add(func)
            self.stat_to_exporter_class[node] = exporter_class
            return func

        return decorator

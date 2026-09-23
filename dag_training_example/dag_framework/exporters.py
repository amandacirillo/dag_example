"""
Base classes for exporters.

An Exporter is a class (not a function) because it needs to hold state while
it accumulates results from one or more stat nodes. The runner will:

    1. Instantiate the exporter the first time one of its stats is computed.
    2. Call ``add_data(node, result)`` every time one of its stats finishes.
    3. Call ``close()`` once every stat that feeds this exporter has run.
"""
from __future__ import annotations

from typing import Any, Optional, Protocol, runtime_checkable

import pandas as pd

from dag_framework.dag_types import Node


@runtime_checkable
class Exporter(Protocol):
    def add_data(self, node: Node, result: Any) -> None:
        ...

    def close(self) -> Any:
        ...


class PrintExporter:
    """Minimal exporter useful for debugging - just prints what it receives."""

    def __init__(self, **_config: Any) -> None:
        self.received: list[tuple[Node, Any]] = []

    def add_data(self, node: Node, result: Any) -> None:
        print(f"[PrintExporter] received {node} -> {result!r}")
        self.received.append((node, result))

    def close(self) -> list[tuple[Node, Any]]:
        print("[PrintExporter] closing")
        return self.received


class AccumulateAndWriteCSVExporter:
    """
    Collects one dataframe per stat node, concatenates them, and writes a
    single CSV when closed. This mirrors
    ``dag_utils/exporters.py::AccumulateAndWriteExporterBase`` in the real
    project, simplified for training purposes.
    """

    output_filename: str = "OUTPUT.csv"

    def __init__(self, output_dir: str = "output", **_config: Any) -> None:
        self.output_dir = output_dir
        self.results_by_node: dict[Node, pd.DataFrame] = {}

    def add_data(self, node: Node, result: pd.DataFrame) -> None:
        self.results_by_node[node] = result

    def concat_for_output(self) -> pd.DataFrame:
        return pd.concat(self.results_by_node.values(), ignore_index=True, sort=False)

    def close(self) -> Optional[pd.DataFrame]:
        import os

        df = self.concat_for_output()
        os.makedirs(self.output_dir, exist_ok=True)
        full_path = os.path.join(self.output_dir, self.output_filename)
        df.to_csv(full_path, index=False)
        print(f"[{self.__class__.__name__}] wrote {len(df)} rows -> {full_path}")
        return df

"""
Importer nodes: these are the "roots" of the DAG - the only nodes with no
DAG dependencies of their own (they read from config only, e.g. a file path).
"""
import pandas as pd

from analysis.register_nodes import register_importer


@register_importer
def raw_scores(csv_path: str) -> pd.DataFrame:
    """Loads the raw student test-score CSV. `csv_path` comes from config."""
    return pd.read_csv(csv_path)

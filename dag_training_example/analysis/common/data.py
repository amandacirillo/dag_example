"""
Shared "common" data nodes. Any package can depend on these by simply naming
the parameter after the node (e.g. a function anywhere with a `clean_scores`
parameter will automatically be wired up to this node), because the DAG
builder falls back to searching "common" when a name isn't found locally.
"""
import pandas as pd

from analysis.register_nodes import register_data


@register_data
def clean_scores(raw_scores: pd.DataFrame) -> pd.DataFrame:
    """Drops rows with missing scores - shared by univariate & bivariate."""
    return raw_scores.dropna(subset=["score"]).reset_index(drop=True)

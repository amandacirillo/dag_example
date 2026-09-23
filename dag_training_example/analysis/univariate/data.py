"""
Package-local data node. Notice it depends on `clean_scores`, which is
defined in `common`, not here - the DAG builder resolves that automatically.
"""
import pandas as pd

from analysis.register_nodes import register_data


@register_data
def grouped_by_item(clean_scores: pd.DataFrame) -> "pd.core.groupby.DataFrameGroupBy":
    return clean_scores.groupby("item")

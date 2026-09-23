"""
Bivariate stat: item-pair correlation matrix. Depends on the *same*
`clean_scores` common node used by univariate - the runner computes it once
and shares it, it does not recompute it per package.
"""
import pandas as pd

from analysis.register_nodes import register_stat
from analysis.bivariate.exporters import BivariateExporter


@register_stat(BivariateExporter)
def correlation(clean_scores: pd.DataFrame) -> pd.DataFrame:
    wide = clean_scores.pivot_table(index="student_id", columns="item", values="score")
    corr_matrix = wide.corr()
    corr_matrix.index.name = "item_a"
    corr = corr_matrix.reset_index().melt(id_vars="item_a", var_name="item_b", value_name="value")
    corr["stat_name"] = "correlation"
    return corr

"""
Univariate stat nodes: nobs, mean, std - one row per item. Each is decorated
with @register_stat(UnivariateExporter), meaning the runner will
automatically route its result to that exporter and close it once every
requested univariate stat has run.
"""
import pandas as pd

from analysis.register_nodes import register_stat
from analysis.univariate.exporters import UnivariateExporter


@register_stat(UnivariateExporter)
def nobs(grouped_by_item: "pd.core.groupby.DataFrameGroupBy") -> pd.DataFrame:
    result = grouped_by_item["score"].count().reset_index(name="value")
    result["stat_name"] = "nobs"
    return result


@register_stat(UnivariateExporter)
def mean(grouped_by_item: "pd.core.groupby.DataFrameGroupBy") -> pd.DataFrame:
    result = grouped_by_item["score"].mean().reset_index(name="value")
    result["stat_name"] = "mean"
    return result


@register_stat(UnivariateExporter)
def std(grouped_by_item: "pd.core.groupby.DataFrameGroupBy") -> pd.DataFrame:
    result = grouped_by_item["score"].std().reset_index(name="value")
    result["stat_name"] = "std"
    return result

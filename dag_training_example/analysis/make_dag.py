"""
Import every analysis module here so their @register_* decorators run and
populate the registry, then build the DAG.

If you add a new package (or a new file within a package), you MUST add an
import for it here, otherwise its nodes will silently not exist in the DAG.
This is the same "gotcha" called out in the real project's DAG README.
"""
from analysis.register_nodes import registered

# noinspection PyUnresolvedReferences
import analysis.common.importers  # noqa: F401
# noinspection PyUnresolvedReferences
import analysis.common.data  # noqa: F401
# noinspection PyUnresolvedReferences
import analysis.univariate.data  # noqa: F401
# noinspection PyUnresolvedReferences
import analysis.univariate.stats  # noqa: F401
# noinspection PyUnresolvedReferences
import analysis.bivariate.stats  # noqa: F401

from dag_framework.make_dag import make_dag as _make_dag


def make_dag():
    return _make_dag(registered)

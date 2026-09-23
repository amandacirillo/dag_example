"""
The single, shared registry for this example project. Every analysis package
imports `registered` (and the decorator shortcuts below) from here, exactly
like the real project's ``dag_main/register_nodes.py``.
"""
from dag_framework.register_nodes import RegisterNodes

registered = RegisterNodes()

register_importer = registered.register_importer
register_data = registered.register_data
register_stat = registered.register_stat

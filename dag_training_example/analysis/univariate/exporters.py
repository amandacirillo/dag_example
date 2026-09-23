from dag_framework.exporters import AccumulateAndWriteCSVExporter


class UnivariateExporter(AccumulateAndWriteCSVExporter):
    output_filename = "UNIVARIATE_OUTPUT.csv"

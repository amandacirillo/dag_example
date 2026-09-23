from dag_framework.exporters import AccumulateAndWriteCSVExporter


class BivariateExporter(AccumulateAndWriteCSVExporter):
    output_filename = "BIVARIATE_OUTPUT.csv"

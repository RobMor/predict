import csv
from io import StringIO
import flask

from predict.plugins import FormatPlugin


class CSV(FormatPlugin):
    id = "csv"
    description = "CSV"

    def __init__(self, rows):
        self.rows = rows

    def generate(self):
        file = StringIO()
        writer = csv.writer(file)

        writer.writerows(self.rows)

        output = flask.make_response(file.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"

        return output
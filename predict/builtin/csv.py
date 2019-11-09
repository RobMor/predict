from predict.plugins import FormatPlugin
import sqlalchemy
import predict.db
import predict.models

class CSV(FormatPlugin):
    id="csv"
    description="CSV"

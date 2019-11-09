from predict.plugins import FormatPlugin
import sqlalchemy
import predict.db
import predict.models
from flask import Response, request, Flask
import flask

class CSV(FormatPlugin):
    id="csv"
    description="CSV"

def createCSV(form):
	filt = form.get('filters')
	add = form.get('addData')
	conRes = form.get('strategy')
	username = form.get('username')
	if(filt == "current_user"):
		labels = (
			predict.db.Session.query(predict.models.Label)
			.filter_by(username=username)
			.all()
		) or []
		def generate():
			for l in labels:
				yield l.cve_id + "," + l.fix_hash + '\n'
		return Response(
			generate(), 
			mimetype='text/csv',
			headers={
						"Content-Disposition":
						"attachment;filename=labels.csv"
					}
		)
	else:
		labels = (
			predict.db.Session.query(predict.models.Label)
			.all()
		) or []
		def generate():
			for l in labels:
				yield l.cve_id + "," + l.fix_hash + '\n'
		return Response(
			generate(), 
			mimetype='text/csv', 
			headers={
					"Content-Disposition":
					"attachment;filename=labels.csv"
				}
		)
from abc import ABC
import entrypoints
import sys
from flask import Response, request, Flask
import flask
# Data Export Process
# 1. Select Data Filter (optional)
# 2. Select Additional Data (optional)
# 3. Select Conflict Resolution (optional)
# 4. Select Output Format (required)

def export(form):
	type = form.get('file-format')
	
	if(type == 'csv'):
		from predict.builtin.csv import createCSV
		return createCSV(form)
	else:
		return type
		
# TODO
class FilterPlugin(ABC):
    pass

# TODO 
class DataPlugin(ABC):
    pass

# TODO
class ConflictPlugin(ABC):
    pass

# TODO
class FormatPlugin(ABC):
    pass


def load_plugins():
    plugins = {}
    for entrypoint in entrypoints.get_group_named("predict.plugins").values():
        source = entrypoint.load()
        
        if issubclass(source, FilterPlugin):
            plugins["filter"] = plugins.get("filter", []) + [source]
        elif issubclass(source, DataPlugin):
            plugins["data"] = plugins.get("data", []) + [source]
        elif issubclass(source, ConflictPlugin):
            plugins["conflict"] = plugins.get("conflict", []) + [source]
        elif issubclass(source, FormatPlugin):
            plugins["format"] = plugins.get("format", []) + [source]

    return plugins

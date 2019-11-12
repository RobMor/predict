import abc
import entrypoints
import flask
import sqlalchemy
import predict.db
import predict.models

def LtoList(labels):
	llist = [[l.cve_id, l.username, l.repo_user, l.repo_name, l.fix_file, l.intro_file, l.fix_hash, l.intro_hash] for l in labels]
	return llist
	
class PluginBase(abc.ABC):
	@property
	@abc.abstractproperty
	def id(self):
		pass

	@property
	@abc.abstractproperty
	def description(self):
		pass


# TODO
class FilterPlugin(PluginBase, abc.ABC):
	@abc.abstractmethod
	def __init__(self, query):
		"""Defines the construction of this filter.

		Args:
			query: query object being used for export.
		"""
		pass
	
	@abc.abstractmethod
	def filterq(self):
		"""Defines the functionality associated with this filter.
		Handles construction of a flask response to be handed back to he user.
		"""
		pass


# TODO
class DataPlugin(PluginBase, abc.ABC):
	pass


# TODO
class ConflictPlugin(PluginBase, abc.ABC):
	pass


# TODO
class FormatPlugin(PluginBase, abc.ABC):
	@abc.abstractmethod
	def __init__(self, data):
		"""Defines the construction of this export format.

		Args:
			data (list of lists): The data to be exported. Each sub-list is a datapoint
		"""
		pass

	@abc.abstractmethod
	def generate(self):
		"""Defines the functionality associated with this file format.

		Handles construction of a flask response to be handed back to he user.
		"""
		pass


def load_plugins():
	plugins = {}
	for name, entrypoint in entrypoints.get_group_named("predict.plugins").items():
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


# Data Export Process
# 1. Select Data Filter (optional)
# 2. Select Additional Data (optional)
# 3. Select Conflict Resolution (optional)
# 4. Select Output Format (required)

def export(filter_, extra_data, strategy, file_format):
	q = predict.db.Session.query(predict.models.Label)
	
	if(filter_ != "none"):
		filter = entrypoints.get_single("predict.plugins", filter_).load()
		filter = filterq(something, q)
		q = filter.filter()
	file_format = entrypoints.get_single("predict.plugins", file_format).load()
	file_format = file_format(LtoList(q.all()) or [])

	return file_format.generate()

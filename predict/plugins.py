import abc
import entrypoints
import flask


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

        Handles construction of a flask response to be handed back tto he user.
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
    data = [["testing", "12"], ["34", "56"]]

    file_format = entrypoints.get_single("predict.plugins", file_format).load()
    file_format = file_format(data)

    return file_format.generate()

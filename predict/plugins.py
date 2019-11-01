from abc import ABC
import entrypoints


# Data Export Process
# 1. Select Data Filter (optional)
# 2. Select Additional Data (optional)
# 3. Select Conflict Resolution (optional)
# 4. Select Output Format (required)


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
        
        if isinstance(source, FilterPlugin):
            plugins["filter"] = plugins.get("filter", []) + [source]
        elif isinstance(source, DataPlugin):
            plugins["data"] = plugins.get("data", []) + [source]
        elif isinstance(source, ConflictPlugin):
            plugins["conflict"] = plugins.get("conflict", []) + [source]
        elif isinstance(source, FormatPlugin):
            plugins["format"] = plugins.get("format", []) + [source]

    return plugins

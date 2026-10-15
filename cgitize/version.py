from importlib import metadata

try:
    __version__ = metadata.version("cgitize")
except:
    __version__ = "unknown"

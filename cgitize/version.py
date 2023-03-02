try:
    import importlib.metadata as metadata
except ImportError:
    import importlib_metadata as metadata


try:
    __version__ = metadata.version('cgitize')
except Exception:
    __version__ = 'unknown'

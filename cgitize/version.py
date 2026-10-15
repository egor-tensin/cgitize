from importlib import metadata

try:
    __version__ = metadata.version("cgitize")
except:
    __version__ = "unknown"


def add_to_arg_parser(parser):
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

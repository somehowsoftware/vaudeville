from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("vaudeville-cue")
except PackageNotFoundError:
    __version__ = "0.0.0+source"

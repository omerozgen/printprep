"""PrintPrep — STL model analysis and slicer recommendation tool."""

__version__ = "0.1.0"


class PrintPrepError(Exception):
    """Raised for user-facing PrintPrep errors (bad input, unreadable mesh, etc.)."""

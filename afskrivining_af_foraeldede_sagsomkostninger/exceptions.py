"""Common exception for the framework"""
class BusinessError(Exception):
    """Raise this in the primary process when business rules need to abort a task."""
    pass  # pylint: disable=(unnecessary-pass)

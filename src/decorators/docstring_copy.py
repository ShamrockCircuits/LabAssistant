def copy_docstring(from_method):
    """
    Decorator to copy the docstring from one method to another.
    """
    def decorator(to_method):
        to_method.__doc__ = from_method.__doc__
        return to_method
    return decorator
"""
Define a decorator for class-level properties.

This behaves like @property, but works on the class instead of the instance.

This was a nice bit of ChatGPT's 4o model picking up my small work.
"""

class classproperty:  # pylint: disable=invalid-name,too-few-public-methods
    """Define a decorator that marks a function as a "class property"."""
    def __init__(self, func):
        """Initialize with the function being decorated."""
        self.func = func

    def __get__(self, instance, owner):
        """Implement the 'get' portion of a property."""
        return self.func(owner)

"""
Define a singleton metaclass.

Ripped right out of StackAbuse
https://stackabuse.com/creating-a-singleton-in-python/
"""
import threading


class SingletonMeta(type):
    """
    Force a class to follow the Singleton pattern: at most one instance of it is allowed.
    """

    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """
        Intercept the construction function for the class to get force one instance.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

if __name__ != '__main__':  # pragma: no cover
    class Singleton(metaclass=SingletonMeta):  # pylint: disable=too-few-public-methods
        """Define a test case for SingletonMeta."""
        ...
    s1 = Singleton()
    s2 = Singleton()
    assert s1 is s2, "The two singleton instances should be identical."

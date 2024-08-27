class JSONFileNotFoundError(FileNotFoundError):
    """JSON file not found."""
    pass

class JSONDecodeError(ValueError):
    """Error decoding JSON."""
    pass

class JSONWriteError(ValueError):
    """Error writing JSON."""
    pass


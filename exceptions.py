class customException(Exception):
    pass

class textAnnotations(customException):
    """Raised when the no text is detected in an image"""
    pass

class NoneType(customException):
    """Raised when the value is not assigned to the variable"""
    pass
class listindexoutofrange(customException):
    """Raised when the text is not detected properly"""
    pass

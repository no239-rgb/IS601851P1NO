#########################################
#       Exception Classes               #
#########################################

class CalculatorError(Exception):
    """
    Base exception class for calculator-related errors.

    Created with minimal class declaration, as opposed to standard class declaration with constructor.
    Inherits all properties from Python's built in Exception class
    """
    pass

class ValidationError(CalculatorError):
    """
    Raised upon input validation failure.

    Created with minimal class declaration. 
    Inherits all properties from CalculationError class
    """
    pass

class OperationError(CalculatorError):
    """
    Raised when a calculation operation fails. 

    Created with minimal class declaration. 
    Inherits all properties from CalculationError class
    """
    pass

class ConfigurationError(CalculatorError):
    """
    Raised when calculator configuration is invalid.

    Created with minimal class declaration. 
    Inherits all properties from CalculationError class
    """
    pass


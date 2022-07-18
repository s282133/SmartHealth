class Error(Exception):
    pass

class InvalidWeightException(Error):
    """Raised when weight is < 0 or > 100"""
    pass

class PatientNotFoundException(Error):
    """Raised when the patient is not found"""
    pass

class DoctorNotFoundException(Error):
    """Raised when the doctor is not found"""
    pass

class ServiceUnavailableException(Error):
    """Raised when a problem is encountered in the communication with a service"""
    pass

class InvalidPatientID(Error):
    """Raised when the chatID is invalid"""
    pass

class InvalidChatIdException(Error):
    """Raised when the ChatID is not found or invalid"""
    pass

class genericException(Error):
    """Raised when a generic error is encountered, no details provided"""
    pass
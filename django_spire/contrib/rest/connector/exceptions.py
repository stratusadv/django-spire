class RestConnectorException(Exception):
    pass

class RestConnectorTimeoutException(RestConnectorException):
    pass

class RestConnectorError(Exception):
    pass

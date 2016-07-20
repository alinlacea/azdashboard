import errno
import socket

from azure.common import AzureHttpError, AzureMissingResourceHttpError


class AzureException(Exception):

    """Customized exception for conectivity with Azure
    Args:
        exception: Exception object
    Fields:
        number: HTTP status code to output
        message: Exception message.
    """

    def __init__(self, exception):
        super(AzureException, self).__init__()
        self.retriable = False
        if type(exception) is AzureMissingResourceHttpError:
            self.number = 404
            self.message = "Azure error. Missing resource: {0}".format(
                repr(exception))
        elif type(exception) is AzureHttpError:
            self.number = 500
            self.message = "Azure error: {0}".format(repr(exception))
        elif type(exception) is socket.gaierror:
            self.number = 404
            self.message = "Connection error: {0}".format(exception[1])
            self.retriable = True
        elif type(exception) is socket.error:
            if exception[0] in [errno.ECONNREFUSED,
                                errno.ECONNRESET,
                                errno.ETIMEDOUT]:
                self.message = "Connection error: {0}".format(exception[1])
                self.retriable = True
                self.number = 504
        else:
            self.message = "Unknown error: {0}".format(exception)
            self.number = 500

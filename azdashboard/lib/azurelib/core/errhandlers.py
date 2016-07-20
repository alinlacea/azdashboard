from time import sleep

import wrapt

from azdashboard.lib.azurelib.core.errors import AzureException
# from utils.vt4log import getLog


def handle_error(error, suppress_list):
    """Creates a simpler error object"""

    # log = getLog("azurelib")
    error = AzureException(error)
    if error.number in suppress_list:
        # log.info("Error suppresed.", suppresed_error=error.number)
        return None
    # log.error(error.message, http_code=error.number, exc=error)
    return error


def azure_error(no_of_retries=10, retry_timing=60, suppress=[]):
    @wrapt.decorator
    def retry_error(wrapped, instance, args, kwargs):
        retriable = True
        retry_no = 0
        while retry_no < no_of_retries and retriable:
            try:
                return wrapped(*args, **kwargs)
            except Exception as err:
                exc = handle_error(err, suppress)
                if not exc:
                    return False
                if exc.retriable and retry_no < no_of_retries:
                    retriable = True
                    retry_no += 1
                    sleep(retry_timing)
                else:
                    raise exc
    return retry_error

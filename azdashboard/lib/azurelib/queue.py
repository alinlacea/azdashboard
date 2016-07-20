import base64
import binascii
import json
from sys import getsizeof
from time import sleep, time

from azdashboard.lib.azurelib.core.entity import AzEntity
from azdashboard.lib.azurelib.core.errhandlers import azure_error


class AzQueue(AzEntity):

    """Object representing a live Azure Queue"""

    def __init__(self, service, name):
        super(AzQueue, self).__init__(service, name)
        # last sync time, queue buffer
        self.ltime = time()
        self.buffer = []

    def flush(self):
        """Remember to flush on exit"""
        if self.buffer != []:
            self.push(json.dumps(self.buffer))
            self.buffer = []  # what if we reuse the object after flush?

    @azure_error()
    def exists(self):
        """Returns True if the queue exists on
        the connection's account."""

        if len(self._service.list_queues
               (prefix=self._name)) > 0:
            return True
        return False

    @azure_error()
    def create(self, fail_on_exist=False):
        """Create the queue on the connection's account"""

        self._service.create_queue(self._name, fail_on_exist=fail_on_exist)
        return True

    @azure_error()
    def delete(self, fail_not_exist=False):
        """Delete the queue from the account"""

        self._service.delete_queue(self._name, fail_not_exist=fail_not_exist)
        return True

    @azure_error()
    def size(self):
        """Returns the approximate number of messages from the queue"""

        return int(self._service
                       .get_queue_metadata(self._name)
                   ["x-ms-approximate-messages-count"])

    @azure_error()
    def get_messages(self, number=32, timeout=None, is_base64=True,
                     blocking=True, maxTime=60 * 2, exit_handler=None):
        """Gets the given number of messages from the queue.
        Args:
            number: (optional) no of messages to dequeue
            timeout: (optional) dequeue expiration. In seconds.
            is_base64: (optional) - boolean -
                    True if queue uses base64 encoding
            blocking: (optional) - boolean -
                    True if must wait untill messages are available
            exit_handler: (optional) - callable
                    A callable returning False when you desire to
                    stop the listening loop if blocking
            maxTime: (optional) - upper limit for retry intervals
                    when checking for messages
        Returns:
            list of dictionary items, containing both data & metadata.
            See library's README for content.
        """
        messages = []
        retry_no = 0
        if exit_handler is None:
            exit_handler = self.default_loop_handler
        while not messages and exit_handler():
            messages = self._service \
                .get_messages(self._name, number, visibilitytimeout=timeout)
            if not blocking:
                break
            if not messages:
                retry_no += 1
                sleep(self.get_next_time(retry_no, maxTime))
        dicts = [message.__dict__ for message in messages]
        if is_base64:
            try:
                for msg in dicts:
                    msg["message_text"] =\
                        base64.b64decode(msg["message_text"])
            except binascii.Error:
                raise
        return dicts

    def pop_packed_messages(self, number=32,
                            maxTime=2*60,
                            exit_handler=None,):
        """Will get a message which contains more messages.
           Returns a python list which contains dicts.
        """
        messages = self.pop_messages(
            number, maxTime=maxTime, exit_handler=exit_handler)
        mlist = []
        for msg in messages:
            mlist.extend(json.loads(msg["message_text"]))
        return mlist

    def pop_messages(self, number=32, is_base64=True,
                     blocking=True, maxTime=60 * 2, exit_handler=None):
        """
        Pops the given number of messages from the queue
        (deletes them on the spot).
        """

        messages = self.get_messages(number=number, is_base64=is_base64,
                                     blocking=blocking,
                                     exit_handler=exit_handler,
                                     maxTime=maxTime)
        for msg in messages:
            self.delete_message(msg)
        return messages

    @azure_error()
    def peek_messages(self, number=32, is_base64=True):
        """Peeks a number of messages from queue's head."""

        messages = self._service \
            .peek_messages(self._name, numofmessages=number)
        dicts = [message.__dict__ for message in messages]
        if is_base64:
            try:
                for msg in dicts:
                    msg["message_text"] =\
                        base64.b64decode(msg["message_text"])
            except binascii.Error:
                raise
        return dicts

    def push_packed(self, msg):
        """Pushes a message to the queue, but will attempt to delay,
        packing it with others messages if possible

        :param msg: message to push
        :type msg: dict
        :rtype: None
        """
        now = time()
        # More than 6 seconds since the last push?
        try:
            json.dumps([msg])
        except Exception:
            raise
        if now - self.ltime >= 10.0:
            # We try to push the buffer as it is, if we have anything there
            if self.buffer != []:
                self.push(json.dumps(self.buffer))
                self.buffer = []
            # We also push the current message
            self.ltime = time()
            self.push(json.dumps([msg]))
        else:
            # We add the current message to the buffer
            self.buffer.append(msg)
            # If it is starting to get big, we push it
            if getsizeof(json.dumps(self.buffer)) > 40000:
                self.ltime = time()
                self.push(json.dumps(self.buffer))
                self.buffer = []

    @azure_error()
    def push(self, msg, is_base64=True):
        """Posts a message to the queue.
        Args:
            msg: JSON format containing message's data
        Returns:
            list of dictionary items, containing both data & metadata.
            See library's README for content.
        """
        if is_base64:
            msg = base64.b64encode(msg)
        self._service.put_message(self._name, msg)
        return True

    @azure_error()
    def purge(self):
        """Removes all messages from the queue"""

        self._service.clear_messages(self._name)
        return True

    @azure_error()
    def delete_message(self, msg):
        """Delete a given message from the queue
        Args:
            msg: dict object - message to be deleted.
                Requires to have 'message_id' & 'pop_receipt' keys
        """

        self._service.delete_message(self._name,
                                     msg["message_id"],
                                     msg["pop_receipt"])

        return True

    @azure_error()
    def list_queues(self):
        """List all queues from the account"""

        queues = self._service.list_queues()
        dicts = [queue.__dict__ for queue in queues]
        return dicts

    def get_next_time(self, retry_no, max_time):
        exp_factor = 2
        return min(exp_factor ** retry_no, max_time)

    def default_loop_handler(self):
        return True

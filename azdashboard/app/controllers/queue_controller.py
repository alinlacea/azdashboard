from azdashboard.app.controllers.application_controller import (
    ApplicationController
)
from azdashboard.config import environment
from azdashboard.lib.azurelib.core.connection import AzConnection
from azdashboard.lib.azurelib.queue import AzQueue

import json

class QueueController(ApplicationController):
    """Class for handling index page."""

    def all(self):
        """Render index page."""
        connection = environment.az_connection
        queue = connection.queue()
        data = queue.list_queues()
        return json.dumps(data)

    def get_queue(self, queue_name):
        connection = environment.az_connection
        queue = connection.queue()
        queue.select(queue_name)
        return queue.size()
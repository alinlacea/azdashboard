import sys

sys.path = ['../../..'] + sys.path

import azdashboard


def get_app():
    return azdashboard.AzDashboard(template_path='../../app/views/').app

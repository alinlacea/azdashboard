from bottle import static_file

from azdashboard.app.controllers.application_controller import (
    ApplicationController
)


class AssetsController(ApplicationController):
    """Class for handling static assets."""

    def favicon():
        return static_file('favicon.ico', root='azdashboard/app/assets/img')

    def img(filename):
        return static_file(filename, root='azdashboard/app/assets/img')

    def js(filename):
        return static_file(filename, root='azdashboard/app/assets/js')

    def css(filename):
        return static_file(filename, root='azdashboard/app/assets/css')

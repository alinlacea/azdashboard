from azdashboard.app.controllers.assets_controller import AssetsController
from azdashboard.app.controllers.queue_controller import QueueController


def setup_routing(app):
    # static files
    app.route('/img/<filename>', 'GET', AssetsController.img)
    app.route('/js/<filename>', 'GET', AssetsController.js)
    app.route('/css/<filename>', 'GET', AssetsController.css)
    app.route('/favicon.ico', 'GET', AssetsController.favicon)
    app.route('/favicon.png', 'GET', AssetsController.favicon)

    # home
    app.route('/', 'GET', QueueController().all)
    app.route('/<queue_name>', 'GET', QueueController().get_queue)

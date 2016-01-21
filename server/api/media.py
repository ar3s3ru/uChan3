from os.path import join, exists
# Flask related imports
from flask import send_file
# API related imports
from server import uchan

folder = uchan.app.config.get('UPLOAD_FOLDER')


# Using Flask decorator router to avoid JSON serialization of server response
@uchan.app.route('/api/media/<filename>', methods=['GET'])
def media(filename: str):
    """
    Routing function for static media files download from server.

    :param filename: Media file name
    :return: (200 OK - Media file, 404 Not Found, 500 Internal Server Error - cannot read from configuration file)
    """
    if folder is None:
        # Cannot read from configuration file
        return 'Internal Server Error', 500

    path = join(folder, filename)

    if exists(path):
        # If path exists, return file by Flask-based routine
        return send_file(path), 200
    else:
        # ...else, throws 404 Not Found
        return 'Not Found', 404


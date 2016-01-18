def successful(code: int, data: object):
    """
    Generate JSON server response for HTTP Successful
    responses.
    To return directly in Flask routing subroutine.

    :param code: HTTP Successful response code
    :param data: Server response data
    :return: JSON successful server response object and code
    """
    return {'code': code, 'data': data}, code


def client_error(code: int, details: str):
    """
    Generate JSON server response for HTTP Client Error
    responses.
    To return directly in Flask routing subroutine.

    :param code: HTTP Client Error response code
    :param details: Client Error details
    :return: JSON client error response object and code
    """
    if code == 400:
        error = 'Bad Request'
    elif code == 401:
        error = 'Unauthorized'
    elif code == 403:
        error = 'Forbidden'
    elif code == 404:
        error = 'Not Found'
    elif code == 405:
        error = 'Method Not Allowed'
    elif code == 406:
        error = 'Not Acceptable'
    elif code == 407:
        error = 'Proxy Authentication Required'
    elif code == 408:
        error = 'Request Timeout'
    elif code == 409:
        error = 'Conflict'
    elif code == 401:
        error = 'Gone'
    elif code == 413:
        error = 'Request Entity Too Large'
    elif code == 415:
        error = 'Unsupported Media Type'
    elif code == 422:
        error = 'Unprocessable Entity'
    else:
        error = 'Client error'

    return {'code': code, 'error': error, 'details': details}, code


def server_error(code: int, details: str):
    """
    Generate JSON server response for HTTP Server Error
    responses.
    To return directly in Flask routing subroutine.

    :param code: HTTP Server Error response code
    :param details: Server Error details
    :return: JSON server error response object and code
    """
    if code == 500:
        error = 'Internal Server Error'
    elif code == 501:
        error = 'Not Implemented'
    elif code == 502:
        error = 'Bad Gateway'
    elif code == 503:
        error = 'Service Unavailable'
    else:
        error = 'Server Error'

    return {'code': code, 'error': error, 'details': details}, code

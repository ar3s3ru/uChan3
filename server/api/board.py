# Flask related imports
# API related imports
from server import uchan
from server.api import AuthEntity
from server.api import handler, handler_data, handler_args
from server.common import responses, JSONRepresentation
from server.common.routines import str_to_bool
from server.models import User, Board, Thread, ThreadUser


def board_routine(user: User, func, id: int, *args, **kwargs):
    """
    Basic board routine.
    Serves as a layer of abstraction to treat priority errors in board method resource routines.

    This fuction needs to be passed (and called) by session_oriented_request() (inherited from AuthEntity),
    with subroutine function (that has to be called from within this routine) and an ID (serves as Board ID).

    Function passed to this routine needs this signature:
        >>> def func(user: User, board: Board, *args, **kwargs)

    N.B. *args and **kwargs can be omitted.

    :param user:   User Object (got from session_oriented_request())
    :param func:   Subroutine function (needs to be called from within this routine)
    :param id:     Board ID
    :param args:   Name arguments
    :param kwargs: Positional arguments
    :return:
    """
    # Requesting board object
    board = BoardAPI.get_board(id)

    if board is None:
        # Board does not exists
        return responses.client_error(404, 'Board does not exist')
    elif not user.board_subscribed(id):
        # User not subscribed to this board
        return responses.client_error(401, 'User is not authorized to see this board')

    # Return the result got from closure function passed as argument
    return func(user, board, *args, **kwargs)


class BoardAPI(AuthEntity):
    """
    Board API Resource entity.
    Regulates board contents show and creation.

    This class inherits from AuthEntity class, since only valid and subscribed users can access a particular board.
    """
    def __init__(self):
        """
        Override superclass constructor to define resource-specific POST JSON fields.

        :return: New Board API object
        """
        super().__init__()

        self.form.add_argument('anon', type=str, location='json')
        self.form.add_argument('title', type=str, location='json')
        self.form.add_argument('text', type=str, location='json')
        self.form.add_argument('image', type=str, location='json')
        self.form.add_argument('image_name', type=str, location='json')

    @staticmethod
    def get_board(board_id: int):
        """
        Query the database and retrieve Board object with desired ID.

        :param board_id: Desired Board ID
        :return: Board object if exists, else None
        """
        return Board.query.get(board_id)

    @handler_args
    def validate_args(self):
        """
        Validates JSON POST arguments.
        Raises ValueError if at least one argument is not valid.

        :return: If POST JSON arguments are valid
        """
        if len(self.args['title']) > 50 or len(self.args['text']) > 1250:
            raise ValueError('Invalid title or text length')
        elif not self.args['anon'] in ['True', 'true', 'False', 'false']:
            raise ValueError('Invalid anonymous field')

    @handler
    def get(self, id: int, page=1):
        """
        GET method implementation for Board API resource entity.

        :param id:   Board ID
        :param page: Board page query
        :return: JSON response (200 OK - Board's threads list, for other errors, see "session_oriented_request")
        """
        def routine(user: User, board: Board):
            """
            Returns Board's threads list, in JSON representation.

            :param user:  Requesting User object
            :param board: Board object
            :return: Board's threads list
            """
            return responses.successful(200, [JSONRepresentation.thread(thread, user)
                                              for thread in board.get_threads(page)])

        return self.session_oriented_request(board_routine, routine, id)

    @handler_data
    def post(self, id: int):
        """
        POST method implementation for Board API resource entity.

        :param id: Board ID
        :return: JSON response (201 Created - New thread, 400 Bad Request - invalid POST data parameters)
        """
        def routine(user: User, board: Board):
            """
            Create new Thread linked to specified board, from POST JSON data.

            :param user:  Requesting User object
            :param board: Board object
            :return: New thread inside specified board
            """
            try:
                # Check thread JSON arguments
                self.check_args()
                self.validate_args()

                # Process anon, image and construct new entity
                anon   = str_to_bool(self.args['anon'])
                image  = self.media_processing()
                thread = Thread(anon, self.args['title'], self.args['text'], image, board.id, user.id)

                # Add new Thread table to database
                uchan.add_to_db(thread)

                # Add new ThreadUser link
                thread = user.get_last_thread()
                uchan.add_to_db(ThreadUser(thread.id, user.id))

                return responses.successful(201, JSONRepresentation.thread(thread, user))
            except ValueError as msg:
                return responses.client_error(400, '{}'.format(msg))
            except KeyError as key:
                return responses.client_error(400, 'Invalid parameter: {}'.format(key))

        return self.session_oriented_request(board_routine, routine, id)


uchan.api.add_resource(BoardAPI, '/api/board/<int:id>', '/api/board/<int:id>/<int:page>')

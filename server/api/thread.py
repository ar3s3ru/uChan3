# API related imports
from server import uchan
from server.api import AuthEntity
from server.api import handler, handler_data, handler_args
from server.models import Thread, User, Post, ThreadUser
from server.common import responses
from server.common import JSONRepresentation
from server.common.routines import str_to_bool


def thread_routine(user: User, func, id: int, *args, **kwargs):
    """
    Basic thread routine.
    Serves as a layer of abstraction to thread priority errors in thread method resource routines.

    This function needs to be passed (and called) by session_oriented_request() (inherited from AuthEntity),
    with subroutine function (that has to be called from within this routine) and an ID (serves as Thread ID).

    Function passed to this routine needs this signature:
        >>> def func(user: User, thread: Thread, *args, **kwargs)

    N.B. *args and **kwargs can be omitted.

    :param user:   User Object (got from session_oriented_request())
    :param func:   Subroutine function (needs to be called from within this routine)
    :param id:     Thread ID
    :param args:   Name arguments
    :param kwargs: Positional arguments
    :return:
    """
    thread = ThreadAPI.get_thread(id)

    if thread is None:
        return responses.client_error(404, 'Thread does not exist')

    if not user.board_subscribed(thread.board):
        return responses.client_error(401, 'User is not authorized to see this thread')

    return func(user, thread, *args, **kwargs)


class ThreadAPI(AuthEntity):
    """
    Thread API resource entity.
    Regulates threads deletion, and thread contents show and creation.

    Since only valid and authorized users can submit posts, view threads and so on, it needs to be inherited
    from AuthEntity class.
    """

    # Unnecessary POST JSON data fields
    unnecessary = ['image', 'image_name', 'reply']

    def __init__(self):
        """
        Overloads AuthEntity constructor to add Post creation JSON fields.

        :return: New ThreadAPI object
        """
        super().__init__()

        self.form.add_argument('anon', type=str, location='json')
        self.form.add_argument('text', type=str, location='json')
        self.form.add_argument('image', type=str, location='json')
        self.form.add_argument('image_name', type=str, location='json')
        self.form.add_argument('reply', type=int, location='json')

    @handler_args
    def check_args(self):
        """
        Checks if necessary JSON POST data arguments are present.

        :return: If necessary POST arguments are present
        """
        for arg in self.args:
            if arg not in self.unnecessary and self.args[arg] is None:
                raise ValueError('Missing parameter: {}'.format(arg))

    @handler_args
    def validate_args(self):
        """
        Validate JSON POST arguments.

        :return: If JSON POST arguments are valid
        """
        if len(self.args['text']) > 1250:
            raise ValueError('Invalid parameter: text')
        elif not self.args['anon'] in ['True', 'true', 'False', 'false']:
            raise ValueError('Invalid anonymous field')
        elif self.args['reply'] is not None and self.args['reply'] < 1:
            raise ValueError('Invalid parameter: reply')

    @staticmethod
    def get_thread(thread_id: int):
        """
        Queries the database to retrieve Thread object from specified ID.

        :param thread_id: Thread ID
        :return: Specified Thread object
        """
        return Thread.query.get(thread_id)

    @handler
    def get(self, id: int, page=1):
        """
        GET method implementation for Thread API resource entity.

        :param id:   Thread ID
        :param page: Thread page (for pagination query)
        :return: 200 OK - Thread's Posts list (for other errors see AuthEntity.session_oriented_request())
        """
        def routine(user: User, thread: Thread):
            """
            Returns Thread's Posts list in JSON object representation.

            :param user:   Requesting User object
            :param thread: Thread ID
            :return: Thread's Posts list in JSON
            """
            return responses.successful(200, [JSONRepresentation.post(post, thread, user)
                                              for post in thread.get_posts(page)])

        return self.session_oriented_request(thread_routine, routine, id)

    @handler_data
    def post(self, id: int):
        """
        POST method implementation for Thread API resource entity.

        :param id: Thread ID
        :return: 201 Created - New Post inside Thread, 400 Bad Request - Issues with POST data fields
        """
        def routine(user: User, thread: Thread):
            """
            Creates new Post table object and returns it as JSON representation.
            Image posting is totally optional (but if chosen, it needs both 'image' and 'image_name' fields.

            :param user:   User object
            :param thread: Thread object
            :return: New Post Object as JSON object
            """
            try:
                self.check_args()
                self.validate_args()

                anon  = str_to_bool(self.args['anon'])
                image = self.media_processing() if self.args['image'] is not None and \
                                                   self.args['image_name'] is not None else None

                post = Post((user.id == thread.author), anon, self.args['text'], thread.id, user.id, thread.board,
                            self.args['reply'], image)

                # Add new Post table to database
                uchan.add_to_db(post)

                # Add new ThreadUser link
                if thread.get_authid(user.id) is None:
                    uchan.add_to_db(ThreadUser(thread.id, user.id))

                # Increments thread counter
                thread.incr_replies((image is not None))
                uchan.commit()

                return responses.successful(201, JSONRepresentation.post(thread.get_last_post(), thread, user))
            except ValueError as msg:
                return responses.client_error(400, '{}'.format(msg))

        return self.session_oriented_request(thread_routine, routine, id)

    @handler
    def delete(self, id: int):
        """
        DELETE method implementation for ThreadAPI resource entity.

        :param id: Thread ID
        :return: 204 No Content (successfully deleted) - 401 Unauthorized (cannot delete thread)
        """
        def routine(user: User, thread: Thread):
            if not user.admin and thread.author != user.id:
                return responses.client_error(401, 'User cannot delete this thread')

            for post in thread.posts:
                uchan.delete_from_db(post, False)

            uchan.delete_from_db(thread)

            return '', 204

        return self.session_oriented_request(thread_routine, routine, id)


uchan.api.add_resource(ThreadAPI, '/api/thread/<int:id>', '/api/thread/<int:id>/<int:page>')

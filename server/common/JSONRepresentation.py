from server.models import University, User, Board, Thread, Post, ChatRequest, Chat, Message
from server.common.routines import get_request


############################################
# University representation                #
############################################
def university(university: University):
    """
    University JSON representation, from University object.

    :param university: University object
    :return: University object JSON representation
    """
    return {
            'id':         university.id,
            'name':       university.name,
            'city':       university.city,
            'domain':     university.domain,
            'suggestion': university.suggestion
        }


############################################
# Board representation                     #
############################################
def board(board: Board):
    """
    Board object representation ready for JSON serialization.

    :param board: Board object
    :return: Dictionary with Board representation fields
    """
    return {'id': board.id, 'memo': board.memo, 'name': board.name}


############################################
# Me representation                        #
############################################
def me(user: User):
    """
    User object representation ready for JSON serialization.

    :param user: User object
    :return: Dictionary with User representation fields
    """
    return {
        'id':         user.id,
        'nickname':   user.nickname,
        'university': University.query.get(user.university).name,
        'gender':     user.get_gender(),
        'boards':     [board(b) for b in user.get_boards()],
        'profilepic': user.profilepic
    }


############################################
# Thread representation                    #
############################################
def thread_author(thread: Thread, user=None):
    """
    Thread author JSON representation, from Thread object.

    :param thread: Thread object
    :param user:   Requesting User object
    :return: Thread author object JSON representation
    """
    if user is None or user.id != thread.author:
        # If requesting user is None or different from Thread Original Poster, request OP User object
        user = User.query.get(thread.author)

    if user is None:
        # IMPOSSIBLE - User cannot be None at this point
        raise AssertionError('Author has to be present')
    elif thread.anon:
        # If Anonymous is set, returns gender and authid
        # TODO: implement chat requests
        return {'gender': user.get_gender(), 'authid': thread.get_author_authid(), 'chat': get_request(thread, user)}
    else:
        # TODO: implement chat requests
        return {
            'nickname':   user.nickname,
            'university': University.query.get(user.university).name,
            'gender':     user.gender,
            'chat':       get_request(thread, user)
        }


def thread(thread: Thread, user: User):
    """
    Thread Object representation from Thread Database Object.

    :param thread: Thread Database Object
    :param user:   Requesting User object
    :return: Thread Object JSON representation
    """
    return {
        'id':      thread.id,
        'board':   thread.board,
        'anon':    not user.admin and thread.anon,
        'title':   thread.title,
        'text':    thread.text,
        'image':   thread.get_image(),
        'posted':  str(thread.posted),
        'replies': thread.replies,
        'images':  thread.images,
        'delete':  user.admin or (thread.author == user.id),
        'author':  thread_author(thread, user)
    }


############################################
# Post representation                      #
############################################
def post_author(post: Post, thread: Thread, user=None):
    """
    Post author JSON representation, from Post object.

    :param post:   Post object
    :param thread: Thread parent object
    :param user:   Requesting User object
    :return: Post author object JSON representation
    """
    if user is None or user.id != post.author:
        user = User.query.get(post.author)

    if user is None:
        raise AssertionError('Author has to be present')
    elif post.anon:
        return {'gender': user.get_gender(), 'authid': post.get_authid(), 'chat': get_request(thread, user)}
    else:
        # TODO: implement chat requests
        return {
            'nickname':   user.nickname,
            'university': University.query.get(user.university).name,
            'gender':     user.gender,
            'chat':       get_request(thread, user)
        }


def post(post: Post, thread: Thread, user: User):
    """
    Post Object representation from Post Database Object.

    :param post:   Post object
    :param thread: Thread parent object
    :param user:   Requesting User object
    :return: Post Object JSON representation
    """
    return {
        'id':     post.id,
        'thread': post.thread,
        'anon':   not user.admin and post.anon,
        'text':   post.text,
        'image':  post.get_image(),
        'op':     post.op,
        'reply':  post.reply,
        'author': post_author(post, user),
        'delete': user.admin or post.author == user.id
    }


############################################
# Chat representation                      #
############################################
def chatuser(user: User):
    return {
        'id':         user.id,
        'nickname':   user.nickname,
        'university': University.query.get(user.university).name,
        'gender':     user.get_gender(),
        'profilepic': user.profilepic
    }


def chatrequest(chatrequest: ChatRequest):
    user = User.query.get(chatrequest.u_from)

    return {
        'id':   chatrequest.id,
        'from': chatuser(user),
    }


def chat(chat: Chat, user: User):
    return {
        'id':   chat.id,
        'last': str(chat.last),
        'user': chatuser(User.query.get(chat.user1) if chat.user2 == user.id else User.query.get(chat.user2))
    }


def message(message: Message):
    return {
        'id':    message.id,
        'from':  message.u_from,
        'to':    message.u_to,
        'image': message.image,
        'text':  message.text,
        'sent':  str(message.sent)
    }
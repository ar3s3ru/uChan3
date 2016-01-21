from datetime import datetime
from dateutil.relativedelta import relativedelta
# API related imports
from server import uchan
from server.common.routines import calculate_authid

# Database session reference
db = uchan.db


class User(db.Model):
    """
    Model for user table in the database.
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    nickname   = db.Column(db.String(20), unique=True)
    password   = db.Column(db.String(64))
    salt       = db.Column(db.String(20))
    university = db.Column(db.Integer, db.ForeignKey('university.id'))
    profilepic = db.Column(db.String(36), unique=True)
    email      = db.Column(db.String(30))
    gender     = db.Column(db.Boolean)
    activated  = db.Column(db.Boolean)
    token      = db.Column(db.String(36), unique=True)
    admin      = db.Column(db.Boolean)
    boards     = db.relationship('UserBoard', lazy='joined')
    threads    = db.relationship('Thread', lazy='dynamic')
    chats      = db.relationship('Chat', lazy='dynamic')

    def __init__(self, nickname: str, password: str, salt: str, university: int, email: str, gender: str,
                 activated: bool, token: str, admin=False):
        """
        Constructor for user table entry.

        :param nickname:   User nickname
        :param password:   User salted password (SHA256)
        :param salt:       Salt for password generation
        :param university: User university id
        :param email:      User email
        :param gender:     User gender
        :param activated:  Denote if user is active or not
        :param token:      Activation token
        :param admin:      Admin user
        :return: User object
        """
        self.nickname   = nickname
        self.password   = password
        self.salt       = salt
        self.university = university
        self.email      = email
        self.activated  = activated
        self.token      = token
        self.admin      = admin
        self.gender     = gender == 'f'

    def __repr__(self):
        """
        User representation for interactive mode.

        :return: User object representation
        """
        return '<User %r>' % self.nickname

    def get_email(self):
        """
        Get user complete email.

        :return: User email
        """
        university = University.query.get(self.university)
        return self.email + '@' + university.domain

    def get_gender(self):
        """
        Returns User related gender.

        :return: 'm' if user is male, 'f' is user is female
        """
        return 'f' if self.gender else 'm'

    def get_last_thread(self):
        """
        Returns last thread submitted by this user.

        :return: Last submitted thread
        """
        return self.threads.order_by(Thread.id.desc()).first()

    def get_threads(self, page: int):
        """
        Returns page list of user threads.
        Max. 10 threads per page.

        :param page: Page list in pagination query.
        :return: User's threads list (max. 10 per page)
        """
        return self.threads.order_by(Thread.id.desc()).paginate(page, 10, False).items

    def board_subscribed(self, bid: int):
        """
        Check if the user is subscribed to a certain board.

        :param bid: Board ID
        :return: User subscription to Board
        """
        return UserBoard.query.filter_by(user=self.id, board=bid).first() is not None

    def get_boards(self):
        """
        Get user subscribed boards.

        :return: List of all user subscribed boards
        """
        return [Board.query.get(ub.board) for ub in self.boards]

    def has_requested_chat(self, user: int):
        return ChatRequest.query.filter_by(u_from=self.id, u_to=user).first() is not None

    def get_requests(self):
        return ChatRequest.query.filter_by(u_to=self.id, activated=False).all()

    def get_chats(self, page: int):
        return self.chats.order_by(Chat.last.desc()).paginate(page, 10, False).items


class Moderator(db.Model):
    """
    Class definition for boards moderators.
    Moderators can delete other user posts.
    """
    __tablename__ = 'moderator'

    id = db.Column(db.Integer, primary_key=True)
    user  = db.Column(db.Integer, db.ForeignKey('user.id'))
    board = db.Column(db.Integer, db.ForeignKey('board.id'))

    def __init__(self, user: int, board: int):
        """
        Construct Moderator object as mapping between an user and a board.

        :param user:  User id
        :param board: Board id
        :return: New Moderator object
        """
        self.user  = user
        self.board = board

    def __repr__(self):
        """
        Representation of Moderator object in interactive mode.

        :return: Moderator interactive mode representation
        """
        return '<Moderator {0}@{1}>'.format(self.user, self.board)


class University(db.Model):
    """
    Model for university table in the database.
    """
    __tablename__ = 'university'

    id = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(30), unique=True)
    city       = db.Column(db.String(20))
    domain     = db.Column(db.String(20))
    suggestion = db.Column(db.String(20))
    users      = db.relationship('User', backref='user', lazy='joined')

    def __init__(self, name: str, city: str, domain: str, suggestion: str):
        """
        Constructor for university entry table.

        :param name:       University name
        :param city:       University city
        :param domain:     University mail domain
        :param suggestion: University mail suggestion
        :return: University object
        """
        self.name   = name
        self.city   = city
        self.domain = domain

        if suggestion is None:
            self.suggestion = ''
        else:
            self.suggestion = suggestion

    def __repr__(self):
        """
        University representation for interactive mode.

        :return: University object representation
        """
        return '<University %r>' % self.name


class Session(db.Model):
    """
    Model for session representation in database.
    """
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    ipaddr = db.Column(db.String(15))
    token  = db.Column(db.String(36), unique=True)
    create = db.Column(db.DateTime)
    expire = db.Column(db.DateTime)
    user   = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, ipaddr: str, token: str, user: int):
        """
        Constructor for session entry table

        :param ipaddr: IP of user bind to this session
        :param token:  Token for this session
        :param user:   User ID for this session
        :return: Session object
        """
        self.ipaddr = ipaddr
        self.token  = token
        self.user   = user
        self.create = datetime.now()
        self.expire = self.create + relativedelta(months=+1)

    def __repr__(self):
        """
        Session representation for interactive mode.

        :return: Session object representation
        """
        return '<Session {0}@{1}: expires {2}>'.format(self.ipaddr, self.token, self.expire)


class Board(db.Model):
    """
    Model for board representation in database.
    """
    __tablename__ = 'board'

    id = db.Column(db.Integer, primary_key=True)
    memo       = db.Column(db.String(10), unique=True)
    name       = db.Column(db.String(30), unique=True)
    # University.id = 1 -> General boards
    university = db.Column(db.Integer, db.ForeignKey('university.id'))
    users      = db.relationship('UserBoard', lazy='dynamic')
    threads    = db.relationship('Thread', lazy='dynamic')
    moderators = db.relationship('Moderator', lazy='dynamic')

    def __init__(self, memo: str, name: str, university: int):
        """
        Constructor for Board entry table.

        :param memo:       Board name in short
        :param name:       Board name
        :param university: Board university ID
        :return: Board object
        """
        self.memo       = memo
        self.name       = name
        self.university = university

    def __repr__(self):
        """
        Board representation for interactive mode.

        :return: Board object representation
        """
        return '<Board {0} - {1}>'.format(self.memo, self.name)

    def get_pinneds(self):
        """
        Returns Pinned Thread objects.

        :return: Pinned Thread objects
        """
        return self.threads.filter_by(pinned=True).all()

    def get_threads(self, page: int):
        """
        Returns list thread page, in pagination query (max. 8 per page)

        :param page: Thread list page (pagination query)
        :return: Thread list
        """
        if page == 1:
            return self.get_pinneds() + self.threads.order_by(Thread.id.desc()).paginate(page, 8, False).items
        else:
            return self.threads.order_by(Thread.id.desc()).paginate(page, 8, False).items


class UserBoard(db.Model):
    """
    Model for many-to-many relationship between Users and Boards.
    """
    __tablename__ = 'userboard'

    id = db.Column(db.Integer, primary_key=True)
    user  = db.Column(db.Integer, db.ForeignKey('user.id'))
    board = db.Column(db.Integer, db.ForeignKey('board.id'))

    def __init__(self, user: int, board: int):
        """
        Constructor for many-to-many relationship User-Board.

        :param user:  Relationship user ID
        :param board: Relationship board ID
        :return: UserBoard object
        """
        self.user  = user
        self.board = board

    def __repr__(self):
        """
        UserBoard representation for interactive mode.

        :return: UserBoard object representation
        """
        return '<User {0} - Board {1}>'.format(self.user, self.board)


class Thread(db.Model):
    """
    Model for representation of Threads in the database.
    """
    __tablename__ = 'thread'

    id = db.Column(db.Integer, primary_key=True)
    # Content related fields
    anon    = db.Column(db.Boolean)
    title   = db.Column(db.String(50), nullable=False)
    text    = db.Column(db.String(1250), nullable=False)
    image   = db.Column(db.String(36), nullable=False)
    pinned  = db.Column(db.Boolean)
    posted  = db.Column(db.DateTime, nullable=False)
    # Interaction related fields
    replies = db.Column(db.Integer, nullable=False)
    images  = db.Column(db.Integer, nullable=False)
    # Placement related fields
    board   = db.Column(db.Integer, db.ForeignKey('board.id'))
    author  = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Relationships
    posts   = db.relationship('Post', lazy='dynamic')
    users   = db.relationship('ThreadUser', lazy='dynamic')

    def __init__(self, anon: bool, title: str, text: str, image: str, board: int, author: int, pinned=False):
        """
        Constructor for Thread object.

        :param anon:   Anonymous
        :param title:  Thread title
        :param text:   Thread text content
        :param image:  Thread image
        :param board:  Thread Board ID
        :param author: Thread Author ID
        :param pinned: Pinned thread
        :return: New Thread object
        """
        self.anon   = anon
        self.title  = title
        self.text   = text
        self.image  = image
        self.board  = board
        self.author = author
        self.pinned = pinned
        self.posted = datetime.now()
        # New object
        self.images  = 0
        self.replies = 0

    def __repr__(self):
        """
        Thread representation for interactive mode.

        :return: Thread object representation
        """
        return '<Thread {0} from {1}>'.format(self.title, self.author)

    def get_image(self):
        """
        Returns thread image.

        :return: Thread image route
        """
        return 'media/' + self.image

    def get_author_authid(self):
        """
        Returns author authid (first authid in the table entry)

        :return: Author AuthID
        """
        return self.users.first().authid

    def get_authid(self, _user: int):
        """
        Returns authid of specified user.

        :param _user: User ID
        :return: authid of specified user
        """
        link = self.users.filter_by(user=_user).first()
        return link.authid if link is not None else None

    def get_posts(self, page: int):
        """
        Returns list posts page, in pagination query (max. 10 elements per page).

        :param page: Posts list page
        :return: Posts list
        """
        return self.posts.paginate(page, 10, False).items

    def get_last_post(self):
        """
        Returns last thread's post created.

        :return: Last post created
        """
        return self.posts.order_by(Post.id.desc()).first()

    def incr_replies(self, image: bool):
        """
        Increments thread replies counter; if image is True, increments thread images counter, as well.

        :param image: If thread post image is added as well
        :return: None
        """
        self.replies += 1

        if image:
            self.images += 1

    def decr_replies(self, image: bool):
        """
        Decrements thread replies counter; if image is True, decrements thread images counter, as well.

        :param image: If thread post image is deleted as well
        :return: None
        """
        self.replies -= 1

        if image:
            self.images -= 1

    def get_threaduser(self, user: int):
        """
        Returns ThreadUser table related to this thread and specified user.

        :param user: Specified User ID
        :return: ThreadUser object
        """
        return self.users.filter_by(user=user).first()


class ThreadUser(db.Model):
    """
    Classe mapping many-to-many per gestire il riferimento agli utenti
    anonimi in un determinato thread.
    """
    __tablename__ = 'threaduser'

    id = db.Column(db.Integer, primary_key=True)
    thread = db.Column(db.Integer, db.ForeignKey('thread.id'))
    user   = db.Column(db.Integer, db.ForeignKey('user.id'))
    follow = db.Column(db.Boolean)
    authid = db.Column(db.String(8))

    def __init__(self, thread: int, user: int):
        """
        Construct ThreadUser object as mapping between a thread and an user.

        :param thread: Thread id
        :param user:   User id
        :return: New ThreadUser object
        """
        self.thread = thread
        self.user   = user
        self.follow = True
        self.authid = calculate_authid(self.thread, self.user)

    def __repr__(self):
        """
        Representation of ThreadUser object in interactive mode.

        :return: ThreadUser interactive mode representation
        """
        return '<Thread {0} - User {1} = UID {2}>'.format(self.thread, self.user, self.id)


class Post(db.Model):
    """
    Post model representation for database use.
    """
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    # Content related fields
    op      = db.Column(db.Boolean)
    anon    = db.Column(db.Boolean)
    text    = db.Column(db.String(1250), nullable=False)
    image   = db.Column(db.String(36))
    posted  = db.Column(db.DateTime, nullable=False)
    # Interaction related fields
    reply   = db.Column(db.Integer, db.ForeignKey('post.id'))
    thread  = db.Column(db.Integer, db.ForeignKey('thread.id'))
    author  = db.Column(db.Integer, db.ForeignKey('user.id'))
    board   = db.Column(db.Integer, db.ForeignKey('board.id'))
    # Relationship related fields
    replies = db.relationship('Post', lazy='joined')

    def __init__(self, op: bool, anon: bool, text: str, thread: int, author: int, board: int, reply=None, image=None):
        """
        Constructor for Post object.

        :param op:     Thread original poster
        :param anon:   Anonymous
        :param text:   Post text content
        :param image:  Post image
        :param thread: Thread ID
        :param author: Author ID
        :param board:  Board ID
        :return: New Post object
        """
        self.op     = op
        self.anon   = anon
        self.text   = text
        self.image  = image
        self.thread = thread
        self.author = author
        self.board  = board
        self.reply  = reply
        self.posted = datetime.now()

    def __repr__(self):
        """
        Post representation for interactive mode.

        :return: Post object representation
        """
        return '<Post {0} - Thread: {1}>'.format(self.text[0:5] + '...', self.thread)

    def get_replies(self):
        """
        Get all posts that replied to this post.

        :return: Replies
        """
        return self.replies.all()

    def get_image(self):
        """
        Get post image.

        :return: Post image route
        """
        return 'media/' + self.image if self.image is not None else None

    def get_authid(self):
        """
        Returns poster authid.

        :return: Post author authid
        """
        return ThreadUser.query.filter_by(user=self.author, thread=self.thread).first().authid


class ChatRequest(db.Model):
    __tablename__ = 'chatrequest'

    id = db.Column(db.Integer, primary_key=True)
    u_from   = db.Column(db.Integer, db.ForeignKey('user.id'))
    u_to     = db.Column(db.Integer, db.ForeignKey('user.id'))
    accepted = db.Column(db.Boolean)

    def __init__(self, user_from: int, user_to: int):
        self.u_from   = user_from
        self.u_to     = user_to
        self.accepted = False
        self.chat     = None

    def accept(self):
        self.accepted = True


class Chat(db.Model):
    __tablename__ = 'chat'

    id = db.Column(db.Integer, primary_key=True)
    user1    = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2    = db.Column(db.Integer, db.ForeignKey('user.id'))
    last     = db.Column(db.DateTime)
    messages = db.relationship('Message', lazy='dynamic')

    def __init__(self, user1: int, user2: int):
        self.user1 = user1
        self.user2 = user2
        self.last  = datetime.now()

    def get_messages(self, page: int):
        return self.messages.order_by(Message.sent.desc()).paginate(page, 20, False).items


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    chat   = db.Column(db.Integer, db.ForeignKey('chat.id'))
    u_from = db.Column(db.Integer, db.ForeignKey('user.id'))
    u_to   = db.Column(db.Integer, db.ForeignKey('user.id'))
    text   = db.Column(db.String(1250), nullable=False)
    image  = db.Column(db.String(36))
    sent   = db.Column(db.DateTime)

    def __init__(self, chat: int, mfrom: int, mto: int, text: str, image=None):
        self.chat  = chat
        self.mfrom = mfrom
        self.mto   = mto
        self.text  = text
        self.image = image
        self.sent  = datetime.now()

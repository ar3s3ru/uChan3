from server import uchan
from server.api import AuthEntity, AuthException
from server.api.university import UniversityAPI
from server.models import Thread, User


class ThreadAPI(AuthEntity):
    @staticmethod
    def thread_author_representation(thread: Thread, user=None):
        if user is None:
            user = User.query.get(thread.author)

        if user is None:
            raise Exception
        elif thread.anon:
            return {'gender': user.get_gender(), 'authid': thread.get_author_authid()}
        else:
            # TODO: implement chat requests
            return {
                'nickname': user.nickname,
                'university': UniversityAPI.university_id(user.university).name,
                'gender': user.gender
            }

    @staticmethod
    def thread_representation(thread: Thread, user: User):
        return {
            'id': thread.id,
            'board': thread.board,
            'anon': not user.admin and thread.anon,
            'title': thread.title,
            'text': thread.text,
            'image': thread.get_image(),
            'posted': str(thread.posted),
            'replies': thread.replies,
            'images': thread.images,
            'delete': user.admin and (thread.author == user.id),
            'author': ThreadAPI.thread_author_representation(thread, user) if thread.author == user.id
                      else ThreadAPI.thread_author_representation(thread)
        }

uchan.api.add_resource(ThreadAPI, '/api/thread/<int:id>', '/api/thread/<int:id>/<int:page>')

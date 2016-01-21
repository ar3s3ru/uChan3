from server import uchan
from server.api import AuthEntity
from server.api import handler
from server.models import User, Post
from server.common import responses
from server.api.thread import ThreadAPI


class PostAPI(AuthEntity):

    @staticmethod
    def get_post(id: int):
        return Post.query.get(id)

    @handler
    def delete(self, id: int):
        def routine(user: User):
            # Retrieve post
            post = self.get_post(id)

            if post is None:
                # Post does not exist
                return responses.client_error(404, 'Post does not exist')

            if not user.admin and post.author != user.id:
                # Post cannot be deleted from requesting user
                return responses.client_error(401, 'User cannot delete this post')

            image  = post.image is not None             # If post has image
            thread = ThreadAPI.get_thread(post.thread)  # Retrieve thread parent

            if thread is None:
                # Thread is None, IMPOSSIBLE
                raise AssertionError('Thread cannot be None')

            # Delete post from database and decrement replies
            uchan.delete_from_db(post, False)
            thread.decr_replies(image)
            uchan.commit()

            return '', 204

        return self.session_oriented_request(routine)


uchan.api.add_resource(PostAPI, '/api/post/<int:id>')

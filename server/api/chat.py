from server import uchan
from server.api import AuthEntity
from server.api import handler, handler_data, handler_args
from server.models import User, ThreadUser, ChatRequest, Chat, Message
from server.common import responses, JSONRepresentation
from server.common.routines import str_to_bool


# --------------------------------------------------------------------------------------------------------------------->
#  Chat requests   # -------------------------------------------------------------------------------------------------->
# --------------------------------------------------------------------------------------------------------------------->
class ChatRequestAPI(AuthEntity):

    @staticmethod
    def get_threaduser(id: int):
        return ThreadUser.query.get(id)

    @handler
    def get(self):
        def requests_routine(user: User):
            return responses.successful(200, [JSONRepresentation.chatrequest(req)
                                              for req in user.get_requests() if req.accepted is False])

        return self.session_oriented_request(requests_routine)

    @handler
    def post(self, id: int):
        def request_routine(user: User):
            threaduser = ChatRequestAPI.get_threaduser(id)

            if threaduser is None:
                return responses.client_error(404, 'User map object does not exists')

            if user.has_requested_chat(threaduser.user):
                return responses.client_error(409, 'Chat already requested')

            request = ChatRequest(user.id, threaduser.user)
            uchan.add_to_db(request)

            return responses.successful(201, 'Chat request sent')

        return self.session_oriented_request(request_routine)


uchan.api.add_resource(ChatRequestAPI, '/api/chat/request', '/api/chat/request/<int:id>')
# --------------------------------------------------------------------------------------------------------------------->


# --------------------------------------------------------------------------------------------------------------------->
#  Chat  # ------------------------------------------------------------------------------------------------------------>
# --------------------------------------------------------------------------------------------------------------------->
def accept_chat_routine(user: User, func, id: int, *args, **kwargs):
    chatrequest = AcceptChatAPI.get_chatrequest(id)

    if chatrequest is None:
        responses.client_error(404, 'Chat request does not exists')

    if chatrequest.u_to != user.id:
        responses.client_error(401, 'Cannot use this chat request')

    if chatrequest.accepted:
        responses.client_error(409, 'Chat request already accepted')

    return func(user, chatrequest, *args, **kwargs)


class AcceptChatAPI(AuthEntity):

    @staticmethod
    def get_chatrequest(id: int):
        return ChatRequest.query.get(id)

    @staticmethod
    def get_chat(id: int):
        return Chat.query.get(id)

    @handler
    def post(self, id: int):
        def accepting_routine(user: User, chatrequest: ChatRequest):
            # Define new Chat entity
            chat = Chat(chatrequest.u_from, chatrequest.u_to)
            chatrequest.accept()
            uchan.add_to_db(chat)

            # Return new chat
            return responses.successful(201, 'Chat request accepted')

        return self.session_oriented_request(accept_chat_routine, accepting_routine, id)

    @handler
    def delete(self, id: int):
        def deleting_routine(user: User, chatrequest: ChatRequest):
            # Delete ChatRequest
            uchan.delete_from_db(chatrequest)
            return '', 204

        return self.session_oriented_request(accept_chat_routine, deleting_routine, id)

uchan.api.add_resource(AcceptChatAPI, '/api/chat/accept/<int:id>')
# --------------------------------------------------------------------------------------------------------------------->

from server import uchan
from server.api import BasicEntity
from server.api import handler
from server.common import responses


class DecoratedHello(BasicEntity):
    @handler
    def get(self):
        return responses.successful(200, 'Hello m8')

uchan.api.add_resource(DecoratedHello, '/')

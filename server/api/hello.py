from server import uchan
from server.api import BasicEntity
from server.common import responses


class DecoratedHello(BasicEntity):
    def get(self):
        return 'Hello m8'

uchan.api.add_resource(DecoratedHello, '/')

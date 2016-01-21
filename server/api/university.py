from server import uchan
from server.models import University
from server.api import BasicEntity
from server.api import handler
from server.common import responses, JSONRepresentation


class UniversityAPI(BasicEntity):
    """
    University API resource entity.
    Retrieves university object(s) from database, and serves it in JSON format.

    Since these objects can be visible from outside (but inside the uChan platform), this resource class
    has to inherit from BasicEntity.
    """
    @staticmethod
    def university_list():
        """
        Returns universities list (present in the database).

        :return: Universities list
        """
        return University.query.all()

    @staticmethod
    def university_id(id: int):
        """
        Retrive a particular University table from the database.

        :param id: Specific University ID
        :return: University object (if exists with ID 'id'), else None
        """
        return University.query.get(id)

    @handler
    def get(self, id=None):
        """
        GET method implementation for University API resource.

        :param id: University ID
        :return: Universities list (if id is None), else an University object (if id is not None); JSON representation.
                 University with ID == 1 is not accessible (401 Unauthorized, if requested);
                 University with ID not in the database will result in 404 Not Found.
        """
        if id is None:
            return responses.successful(200, [JSONRepresentation.university(uni)
                                              for uni in self.university_list() if uni.id != 1])
        elif id == 1:
            return responses.client_error(401, 'Cannot request this university')
        else:
            university = self.university_id(id)

            if university is None:
                return responses.client_error(404, 'University not found')
            else:
                return responses.successful(200, JSONRepresentation.university(university))

uchan.api.add_resource(UniversityAPI, '/api/university', '/api/university/<int:id>')


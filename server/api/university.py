from server import uchan
from server.models import University
from server.api import BasicEntity
from server.api import handler
from server.common import responses


class UniversityAPI(BasicEntity):

    @staticmethod
    def university_list():
        return University.query.all()

    @staticmethod
    def university_id(id: int):
        return University.query.get(id)

    @staticmethod
    def university_representation(university: University):
        return {
            'id':         university.id,
            'name':       university.name,
            'city':       university.city,
            'domain':     university.domain,
            'suggestion': university.suggestion
        }

    @handler
    def get(self, id=None):
        if id is None:
            return responses.successful(200, [self.university_representation(uni)
                                              for uni in self.university_list() if uni.id != 1])
        elif id == 1:
            return responses.client_error(401, 'Cannot request this university')
        else:
            university = self.university_id(id)

            if university is None:
                return responses.client_error(404, 'University not found')
            else:
                return responses.successful(200, self.university_representation(university))

uchan.api.add_resource(UniversityAPI, '/api/university', '/api/university/<int:id>')

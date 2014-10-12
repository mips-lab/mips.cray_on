from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import Authenticated

class RootFactory(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, Authenticated, 'authenticated')]

    def __init__(self, request):
        pass

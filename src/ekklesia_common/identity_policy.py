import logging
import morepath
from ekklesia_common.database.datamodel import User


logg = logging.getLogger(__name__)


class UserIdentity(morepath.Identity):

    def __init__(self, user):
        self.user = user

    @property
    def userid(self):
        return self.user.id


class NoIdentity(morepath.Identity):
    user = None
    userid = None


class EkklesiaIdentityPolicy(morepath.IdentityPolicy):

    identity_class = UserIdentity

    def remember(self, response, request, identity):
        request.browser_session['user_id'] = identity.user.id

    def identify(self, request):
        user_id = request.browser_session.get('user_id')
        logg.debug('identity policy, user_id is %s', user_id)
        if user_id is None:
            return NoIdentity

        user = request.db_session.query(User).get(user_id)

        if user is None:
            logg.info('user_id %s in session, but not found in the database!', user_id)
            return NoIdentity

        return self.identity_class(user)

    def forget(self, response, request):
        del request.browser_session['user_id']
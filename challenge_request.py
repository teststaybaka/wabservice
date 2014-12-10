from db_utils import *
from models import *
from views import BaseHandler


class Invite(BaseHandler):
    def get(self, challenge_id):
        self.redirect_to(RouteName.DETAIL, challenge_id=challenge_id)

    def post(self, challenge_id):
        current_user = self.check_login_status()
        if current_user is not None:
            current_user_id = current_user.get('id')
            invite(self, challenge_id, current_user_id,
                   self.request.get("friend1"))
        else:
            self.gen_error_page(message=StrConst.NOT_LOGGED_IN)


class Accept(BaseHandler):
    def get(self, request_id):
        challenge_id = accept_request(request_id)
        self.redirect_to(RouteName.DETAIL, challenge_id=challenge_id)


class Reject(BaseHandler):
    def get(self, request_id):
        challenge_id = reject_request(request_id)
        self.redirect_to(RouteName.DETAIL, challenge_id=challenge_id)


class Verify(BaseHandler):
    def get(self, request_id):
        challenge_id = verify_request(request_id)
        self.redirect_to(RouteName.COMPLETIONS, challenge_id=challenge_id)


class Retry(BaseHandler):
    def get(self, request_id):
        challenge_id = retry_request(request_id)
        self.redirect_to(RouteName.COMPLETIONS, challenge_id=challenge_id)


def invite(handler, challenge_id, inviter_id, invitee_id):
    challenge = Challenge.all().filter(
        "challenge_id =", int(challenge_id)).get()
    if challenge is None:
        handler.gen_error_page(message=StrConst.CHALLENGE_NOT_FOUND)
        return

    creator_id = Challenge.all().filter(
        "challenge_id =", int(challenge_id)).get().creator_id

    # user as invitee
    if inviter_id != creator_id:
        verified_request = ChallengeRequest.all() \
            .ancestor(KeyStore.challenge_request_key()) \
            .filter('invitee_id =', inviter_id) \
            .filter('challenge_id =', long(challenge_id)) \
            .filter('status =', RequestStatus.VERIFIED).get()
        if verified_request is not None:
            verified_request.status = RequestStatus.COMPLETED
            verified_request.put()
        else:
            handler.gen_error_page(message=StrConst.INVITE_NOT_AUTHORIZED)
            return

    # user as inviter
    request_key = KeyStore.challenge_request_key()
    request = ChallengeRequest(inviter_id=inviter_id,
                               invitee_id=invitee_id,
                               challenge_id=int(challenge_id),
                               status=RequestStatus.PENDING,
                               parent=request_key)
    request.put()

    request = ChallengeRequest.get_by_id(request.key().id(), request_key)
    if request is None:
        handler.gen_error_page(message=StrConst.INVITE_FAILED)
    else:
        handler.session['message'] = StrConst.INVITE_SUCCESS
        handler.redirect_to(RouteName.DETAIL,
                            challenge_id=challenge_id)


def update_request_status(request_id, status):
    request_key = KeyStore.challenge_request_key()
    request = ChallengeRequest.get_by_id(long(request_id), request_key)
    request.status = status
    request.put()
    return request.challenge_id


def accept_request(request_id):
    return update_request_status(request_id, RequestStatus.ACCEPTED)


def reject_request(request_id):
    return update_request_status(request_id, RequestStatus.REJECTED)


def verify_request(request_id):
    return update_request_status(request_id, RequestStatus.VERIFIED)


def retry_request(request_id):
    return update_request_status(request_id, RequestStatus.ACCEPTED)
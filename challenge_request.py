from db_utils import *
from models import *
from views import BaseHandler


class Invite(BaseHandler):
    def get(self, challenge_id):
        self.redirect_to(RouteName.DETAIL, challenge_id=challenge_id)

    def post(self, challenge_id):
        self.refresh_login_status()
        current_user = self.check_login_status()
        if current_user is not None:
            current_user_id = current_user.get('id')
            invite(self, challenge_id, current_user_id,
                   self.request.POST.getall("friendList"))
        else:
            self.session['message'] = StrConst.NOT_LOGGED_IN
            self.redirect_to(RouteName.DETAIL, challenge_id=challenge_id)


class Accept(BaseHandler):
    def get(self, request_id):
        current_user = self.check_login_status()
        if current_user:
            current_user_id = current_user.get('id')
            request_key = KeyStore.challenge_request_key()
            request = ChallengeRequest.get_by_id(long(request_id), request_key)
            if request is None:
                self.gen_error_page(StrConst.REQUEST_NOT_FOUND)
            else:
                if request.invitee_id != current_user_id:
                    self.gen_error_page(
                        StrConst.REQUEST_NOT_AUTHORIZED.format('accept'))
                else:
                    if request.status == RequestStatus.PENDING or request.status == RequestStatus.REJECTED:
                        request.status = RequestStatus.ACCEPTED
                        request.put()
                    self.redirect_to(RouteName.DETAIL,
                                     challenge_id=request.challenge_id)


class Reject(BaseHandler):
    def get(self, request_id):
        current_user = self.check_login_status()
        if current_user:
            current_user_id = current_user.get('id')
            request_key = KeyStore.challenge_request_key()
            request = ChallengeRequest.get_by_id(long(request_id), request_key)
            if request is None:
                self.gen_error_page(StrConst.REQUEST_NOT_FOUND)
            else:
                if request.invitee_id != current_user_id:
                    self.gen_error_page(
                        StrConst.REQUEST_NOT_AUTHORIZED.format('reject'))
                else:
                    if request.status == RequestStatus.PENDING:
                        request.status = RequestStatus.REJECTED
                        request.put()
                    self.redirect_to(RouteName.DETAIL,
                                     challenge_id=request.challenge_id)


class Verify(BaseHandler):
    def get(self, request_id):
        current_user = self.check_login_status()
        if current_user:
            current_user_id = current_user.get('id')
            request_key = KeyStore.challenge_request_key()
            request = ChallengeRequest.get_by_id(long(request_id), request_key)
            if request is None:
                self.gen_error_page(StrConst.REQUEST_NOT_FOUND)
            else:
                if request.inviter_id != current_user_id:
                    self.gen_error_page(
                        StrConst.REQUEST_NOT_AUTHORIZED.format('verify'))
                else:
                    if request.status == RequestStatus.VERIFYING:
                        request.status = RequestStatus.VERIFIED
                        request.put()
                    self.redirect_to(RouteName.DETAIL,
                                     challenge_id=request.challenge_id)


class Retry(BaseHandler):
    def get(self, request_id):
        current_user = self.check_login_status()
        if current_user:
            current_user_id = current_user.get('id')
            request_key = KeyStore.challenge_request_key()
            request = ChallengeRequest.get_by_id(long(request_id), request_key)
            if request is None:
                self.gen_error_page(StrConst.REQUEST_NOT_FOUND)
            else:
                if request.inviter_id != current_user_id:
                    self.gen_error_page(
                        StrConst.REQUEST_NOT_AUTHORIZED.format('verify'))
                else:
                    if request.status == RequestStatus.VERIFYING:
                        request.status = RequestStatus.ACCEPTED
                        request.put()
                    self.redirect_to(RouteName.DETAIL,
                                     challenge_id=request.challenge_id)


def invite(handler, challenge_id, inviter_id, invitee_id_List):
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
    for invitee_id in invitee_id_List:
        # check if invitee has been invited before
        request = ChallengeRequest.all() \
            .ancestor(KeyStore.challenge_request_key()) \
            .filter('invitee_id =', invitee_id) \
            .filter('challenge_id =', int(challenge_id)).get()

        # add invitee if invitee not invited before
        if request is None:
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

    # all invite success
    handler.session['message'] = StrConst.INVITE_SUCCESS
    handler.redirect_to(RouteName.DETAIL,
                        challenge_id=challenge_id)
from models import *


def challenge_request_key():
    return db.Key.from_path('EntityType', 'ChallengeRequest')


def invite(challenge_id, inviter_id, invitee_id):
    creator_id = Challenge.all().filter(
        "challenge_id =", int(challenge_id)).get().creator_id

    # user as invitee
    if inviter_id != creator_id:
        query = db.GqlQuery(
            "select * from ChallengeRequest where invitee_id=:1 AND challenge_id=:2",
            inviter_id,
            int(challenge_id))
        query_item = query.get()
        if query_item is not None:
            query_item.status = RequestStatus.COMPLETED
            query_item.put()

    # user as inviter
    request_key = challenge_request_key()
    request = ChallengeRequest(inviter_id=inviter_id,
                               invitee_id=invitee_id,
                               challenge_id=int(challenge_id),
                               status=RequestStatus.PENDING,
                               parent=request_key)
    request.put()


def update_request_status(request_id, status):
    request_key = challenge_request_key()
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
    return update_request_status(request_id, RequestStatus.PENDING)
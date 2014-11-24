from models import *


def challenge_request_key():
    return db.Key.from_path('EntityType', 'ChallengeRequest')


def update_request_status(request_id, status):
    request_key = challenge_request_key()
    request = ChallengeRequest.get_by_id(long(request_id), request_key)
    request.status = status
    request.put()
    return request.challenge_id


def accept_request(request_id):
    return update_request_status('accepted')


def reject_request(request_id):
    return update_request_status('rejected')


def verify_request(request_id):
    return update_request_status('verified')


def retry_request(request_id):
    return update_request_status('retry')
from models import *

def challengeRequestKey():
    return db.Key.from_path('EntityType', 'ChallengeRequest')

def acceptRequest(request_id):
    request_key = challengeRequestKey()
    request = ChallengeRequest.get_by_id(long(request_id), request_key)
    request.status = 'accepted'
    request.put()
    return request.challenge_id
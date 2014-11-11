import webapp2
from google.appengine.ext import db

from models import *
from challenge import challengeRequestKey

class Init(webapp2.RequestHandler):
    def get(self):
        query = db.GqlQuery("select * from Challenge_ID_Factory")
        for entry in query.run():
            entry.delete()
        query = db.GqlQuery("select * from Challenge")
        for entry in query.run():
            entry.delete()
        query = db.GqlQuery("SELECT * FROM User")
        for entry in query.run():
            entry.delete()
        query = db.GqlQuery("SELECT * FROM ChallengeRequest")
        for entry in query.run():
            entry.delete()

        challenge_ID_Factory = Challenge_ID_Factory(id_counter=0);
        challenge_ID_Factory.put();

        testUserId = '1498084320443459'

        challenge1 = Challenge(challenge_id=challenge_ID_Factory.get_id(), creator_id=testUserId,
            title='new fb user challenge', summary="It's great", content='try it out!',
            state='ongoing', veri_method='image');
        challenge1.category.append(available_category_list[0]);
        challenge1.put()

        requestKey = challengeRequestKey(testUserId)
        sampleRequest = ChallengeRequest(inviter_id = testUserId, challenge_id = 1, invitee_id = testUserId, status = 'pending', parent = requestKey)
        sampleRequest.put()

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Data initialized.')
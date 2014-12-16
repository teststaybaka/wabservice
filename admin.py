from challenge import *

class Init(webapp2.RequestHandler):
    def get(self):
        query = db.GqlQuery("select * from Challenge_ID_Factory")
        for entry in query.run():
            entry.delete()
        query = db.GqlQuery("select * from Challenge")
        for entry in query.run():
            entry.delete()
        #query = db.GqlQuery("SELECT * FROM User")
        #for entry in query.run():
        #    entry.delete()
        query = db.GqlQuery("SELECT * FROM ChallengeRequest")
        for entry in query.run():
            entry.delete()

        challenge_ID_Factory = get_id_factory()
        challenge_ID_Factory.put();

        testUserId = '1498084320443459'

        challenge1 = Challenge(challenge_id=challenge_ID_Factory.get_id(), creator_id=testUserId,
            title='new fb user challenge', summary="It's great", content='try it out!',
            state='ongoing', parent=KeyStore.challenge_key());
        challenge1.category.append(available_category_list[0]);
        challenge1.put()

        challenge2 = Challenge(challenge_id=challenge_ID_Factory.get_id(), creator_id=testUserId,
            title='Ice Bucket Challenge', summary='Sometimes called the ALS Ice Bucket Challenge, it is an activity involving dumping a bucket of ice water on some\'s head to promote awareness of the disease amyotrophic lateral sclerosis (ALS) and encourage donations to research.',
            content="Within 24 hours of being challenged, participants must record a video of themselves in continuous footage. First, they are to announce their acceptance of the challenge followed by pouring ice into a bucket of water. Then, the bucket is to be lifted and poured over the participant's head. Then the participant can nominate a minimum of three other people to participate in the challenge. Whether people choose to donate, perform the challenge, or do both varies. In one version of the challenge, the participant is expected to donate $10 if they have poured the ice water over their head or donate $100 if they have not. In another version, dumping the ice water over the participant's head is done in lieu of any donation, which has led to some criticisms of the challenge being a form of \"slacktivism\". Many participants donate $100 in addition to doing the challenge.",
            state='ongoing', parent=KeyStore.challenge_key())
        challenge2.category.append(available_category_list[2]);
        challenge2.put()

        requestKey = KeyStore.challenge_request_key()
        # sampleRequest = ChallengeRequest(inviter_id = testUserId, challenge_id = 1, invitee_id = '10152423279882927', status = 'pending', parent = requestKey)
        # sampleRequest = ChallengeRequest(inviter_id = testUserId, challenge_id = 1, invitee_id = '1486877718253752', status = 'accepted', parent = requestKey)
        sampleRequest = ChallengeRequest(inviter_id = testUserId, challenge_id = 1, invitee_id = '741209259295825', status = 'accepted', parent = requestKey)
        sampleRequest.put()

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Data initialized.')

class AddNewEntity(webapp2.RequestHandler):
    def get(self):
        challenge_ID_Factory = db.GqlQuery("select * from Challenge_ID_Factory").get()
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('New entity has been added.')
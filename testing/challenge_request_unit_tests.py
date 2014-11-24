import unittest
from challenge import *
from google.appengine.ext import testbed

class ChallengeRequestUnitTests(unittest.TestCase):
    def setUp(self):
        # initializing app engine test environment
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_app_identity_stub()
        self.testbed.init_datastore_v3_stub()

        # initializing test data
        self.test_user_id1 = '1'
        self.test_user_id2 = '2'
        self.test_challenge_id1 = 2

    def test_accept(self):
        # create a sample request
        request_key = challengeRequestKey()
        sample_request = ChallengeRequest(inviter_id = self.test_user_id1, challenge_id = self.test_challenge_id1, \
                                         invitee_id = self.test_user_id2, status = 'pending', parent = request_key)
        sample_request.put()

        # accept the request
        acceptRequest(sample_request.key().id())

        # re-query the request to make sure we get the updated value, and then verify
        sample_request = ChallengeRequest.get_by_id(long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == 'accepted')

    def tearDown(self):
        self.testbed.deactivate()
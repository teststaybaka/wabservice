import unittest

from gaetestbed import WebTestCase
from google.appengine.ext import testbed
from webapp2_extras.securecookie import SecureCookieSerializer

from challenge import *
from urls import application


class ChallengeRequestUnitTests(unittest.TestCase, WebTestCase):
    APPLICATION = application
    KEY = SECRET_KEY

    def setUp(self):
        # initializing app engine testing environment
        self.cookie_serializer = SecureCookieSerializer(self.KEY)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_app_identity_stub()
        self.testbed.init_datastore_v3_stub()

        # initializing test user data
        self.test_user_id1 = '1'
        self.test_user_id2 = '2'
        self.test_user_id3 = '3'
        self.test_challenge_id1 = 2

        self.test_user_2 = User(
            key_name=self.test_user_id2,
            id=self.test_user_id2,
            name='Test User 2',
            profile_url=' ',
            access_token=' '
        )

        self.challenge_ID_Factory = Challenge_ID_Factory(id_counter=0)

    # TEAM102014-8
    def test_invite(self):
        # create a sample challenge
        sample_challenge_id = self.challenge_ID_Factory.get_id()
        sample_challenge = Challenge(
            challenge_id=sample_challenge_id,
            creator_id=self.test_user_id1,
            title='sample challenge 1',
            summary="It's great",
            content='try it out!',
            state='ongoing',
            veri_method='image')
        sample_challenge.category.append(available_category_list[0])
        sample_challenge.put()

        # create a sample request
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=sample_challenge_id,
            invitee_id=self.test_user_id2,
            status='verified',
            parent=request_key)
        sample_request.put()

        session_user = dict(
            name=self.test_user_2.name,
            profile_url=self.test_user_2.profile_url,
            id=self.test_user_2.id,
            access_token=self.test_user_2.access_token
        )
        session = {"user": session_user}
        serialized = self.cookie_serializer.serialize('session', session)
        headers = {'Cookie': 'session=%s' % serialized}

        self.app.post('/invite/' + str(sample_challenge_id),
                      params={'friend1': self.test_user_id3},
                      headers=headers)

        # get the request created by the invite() call
        request = ChallengeRequest.all().ancestor(request_key) \
            .filter("challenge_id =", sample_challenge_id) \
            .filter("inviter_id =", self.test_user_id2) \
            .filter("invitee_id =", self.test_user_id3) \
            .get()

        # re-query the request to make sure we get the updated status
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)

        self.assertIsNotNone(request)
        self.assertEqual(sample_request.status, 'completed')
        self.assertEqual(request.status, 'pending')

    def test_invite_not_logged_in(self):
        response = self.app.post('/invite/1',
                                 params={'friend1': self.test_user_id1})
        self.assertRedirects(response)

    # TEAM102014-29
    def test_accept(self):
        # create a sample request
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status='pending',
            parent=request_key)
        sample_request.put()

        # accept the request
        self.get(
            '/requests/' + str(sample_request.key().id()) + '/accept')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == 'accepted')

    # TEAM102014-30
    def test_accept_repeated(self):
        # create a sample request that has already been accepted
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status='accepted',
            parent=request_key)
        sample_request.put()

        # accept the request
        self.get(
            '/requests/' + str(sample_request.key().id()) + '/accept')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == 'accepted')

    # TEAM102014-29
    def test_reject(self):
        # create a sample request
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status='pending',
            parent=request_key)
        sample_request.put()

        # reject the request
        self.get(
            '/requests/' + str(sample_request.key().id()) + '/reject')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == 'rejected')

    # TEAM102014-30
    def test_reject_repeated(self):
        # create a sample request that has already been rejected
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status='rejected',
            parent=request_key)
        sample_request.put()

        # reject the request
        self.get(
            '/requests/' + str(sample_request.key().id()) + '/reject')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == 'rejected')

    # TEAM102014-31
    def test_verify(self):
        # create a sample request
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status='pending',
            parent=request_key)
        sample_request.put()

        # confirm the request
        self.get(
            '/requests/' + str(sample_request.key().id()) + '/confirm')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == 'verified')

    # TEAM102014-31
    def test_retry(self):
        # create a sample request
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status='pending',
            parent=request_key)
        sample_request.put()

        # deny the request
        self.get(
            '/requests/' + str(sample_request.key().id()) + '/retry')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == 'pending')

    def tearDown(self):
        self.testbed.deactivate()
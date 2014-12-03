import unittest

from gaetestbed import WebTestCase
from google.appengine.api import files
from google.appengine.ext.blobstore import *
from google.appengine.ext import testbed
from webapp2_extras.securecookie import SecureCookieSerializer

from challenge import *
from const import *
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
        self.testbed.init_files_stub()

        # initializing test user data
        self.test_user_id1 = '1'
        self.test_user_id2 = '2'
        self.test_user_id3 = '3'
        self.test_user_id4 = '4'

        self.test_user_1 = User(
            key_name=self.test_user_id1,
            id=self.test_user_id1,
            name='Test User 1',
            profile_url=' ',
            access_token=' '
        )
        self.test_user_1.put()

        self.test_user_2 = User(
            key_name=self.test_user_id2,
            id=self.test_user_id2,
            name='Test User 2',
            profile_url=' ',
            access_token=' '
        )
        self.test_user_2.put()

        self.test_user_3 = User(
            key_name=self.test_user_id3,
            id=self.test_user_id3,
            name='Test User 3',
            profile_url=' ',
            access_token=' '
        )
        self.test_user_3.put()

        self.test_user_4 = User(
            key_name=self.test_user_id4,
            id=self.test_user_id4,
            name='Test User 4',
            profile_url=' ',
            access_token=' '
        )
        self.test_user_4.put()

        self.challenge_ID_Factory = Challenge_ID_Factory(id_counter=0)
        self.test_challenge_id1 = self.challenge_ID_Factory.get_id()

    def tearDown(self):
        self.testbed.deactivate()


class ChallengeRequestActionsUnitTests(ChallengeRequestUnitTests):
    # TEAM102014-8
    def test_invite(self):
        # create a sample challenge
        sample_challenge = Challenge(
            challenge_id=self.test_challenge_id1,
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
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.VERIFIED,
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

        self.app.post('/invite/' + str(self.test_challenge_id1),
                      params={'friend1': self.test_user_id3},
                      headers=headers)

        # get the request created by the invite() call
        request = ChallengeRequest.all().ancestor(request_key) \
            .filter("challenge_id =", self.test_challenge_id1) \
            .filter("inviter_id =", self.test_user_id2) \
            .filter("invitee_id =", self.test_user_id3) \
            .get()

        # re-query the request to make sure we get the updated status
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)

        self.assertIsNotNone(request)
        self.assertEqual(sample_request.status, RequestStatus.COMPLETED)
        self.assertEqual(request.status, RequestStatus.PENDING)

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
            status=RequestStatus.PENDING,
            parent=request_key)
        sample_request.put()

        # accept the request
        self.get('/requests/' + str(sample_request.key().id()) + '/accept')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == RequestStatus.ACCEPTED)

    # TEAM102014-30
    def test_accept_repeated(self):
        # create a sample request that has already been accepted
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.ACCEPTED,
            parent=request_key)
        sample_request.put()

        # accept the request
        self.get('/requests/' + str(sample_request.key().id()) + '/accept')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == RequestStatus.ACCEPTED)

    # TEAM102014-29
    def test_reject(self):
        # create a sample request
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.PENDING,
            parent=request_key)
        sample_request.put()

        # reject the request
        self.get('/requests/' + str(sample_request.key().id()) + '/reject')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == RequestStatus.REJECTED)

    # TEAM102014-30
    def test_reject_repeated(self):
        # create a sample request that has already been rejected
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.REJECTED,
            parent=request_key)
        sample_request.put()

        # reject the request
        self.get('/requests/' + str(sample_request.key().id()) + '/reject')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == RequestStatus.REJECTED)

    # TEAM102014-31
    def test_verify(self):
        # create a sample request
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.VERIFYING,
            parent=request_key)
        sample_request.put()

        # confirm the request
        self.get('/requests/' + str(sample_request.key().id()) + '/confirm')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == RequestStatus.VERIFIED)

    # TEAM102014-31
    def test_retry(self):
        # create a sample request
        request_key = challenge_request_key()
        sample_request = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.VERIFYING,
            parent=request_key)
        sample_request.put()

        # deny the request
        self.get('/requests/' + str(sample_request.key().id()) + '/retry')

        # re-query the request to make sure we get the updated value and verify
        sample_request = ChallengeRequest.get_by_id(
            long(sample_request.key().id()), request_key)
        self.assertTrue(sample_request.status == RequestStatus.PENDING)


class CompletionsUnitTests(ChallengeRequestUnitTests):
    def setUp(self):
        super(CompletionsUnitTests, self).setUp()

        session_user = dict(
            name=self.test_user_1.name,
            profile_url=self.test_user_1.profile_url,
            id=self.test_user_1.id,
            access_token=self.test_user_1.access_token
        )
        session = {"user": session_user}
        serialized = self.cookie_serializer.serialize('session', session)
        self.headers = {'Cookie': 'session=%s' % serialized}

        # create a sample challenge
        self.sample_challenge = Challenge(
            challenge_id=self.test_challenge_id1,
            creator_id=self.test_user_id1,
            title='sample challenge 1',
            summary="It's great",
            content='try it out!',
            state='ongoing',
            veri_method='image')
        self.sample_challenge.category.append(available_category_list[0])
        self.sample_challenge.put()

        file_name = files.blobstore.create(mime_type='application/octet-stream')
        files.finalize(file_name)
        blob_key = files.blobstore.get_blob_key(file_name)
        self.blob_info = BlobInfo(blob_key)

        request_key = challenge_request_key()
        # create requests with status of ACCEPTED, VERIFYING, VERIFIED,
        # and COMPLETED with current user being the creator
        request1 = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id1,
            status=RequestStatus.ACCEPTED,
            parent=request_key,
            file_info=self.blob_info)
        request1.put()

        request2 = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.VERIFYING,
            parent=request_key,
            file_info=self.blob_info)
        request2.put()

        request3 = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id3,
            status=RequestStatus.VERIFIED,
            parent=request_key,
            file_info=self.blob_info)
        request3.put()

        request4 = ChallengeRequest(
            inviter_id=self.test_user_id1,
            challenge_id=self.test_challenge_id1,
            invitee_id=self.test_user_id4,
            status=RequestStatus.COMPLETED,
            parent=request_key,
            file_info=self.blob_info)
        request4.put()

    def test_completion_creator(self):
        # request the completions page
        response = self.get(
            '/challenge/' + str(self.test_challenge_id1) + '/completions',
            headers=self.headers)

        self.assertNotIn(self.test_user_1.name, response)
        self.assertIn(self.test_user_2.name, response)
        self.assertIn(self.test_user_3.name, response)
        self.assertIn(self.test_user_4.name, response)

    def test_completions_not_creator(self):
        # change the creator of sample challenge
        self.sample_challenge.creator_id = self.test_user_id2
        self.sample_challenge.put()

        # request the completions page
        response = self.get(
            '/challenge/' + str(self.test_challenge_id1) + '/completions',
            headers=self.headers)

        self.assertNotIn(self.test_user_1.name, response)
        self.assertNotIn(self.test_user_2.name, response)
        self.assertIn(self.test_user_3.name, response)
        self.assertIn(self.test_user_4.name, response)

    def tearDown(self):
        super(CompletionsUnitTests, self).setUp()
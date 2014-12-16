from google.appengine.api import files
from google.appengine.ext.blobstore import *

from base_test_case import *


class ChallengeTestCases(BaseTestCase):
    # TEAM102014-28.1
    def test_create(self):
        headers = self.set_session_user(self.test_user_1)
        self.get('/create', headers=headers)

        self.app.post('/create',
                      params={'title': 'title of test case test_create',
                              'summary': 'summary of test case test_create',
                              'content': 'content of test case test_create',
                              'category': 'Public'},
                      headers=headers)

        # check if this challenge appears on the home page
        response = self.get('/')
        self.assertIn('title of test case test_create', response)

        # query the datastore to check if this challenge has been created
        challenge = Challenge.all().filter(
            'title =', 'title of test case test_create').get()
        self.assertIsNotNone(challenge)
        self.assertEqual(
            'content of test case test_create', challenge.content)

    def test_create_two_challenges(self):
        headers = self.set_session_user(self.test_user_1)
        self.app.post('/create',
                      params={'title': 'title of test case test_create',
                              'summary': 'summary of test case test_create',
                              'content': 'content of test case test_create',
                              'category': 'Public'},
                      headers=headers)

        self.app.post('/create',
                      params={'title': 'title 2 of test case test_create',
                              'summary': 'summary 2 of test case test_create',
                              'content': 'content 2 of test case test_create',
                              'category': 'Public'},
                      headers=headers)

        # check if both two challenges appear on the home page
        response = self.get('/')
        self.assertIn('title of test case test_create', response)
        self.assertIn('title 2 of test case test_create', response)

        challenge1 = Challenge.all().filter(
            'title =', 'title of test case test_create').get()
        challenge2 = Challenge.all().filter(
            'title =', 'title 2 of test case test_create').get()
        self.assertNotEqual(challenge1.challenge_id, challenge2.challenge_id)

    # TEAM102014-28.2
    def test_create_missing_fields(self):
        headers = self.set_session_user(self.test_user_1)
        self.get('/create', headers=headers)

        response = self.app.post('/create',
                                 params={'title': '',
                                         'summary': '',
                                         'content': '',
                                         'category': ''},
                                 headers=headers)

        self.assertIn(
            'Some required fields are missing or invalid.', response)

    # TEAM102014-28.3
    def test_create_not_logged_in(self):
        response = self.get('/create')
        self.assertIn(StrConst.NOT_LOGGED_IN, response)

        response = self.app.post('/create')
        self.assertIn(StrConst.NOT_LOGGED_IN, response)

    def test_edit_creator(self):
        headers = self.set_session_user(self.test_user_1)

        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        response = self.get(
            '/challenge/' + str(test_challenge.challenge_id) + '/edit',
            headers=headers)
        self.assertIn(test_challenge.title, response)

        self.app.post(
            '/challenge/' + str(test_challenge.challenge_id) + '/edit',
            params={'title': 'new title of test challenge',
                    'summary': 'new summary of test challenge',
                    'content': 'new content of test challenge',
                    'category': 'Public'},
            headers=headers)

        # visit the detail page of this challenge to check the updated values
        headers = self.set_session_user(self.test_user_2)
        response = self.get('/challenge/' + str(test_challenge.challenge_id),
                            headers=headers)
        self.assertIn('new title of test challenge', response)
        self.assertIn('new content of test challenge', response)

    def test_edit_not_creator(self):
        headers = self.set_session_user(self.test_user_2)

        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        response = self.get(
            '/challenge/' + str(test_challenge.challenge_id) + '/edit',
            headers=headers)
        self.assertRedirects(response)

        response = self.app.post(
            '/challenge/' + str(test_challenge.challenge_id) + '/edit',
            params={'title': 'new title of test challenge',
                    'summary': 'new summary of test challenge',
                    'content': 'new content of test challenge',
                    'category': 'Public'},
            headers=headers)
        self.assertRedirects(response)

    # TEAM102014-67
    def test_edit_missing_fields(self):
        headers = self.set_session_user(self.test_user_1)

        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        response = self.app.post(
            '/challenge/' + str(test_challenge.challenge_id) + '/edit',
            params={'title': '',
                    'summary': '',
                    'content': '',
                    'category': ''},
            headers=headers)
        self.assertIn(
            'Some required fields are missing or invalid.', response)

    # TEAM102014-65.1
    def test_edit_challenge_not_found(self):
        response = self.get('/challenge/1/edit')
        self.assertIn(StrConst.CHALLENGE_NOT_FOUND, response)

        response = self.app.post('/challenge/1/edit')
        self.assertIn(StrConst.CHALLENGE_NOT_FOUND, response)

    # TEAM102014-69.2
    def test_edit_not_logged_in(self):
        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        response = self.get(
            '/challenge/' + str(test_challenge.challenge_id) + '/edit')
        self.assertIn(StrConst.NOT_LOGGED_IN, response)

        response = self.app.post(
            '/challenge/' + str(test_challenge.challenge_id) + '/edit')
        self.assertIn(StrConst.NOT_LOGGED_IN, response)

    # TEAM102014-65.2
    def test_detail_challenge_not_found(self):
        response = self.get('/challenge/1')
        self.assertIn(StrConst.CHALLENGE_NOT_FOUND, response)

    # TEAM102014-69.3
    def test_detail_not_logged_in(self):
        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        response = self.get(
            '/challenge/' + str(test_challenge.challenge_id))
        self.assertIn("Please login to perform any action.", response)


class InviteTestCases(BaseTestCase):
    # TEAM102014-8.1
    def test_invite_no_friend(self):
        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        # create a request to test_user_2 that has been verified
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            challenge_id=test_challenge.challenge_id,
            status=RequestStatus.VERIFIED)

        headers = self.set_session_user(self.test_user_2)

        # test_user_2 sends a invite request with no friend selected
        self.app.post('/invite/' + str(test_challenge.challenge_id),
                      headers=headers)

        # get the request created by the invite() call
        request_key = KeyStore.challenge_request_key()
        created_request = ChallengeRequest.all().ancestor(request_key) \
            .filter("challenge_id =", test_challenge.challenge_id) \
            .filter("inviter_id =", self.test_user_id2) \
            .get()

        self.assertIsNone(created_request)

    # TEAM102014-8.2
    def test_invite(self):
        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        # create a request to test_user_2 that has been verified
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            challenge_id=test_challenge.challenge_id,
            status=RequestStatus.VERIFIED)

        headers = self.set_session_user(self.test_user_2)

        # test_user_2 now invites test_user_3 to the same challenge
        self.app.post('/invite/' + str(test_challenge.challenge_id),
                      params={'friendList': [self.test_user_id3]},
                      headers=headers)

        # get the request created by the invite() call
        request_key = KeyStore.challenge_request_key()
        created_request = ChallengeRequest.all().ancestor(request_key) \
            .filter("challenge_id =", test_challenge.challenge_id) \
            .filter("inviter_id =", self.test_user_id2) \
            .filter("invitee_id =", self.test_user_id3) \
            .get()

        # re-query the first request to make sure we get the updated status
        test_request = ChallengeRequest.get_by_id(
            long(test_request.key().id()), request_key)

        self.assertIsNotNone(created_request)
        self.assertEqual(created_request.status, RequestStatus.PENDING)
        self.assertEqual(test_request.status, RequestStatus.COMPLETED)

        response = self.get('/challenge/' + str(test_request.challenge_id),
                            headers=headers)
        self.assertIn('You may wanna take a look at how others did.', response)

    # TEAM102014-8.3
    def test_invite_multiple_friends(self):
        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        # create a request to test_user_2 that has been verified
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            challenge_id=test_challenge.challenge_id,
            status=RequestStatus.VERIFIED)

        headers = self.set_session_user(self.test_user_2)

        # test_user_2 now invites test_user_3 to the same challenge
        self.app.post('/invite/' + str(test_challenge.challenge_id),
                      params={'friendList':
                                  [self.test_user_id3, self.test_user_id1]},
                      headers=headers)

        # get the request created by the invite() call
        request_key = KeyStore.challenge_request_key()
        created_request_1 = ChallengeRequest.all().ancestor(request_key) \
            .filter("challenge_id =", test_challenge.challenge_id) \
            .filter("inviter_id =", self.test_user_id2) \
            .filter("invitee_id =", self.test_user_id3) \
            .get()

        created_request_2 = ChallengeRequest.all().ancestor(request_key) \
            .filter("challenge_id =", test_challenge.challenge_id) \
            .filter("inviter_id =", self.test_user_id2) \
            .filter("invitee_id =", self.test_user_id1) \
            .get()

        # re-query the first request to make sure we get the updated status
        test_request = ChallengeRequest.get_by_id(
            long(test_request.key().id()), request_key)

        self.assertIsNotNone(created_request_1)
        self.assertEqual(created_request_1.status, RequestStatus.PENDING)
        self.assertIsNotNone(created_request_2)
        self.assertEqual(created_request_2.status, RequestStatus.PENDING)
        self.assertEqual(test_request.status, RequestStatus.COMPLETED)

    # TEAM102014-80.2
    def test_invite_creator(self):
        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        headers = self.set_session_user(self.test_user_1)
        self.app.post('/invite/' + str(test_challenge.challenge_id),
                      params={'friendList': [self.test_user_id2]},
                      headers=headers)

        # get the request created by the invite() call
        request_key = KeyStore.challenge_request_key()
        created_request = ChallengeRequest.all().ancestor(request_key) \
            .filter("challenge_id =", test_challenge.challenge_id) \
            .filter("inviter_id =", self.test_user_id1) \
            .filter("invitee_id =", self.test_user_id2) \
            .get()

        self.assertIsNotNone(created_request)
        self.assertEqual(created_request.status, RequestStatus.PENDING)

    # TEAM102014-80.1
    def test_invite_creator_no_friend_selected(self):
        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        headers = self.set_session_user(self.test_user_1)
        self.app.post('/invite/' + str(test_challenge.challenge_id),
                      params={'friendList': []},
                      headers=headers)

        # get the request created by the invite() call
        request_key = KeyStore.challenge_request_key()
        created_request = ChallengeRequest.all().ancestor(request_key) \
            .filter("challenge_id =", test_challenge.challenge_id) \
            .filter("inviter_id =", self.test_user_id1) \
            .get()

        self.assertIsNone(created_request)

    # TEAM102014-80.3
    def test_invite_creator_multiple_friends(self):
        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        headers = self.set_session_user(self.test_user_1)
        self.app.post('/invite/' + str(test_challenge.challenge_id),
                      params={'friendList':
                                  [self.test_user_id2, self.test_user_id3]},
                      headers=headers)

        # get the request created by the invite() call
        request_key = KeyStore.challenge_request_key()
        created_request_1 = ChallengeRequest.all().ancestor(request_key) \
            .filter("challenge_id =", test_challenge.challenge_id) \
            .filter("inviter_id =", self.test_user_id1) \
            .filter("invitee_id =", self.test_user_id2) \
            .get()

        created_request_2 = ChallengeRequest.all().ancestor(request_key) \
            .filter("challenge_id =", test_challenge.challenge_id) \
            .filter("inviter_id =", self.test_user_id1) \
            .filter("invitee_id =", self.test_user_id3) \
            .get()

        self.assertIsNotNone(created_request_1)
        self.assertEqual(created_request_1.status, RequestStatus.PENDING)
        self.assertIsNotNone(created_request_2)
        self.assertEqual(created_request_2.status, RequestStatus.PENDING)

    # TEAM102014-69.9
    def test_invite_not_authorized(self):
        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        headers = self.set_session_user(self.test_user_2)

        # test_user_2 now invites test_user_3 to the same challenge
        response = self.app.post('/invite/' + str(test_challenge.challenge_id),
                                 params={'friend1': self.test_user_id3},
                                 headers=headers)
        self.assertIn(StrConst.INVITE_NOT_AUTHORIZED, response)

    # TEAM102014-65.3
    def test_invite_challenge_not_found(self):
        headers = self.set_session_user(self.test_user_1)
        response = self.app.post('/invite/1',
                                 params={'friend1': self.test_user_id1},
                                 headers=headers)
        self.assertIn(StrConst.CHALLENGE_NOT_FOUND, response)

    # TEAM102014-69.4
    def test_invite_not_logged_in(self):
        response = self.app.post('/invite/1',
                                 params={'friend1': self.test_user_id1})
        self.assertIn(StrConst.NOT_LOGGED_IN, response)

    def test_invite_get(self):
        response = self.app.get('/invite/1',
                                params={'friend1': self.test_user_id1})
        self.assertRedirects(response)


class CompletionsTestCases(BaseTestCase):
    def setUp(self):
        super(CompletionsTestCases, self).setUp()

        self.test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        self.headers = self.set_session_user(self.test_user_1)

        # create dummy file info
        img_file_name = files.blobstore.create(mime_type='image/png')
        files.finalize(img_file_name)
        img_blob_key = files.blobstore.get_blob_key(img_file_name)
        img_blob_info = BlobInfo(img_blob_key)

        video_file_name = files.blobstore.create(mime_type='video/avi')
        files.finalize(video_file_name)
        video_blob_key = files.blobstore.get_blob_key(video_file_name)
        video_blob_info = BlobInfo(video_blob_key)

        # create requests with status of ACCEPTED, VERIFYING, VERIFIED,
        # and COMPLETED with current user being the creator
        self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id1,
            challenge_id=self.test_challenge.challenge_id,
            status=RequestStatus.ACCEPTED,
            file_info=img_blob_info
        )

        self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            challenge_id=self.test_challenge.challenge_id,
            status=RequestStatus.VERIFYING,
            file_info=img_blob_info
        )

        self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id3,
            challenge_id=self.test_challenge.challenge_id,
            status=RequestStatus.VERIFIED,
            file_info=img_blob_info
        )

        self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id4,
            challenge_id=self.test_challenge.challenge_id,
            status=RequestStatus.COMPLETED,
            file_info=video_blob_info
        )

    def test_completion_creator(self):
        # request the completions page
        response = self.get(
            '/challenge/' + str(self.test_challenge.challenge_id) +
            '/completions', headers=self.headers)

        self.assertNotIn(self.test_user_1.name, response)
        self.assertIn(self.test_user_2.name, response)
        self.assertIn(self.test_user_3.name, response)
        self.assertIn(self.test_user_4.name, response)

    def test_completions_not_creator(self):
        # change the creator of sample challenge
        self.test_challenge.creator_id = self.test_user_id2
        self.test_challenge.put()

        # request the completions page
        response = self.get(
            '/challenge/' + str(self.test_challenge.challenge_id)
            + '/completions', headers=self.headers)

        self.assertNotIn(self.test_user_1.name, response)
        self.assertNotIn(self.test_user_2.name, response)
        self.assertIn(self.test_user_3.name, response)
        self.assertIn(self.test_user_4.name, response)

    # TEAM102014-65.8
    def test_completions_not_found(self):
        response = self.get('/challenge/111/completions')
        self.assertIn(StrConst.CHALLENGE_NOT_FOUND, response)

    def tearDown(self):
        super(CompletionsTestCases, self).tearDown()

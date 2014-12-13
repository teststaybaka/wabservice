import unittest

from gaetestbed import WebTestCase
from google.appengine.api import files
from google.appengine.ext.blobstore import *
from google.appengine.ext import testbed
from webapp2_extras.securecookie import SecureCookieSerializer

from challenge import *
from const import *
from urls import application


class BaseTestCase(unittest.TestCase, WebTestCase):
    """
    Base class of unit test cases for challenge request related classes
    and functions.
    """
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
        self.challenge_ID_Factory.put()

    def tearDown(self):
        self.testbed.deactivate()

    def set_session_user(self, user):
        """
        Set the user variable in current session.

        :param user: the User object to be set as the session's user
        :return: a header that can be added to a request
        """
        session_user = dict(
            name=user.name,
            profile_url=user.profile_url,
            id=user.id,
            access_token=user.access_token
        )
        session = {"user": session_user}
        serialized = self.cookie_serializer.serialize('session', session)
        headers = {'Cookie': 'session=%s' % serialized}
        return headers

    def create_test_challenge(self, creator_id, challenge_id=None):
        """
        Create a test challenge and put it into the test datastore.

        :param creator_id: the user_id of the challenge creator
        :param challenge_id: if None, a id will be generated by the
        challenge_ID_Factory; otherwise, the created challenge will use the
        provide id
        :return: the created challenge.
        """
        if challenge_id is None:
            challenge_id = self.challenge_ID_Factory.get_id()

        test_challenge = Challenge(
            challenge_id=challenge_id,
            creator_id=creator_id,
            title='test challenge ' + str(challenge_id),
            summary="This is the summary of test challenge "
                    + str(challenge_id),
            content="This is the content of test challenge "
                    + str(challenge_id),
            state='ongoing',
            veri_method='image',
            parent=KeyStore.challenge_key())
        test_challenge.category.append(available_category_list[0])
        test_challenge.put()
        return test_challenge

    def create_test_request(self, inviter_id, invitee_id, challenge_id=None,
                            status=RequestStatus.PENDING, file_info=None):
        """
        Create a test challenge request and put it into the test datastore.

        :param inviter_id: the inviter_id of the test request
        :param invitee_id: the invitee_id of the test request
        :param challenge_id: if None, a test challenge will be created with
        creator_id being test_user_id1; otherwise, it will try to find the
        challenge with the provided id; if not found, a new challenge will be
        created with that id.
        :param status: the status of the test request. the default status is
        RequestStatus.PENDING
        :param file_info: if provided, it will be the file_info of the request
        :return: the created challenge request
        """
        if challenge_id is None:
            test_challenge = self.create_test_challenge(self.test_user_id1)
        else:
            test_challenge = Challenge.all()\
                .filter("challenge_id =", challenge_id).get()
            if test_challenge is None:
                test_challenge = self.create_test_challenge(
                    self.test_user_id1, challenge_id)

        request_key = KeyStore.challenge_request_key()
        test_request = ChallengeRequest(
            inviter_id=inviter_id,
            challenge_id=test_challenge.challenge_id,
            invitee_id=invitee_id,
            status=status,
            file_info=file_info,
            parent=request_key)
        test_request.put()
        return test_request


class ChallengeTestCases(BaseTestCase):
    # TEAM102014-28.1
    def test_create(self):
        headers = self.set_session_user(self.test_user_1)
        self.get('/create', headers=headers)

        self.app.post('/create',
                      params={'title': 'title of test case test_create',
                              'summary': 'summary of test case test_create',
                              'content': 'content of test case test_create',
                              'veri_method': 'image',
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
                              'veri_method': 'image',
                              'category': 'Public'},
                      headers=headers)

        self.app.post('/create',
                      params={'title': 'title 2 of test case test_create',
                              'summary': 'summary 2 of test case test_create',
                              'content': 'content 2 of test case test_create',
                              'veri_method': 'image',
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
                                         'veri_method': '',
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
                    'veri_method': 'video',
                    'category': 'Public'},
            headers=headers)

        # visit the detail page of this challenge to check the updated values
        response = self.get('/challenge/' + str(test_challenge.challenge_id))
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
                    'veri_method': 'video',
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
                    'veri_method': 'video',
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
    # TEAM102014-8
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
                      params={'friend1': self.test_user_id3},
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

    def test_invite_creator(self):
        test_challenge = self.create_test_challenge(
            creator_id=self.test_user_id1)

        headers = self.set_session_user(self.test_user_1)
        self.app.post('/invite/' + str(test_challenge.challenge_id),
                      params={'friend1': self.test_user_id2},
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


class ChallengeRequestTestCases(BaseTestCase):
    def template_test(self, action, status=None):
        """
        Test cases for all actions that can be performed on a request.

        :param action: the type of action to be done on the request
        :param status: the initial status of the request. if None, it will be
        RequestStatus.PENDING as default
        """
        # set the pre/post-conditions for the specified action
        start_status = RequestStatus.PENDING
        start_string = ""
        end_status = RequestStatus.PENDING
        end_string = ""
        test_headers = self.set_session_user(self.test_user_1)

        if action == 'accept':
            end_string = "Upload an image or video to verify your success."
            end_status = RequestStatus.ACCEPTED
            test_headers = self.set_session_user(self.test_user_2)
        elif action == 'reject':
            end_string = "Challenge rejected. Reconsider Taking the challenge!"
            end_status = RequestStatus.REJECTED
            test_headers = self.set_session_user(self.test_user_2)
        elif action == 'confirm':
            end_string = "Congratulation! You have completed this challenge."
            start_status = RequestStatus.VERIFYING
            end_status = RequestStatus.VERIFIED
        elif action == 'retry':
            end_string = "Upload an image or video to verify your success."
            start_status = RequestStatus.VERIFYING
            end_status = RequestStatus.ACCEPTED

        if status is not None:
            start_status = status

        if start_status == RequestStatus.PENDING:
            start_string = "You have been challenged. Let's do it!"
        elif start_status == RequestStatus.ACCEPTED:
            start_string = "Upload an image or video to verify your success."
        elif start_status == RequestStatus.REJECTED:
            start_string = \
                "Challenge rejected. Reconsider Taking the challenge!"
        elif start_status == RequestStatus.VERIFYING:
            start_string = "Your application is waiting for verification."

        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            status=start_status)

        headers = self.set_session_user(self.test_user_2)
        # visit the challenge detail page
        response = self.get('/challenge/' + str(test_request.challenge_id),
                            headers=headers)
        self.assertIn(start_string, response)

        self.get('/requests/' + str(test_request.key().id()) + '/' + action,
                 headers=test_headers)

        # re-query the request to make sure we get the updated value and verify
        request_key = KeyStore.challenge_request_key()
        test_request = ChallengeRequest.get_by_id(
            long(test_request.key().id()), request_key)
        self.assertTrue(test_request.status == end_status)

        # re-visit the challenge detail page to see if it is updated correctly
        response = self.get('/challenge/' + str(test_request.challenge_id),
                            headers=headers)
        self.assertIn(end_string, response)

    # TEAM102014-29
    def test_accept(self):
        self.template_test(action='accept')

    # TEAM102014-30
    def test_accept_repeated(self):
        self.template_test(action='accept', status=RequestStatus.ACCEPTED)

    # TEAM102014-69.5
    def test_accept_not_logged_in(self):
        response = self.get('/requests/1/accept')
        self.assertIn(StrConst.NOT_LOGGED_IN, response)

    # TEAM102014-69.10
    def test_accept_not_authorized(self):
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.PENDING)
        headers = self.set_session_user(self.test_user_3)
        response = self.get('/requests/' + str(test_request.key().id())
                            + '/accept', headers=headers)
        self.assertIn(StrConst.REQUEST_NOT_AUTHORIZED.format('accept'),
                      response)

    # TEAM102014-75.1
    def test_accept_wrong_state(self):
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.VERIFYING)
        headers = self.set_session_user(self.test_user_2)
        self.get('/requests/' + str(test_request.key().id()) + '/accept',
                 headers=headers)
        test_request = ChallengeRequest.get_by_id(
            test_request.key().id(),
            KeyStore.challenge_request_key())
        self.assertEqual(test_request.status, RequestStatus.VERIFYING)

    # TEAM102014-65.4
    def test_accept_not_found(self):
        headers = self.set_session_user(self.test_user_1)
        response = self.get('/requests/1/accept', headers=headers)
        self.assertIn(StrConst.REQUEST_NOT_FOUND, response)

    # TEAM102014-29
    def test_reject(self):
        self.template_test(action='reject')

    # TEAM102014-30
    def test_reject_repeated(self):
        self.template_test(action='reject', status=RequestStatus.REJECTED)

    # TEAM102014-69.6
    def test_reject_not_logged_in(self):
        response = self.get('/requests/1/reject')
        self.assertIn(StrConst.NOT_LOGGED_IN, response)

    # TEAM102014-69.11
    def test_reject_not_authorized(self):
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.PENDING)
        headers = self.set_session_user(self.test_user_3)
        response = self.get('/requests/' + str(test_request.key().id())
                            + '/reject', headers=headers)
        self.assertIn(StrConst.REQUEST_NOT_AUTHORIZED.format('reject'),
                      response)

    # TEAM102014-75.2
    def test_reject_wrong_state(self):
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.VERIFYING)
        headers = self.set_session_user(self.test_user_2)
        self.get('/requests/' + str(test_request.key().id()) + '/reject',
                 headers=headers)
        test_request = ChallengeRequest.get_by_id(
            test_request.key().id(),
            KeyStore.challenge_request_key())
        self.assertEqual(test_request.status, RequestStatus.VERIFYING)

    # TEAM102014-65.5
    def test_reject_not_found(self):
        headers = self.set_session_user(self.test_user_1)
        response = self.get('/requests/1/reject', headers=headers)
        self.assertIn(StrConst.REQUEST_NOT_FOUND, response)

    # TEAM102014-31
    def test_verify(self):
        self.template_test(action='confirm')

    # TEAM102014-69.7
    def test_verify_not_logged_in(self):
        response = self.get('/requests/1/confirm')
        self.assertIn(StrConst.NOT_LOGGED_IN, response)

    # TEAM102014-69.12
    def test_verify_not_authorized(self):
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.VERIFYING)
        headers = self.set_session_user(self.test_user_2)
        response = self.get('/requests/' + str(test_request.key().id())
                            + '/confirm', headers=headers)
        self.assertIn(StrConst.REQUEST_NOT_AUTHORIZED.format('verify'),
                      response)

    # TEAM102014-75.3
    def test_verify_wrong_state(self):
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.PENDING)
        headers = self.set_session_user(self.test_user_1)
        self.get('/requests/' + str(test_request.key().id()) + '/confirm',
                 headers=headers)
        test_request = ChallengeRequest.get_by_id(
            test_request.key().id(),
            KeyStore.challenge_request_key())
        self.assertEqual(test_request.status, RequestStatus.PENDING)

    # TEAM102014-65.6
    def test_verify_not_found(self):
        headers = self.set_session_user(self.test_user_1)
        response = self.get('/requests/1/confirm', headers=headers)
        self.assertIn(StrConst.REQUEST_NOT_FOUND, response)

    # TEAM102014-31
    def test_retry(self):
        self.template_test(action='retry')

    # TEAM102014-69.8
    def test_retry_not_logged_in(self):
        response = self.get('/requests/1/retry')
        self.assertIn(StrConst.NOT_LOGGED_IN, response)

    # TEAM102014-69.13
    def test_retry_not_authorized(self):
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.VERIFYING)
        headers = self.set_session_user(self.test_user_2)
        response = self.get('/requests/' + str(test_request.key().id())
                            + '/retry', headers=headers)
        self.assertIn(StrConst.REQUEST_NOT_AUTHORIZED.format('verify'),
                      response)

    # TEAM102014-75.4
    def test_retry_wrong_state(self):
        test_request = self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            status=RequestStatus.PENDING)
        headers = self.set_session_user(self.test_user_1)
        self.get('/requests/' + str(test_request.key().id()) + '/retry',
                 headers=headers)
        test_request = ChallengeRequest.get_by_id(
            test_request.key().id(),
            KeyStore.challenge_request_key())
        self.assertEqual(test_request.status, RequestStatus.PENDING)

    # TEAM102014-65.7
    def test_retry_not_found(self):
        headers = self.set_session_user(self.test_user_1)
        response = self.get('/requests/1/retry', headers=headers)
        self.assertIn(StrConst.REQUEST_NOT_FOUND, response)


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
        super(CompletionsTestCases, self).setUp()
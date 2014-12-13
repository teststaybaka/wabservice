import unittest

from gaetestbed import WebTestCase
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
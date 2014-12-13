from base_test_case import *


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
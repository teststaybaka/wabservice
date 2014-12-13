from base_test_case import *


class AccountTestCases(BaseTestCase):
    # TEAM102014-12.1
    def test_history(self):
        headers = self.set_session_user(self.test_user_1)
        created_challenge = self.create_test_challenge(self.test_user_id1)
        invited_challenge = self.create_test_challenge(self.test_user_id2)
        self.create_test_request(
            inviter_id=self.test_user_id2,
            invitee_id=self.test_user_id1,
            challenge_id=invited_challenge.challenge_id)
        self.create_test_request(
            inviter_id=self.test_user_id1,
            invitee_id=self.test_user_id2,
            challenge_id=created_challenge.challenge_id)

        response = self.get('/history', headers=headers)
        self.assertIn('You are invited to the challenge <a href="/challenge/'
                      + str(invited_challenge.challenge_id) + '">'
                      + invited_challenge.title + '</a> invited by '
                      + self.test_user_2.name,
                      response)
        self.assertIn('You invited ' + self.test_user_2.name
                      + ' to the challenge <a href="/challenge/'
                      + str(created_challenge.challenge_id) + '">'
                      + created_challenge.title + '</a>',
                      response)
        self.assertIn('You created the challenge <a href="/challenge/'
                      + str(created_challenge.challenge_id) + '">'
                      + created_challenge.title + '</a>',
                      response)

    # TEAM102014-12.2
    def test_history_not_logged_in(self):
        response = self.get('/history')
        self.assertIn(StrConst.NOT_LOGGED_IN, response)
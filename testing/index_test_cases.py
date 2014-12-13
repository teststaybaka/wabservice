from base_test_case import *


class IndexTestCases(BaseTestCase):
    # TEAM102014-20.1
    def test_index_no_challenge(self):
        response = self.get('/')
        self.assertNotIn('class="per-challenge"', response)

    # TEAM102014-20.2
    def test_index_has_challenges(self):
        challenge1 = self.create_test_challenge(self.test_user_id1)
        challenge2 = self.create_test_challenge(self.test_user_id2)
        challenge3 = self.create_test_challenge(self.test_user_id3)

        response = self.get('/')
        self.assertIn(challenge1.title, response)
        self.assertIn(challenge1.summary, response)
        self.assertIn(challenge2.title, response)
        self.assertIn(challenge2.summary, response)
        self.assertIn(challenge3.title, response)
        self.assertIn(challenge3.summary, response)

    # TEAM102014-20.3
    def test_index_search(self):
        challenge1 = self.create_test_challenge(self.test_user_id1)
        challenge1.title = 'Title 1 with keyword'
        challenge1.put()
        challenge2 = self.create_test_challenge(self.test_user_id2)
        challenge2.title = 'Title 2 with keyword'
        challenge2.put()
        challenge3 = self.create_test_challenge(self.test_user_id3)

        response = self.get('/', params={'keyword': 'keyword'})
        self.assertIn(challenge1.title, response)
        self.assertIn(challenge1.summary, response)
        self.assertIn(challenge2.title, response)
        self.assertIn(challenge2.summary, response)
        self.assertNotIn(challenge3.title, response)
        self.assertNotIn(challenge3.summary, response)

    # TEAM102014-20.4
    def test_index_empty_search(self):
        challenge1 = self.create_test_challenge(self.test_user_id1)
        challenge2 = self.create_test_challenge(self.test_user_id2)
        challenge3 = self.create_test_challenge(self.test_user_id3)

        response = self.get('/', params={'keyword': 'keyword'})
        self.assertNotIn(challenge1.title, response)
        self.assertNotIn(challenge1.summary, response)
        self.assertNotIn(challenge2.title, response)
        self.assertNotIn(challenge2.summary, response)
        self.assertNotIn(challenge3.title, response)
        self.assertNotIn(challenge3.summary, response)

    # TEAM102014-20.5
    def test_index_category(self):
        challenge1 = self.create_test_challenge(self.test_user_id1)
        challenge1.category = [available_category_list[0],
                               available_category_list[1]]
        challenge1.put()
        challenge2 = self.create_test_challenge(self.test_user_id2)
        challenge2.category = [available_category_list[0],
                               available_category_list[2]]
        challenge2.put()
        challenge3 = self.create_test_challenge(self.test_user_id3)
        challenge3.category = [available_category_list[1],
                               available_category_list[2]]
        challenge3.put()

        response = self.get(
            '/', params={'now_category': available_category_list[1]})
        self.assertIn(challenge1.title, response)
        self.assertIn(challenge1.summary, response)
        self.assertNotIn(challenge2.title, response)
        self.assertNotIn(challenge2.summary, response)
        self.assertIn(challenge3.title, response)
        self.assertIn(challenge3.summary, response)

    # TEAM102014-20.6
    def test_index_category_empty(self):
        challenge1 = self.create_test_challenge(self.test_user_id1)
        challenge1.category = [available_category_list[0],
                               available_category_list[1]]
        challenge1.put()
        challenge2 = self.create_test_challenge(self.test_user_id2)
        challenge2.category = [available_category_list[0],
                               available_category_list[0]]
        challenge2.put()
        challenge3 = self.create_test_challenge(self.test_user_id3)
        challenge3.category = [available_category_list[1],
                               available_category_list[1]]
        challenge3.put()

        response = self.get(
            '/', params={'now_category': available_category_list[2]})
        self.assertNotIn(challenge1.title, response)
        self.assertNotIn(challenge1.summary, response)
        self.assertNotIn(challenge2.title, response)
        self.assertNotIn(challenge2.summary, response)
        self.assertNotIn(challenge3.title, response)
        self.assertNotIn(challenge3.summary, response)

    # TEAM102014-20.7
    def test_index_keyword_and_category(self):
        challenge1 = self.create_test_challenge(self.test_user_id1)
        challenge1.title = 'Title 1 with keyword'
        challenge1.category = [available_category_list[0],
                               available_category_list[1]]
        challenge1.put()
        challenge2 = self.create_test_challenge(self.test_user_id2)
        challenge2.category = [available_category_list[0],
                               available_category_list[2]]
        challenge2.put()
        challenge3 = self.create_test_challenge(self.test_user_id3)
        challenge3.title = 'Title 3 with keyword'
        challenge3.category = [available_category_list[1],
                               available_category_list[2]]
        challenge3.put()

        response = self.get('/', params={
            'keyword': 'keyword',
            'now_category': available_category_list[0]})
        self.assertIn(challenge1.title, response)
        self.assertIn(challenge1.summary, response)
        self.assertNotIn(challenge2.title, response)
        self.assertNotIn(challenge2.summary, response)
        self.assertNotIn(challenge3.title, response)
        self.assertNotIn(challenge3.summary, response)
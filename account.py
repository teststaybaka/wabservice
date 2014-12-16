from views import *
from db_utils import KeyStore

class History(BaseHandler):
    def get(self):
        current_user = self.check_login_status()
        if current_user:
            challenge_key = KeyStore.challenge_key()
            challenge_request_key = KeyStore.challenge_request_key()

            requests = ChallengeRequest.all().ancestor(challenge_request_key)\
                .filter('invitee_id =', current_user.get('id')).fetch(None)
            invited_list = []
            for request in requests:
                query = db.GqlQuery(
                    'select * from Challenge where challenge_id = :1',
                    request.challenge_id)
                challenge = query.get()
                query = db.GqlQuery('select * from User where id = :1',
                                    request.inviter_id)
                inviter = query.get()
                invited_list.append({'challenge_id':challenge.challenge_id,
                                     'challenge_title': challenge.title,
                                     'status': request.status,
                                     'inviter': inviter})
            
            requests = ChallengeRequest.all().ancestor(challenge_request_key)\
                .filter('inviter_id =', current_user.get('id')).fetch(None)
            inviting_list = []
            for request in requests:
                query = db.GqlQuery(
                    'select * from Challenge where challenge_id = :1',
                    request.challenge_id)
                challenge = query.get()
                query = db.GqlQuery('select * from User where id = :1',
                                    request.invitee_id)
                invitee = query.get()
                inviting_list.append({'challenge_id':challenge.challenge_id,
                                      'challenge_title':challenge.title,
                                      'status': request.status,
                                      'invitee': invitee})

            created_list = []
            challenges = Challenge.all().ancestor(challenge_key).filter(
                'creator_id =', current_user.get('id')).fetch(None)
            for challenge in challenges:
                created_list.append({'challenge_id': challenge.challenge_id,
                                     'challenge_title': challenge.title})

            category = self.request.get("category", default_value='all')
            if category != 'all':
                if category != 'created':
                    created_list = []
                if category != 'invited':
                    invited_list = []
                if category != 'inviting':
                    inviting_list = []

            context = {'dialog': 'Hello ' + current_user.get('name') +
                                 '. Check out how you\'ve done.',
                       'invited_list': invited_list,
                       'inviting_list': inviting_list,
                       'created_list': created_list}
            template = env.get_template('template/history.html')
            self.response.write(template.render(context))


class LoginStatusChange(BaseHandler):
    def get(self, pre_page):
        self.refresh_login_status()
        if self.current_user:
            self.response.set_cookie('status', 'login', path='/')
        else:
            self.response.set_cookie('status', 'logout', path='/')
        if len(pre_page) != 0:
            pre_page = pre_page[0:-1]
        logging.info(pre_page)
        self.redirect('/'+pre_page)
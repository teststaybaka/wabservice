from views import *

class TestFacebook(BaseHandler):
    def get(self):
        logging.info(self.current_user)
        context = {}
        template = env.get_template('template/facebook_login_test.html')
        self.response.write(template.render(context))
        # if self.session.get("user"):
        #     self.response.headers['Content-Type'] = 'text/plain'
        #     self.response.write(self.session.get("user").get("name")+" "+self.session.get("user").get("id"))
        #     logging.info(self.session.get("user"))
        # else:
        #     cookie = facebook.get_user_from_cookie(self.request.cookies,
        #                                            FACEBOOK_APP_ID,
        #                                            FACEBOOK_APP_SECRET)
        #     logging.info(cookie)
        #     if cookie:
        #         # user = User.get_by_key_name(cookie["uid"])
        #         # self.session["user"] = dict(
        #         #     name=user.name,
        #         #     profile_url=user.profile_url,
        #         #     id=user.id,
        #         #     access_token=user.access_token)
        #         # logging.info("logged in");
        #         graph = facebook.GraphAPI(cookie["access_token"])
        #         profile = graph.get_object("me")
        #         self.session["user"] = dict(
        #             key_name=str(profile["id"]),
        #             id=str(profile["id"]),
        #             name=profile["name"],
        #             profile_url=profile["link"],
        #             access_token=cookie["access_token"]
        #         )
        #         logging.info(self.session.get("user"))
        #     else:
        #         context = {}
        #         template = env.get_template('template/facebook_login_test.html')
        #         self.response.write(template.render(context))
        # if self.session.get("user"):
        #     self.response.headers['Content-Type'] = 'text/plain'
        #     self.response.write(self.session.get("user"))
        # else:
        #     self.response.headers['Content-Type'] = 'text/plain'
        #     self.response.write('hellow')
        #     self.session["user"] = 'this is a user'

class Account(BaseHandler):
    def get(self):
        current_user = self.current_user
        if current_user:
            context = {'dialog': 'Hello '+current_user.get('name')+'. Check out how you\'ve done.'}
            template = env.get_template('template/account_base.html')
            self.response.write(template.render(context))
        else:
            self.redirect_to('home')

class Inbox(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class History(BaseHandler):
    def get(self):
        current_user = self.current_user
        if current_user:
            user = User.get_by_key_name(current_user.get("id"))
            logging.info(user.name)
            # challenge_list = []
            # for userChallenge in user.challenges:
            #     challenge_list.append(userChallenge.challenge)
            requests = ChallengeRequest.all().filter('invitee_id =', current_user.get('id')).fetch(None);

            context = {'dialog': 'Hello '+current_user.get('name')+'. Check out how you\'ve done.', 'requests': requests}
            template = env.get_template('template/account_history.html')
            self.response.write(template.render(context))
        else:
            self.redirect_to('home')

class LoginStatusChange(BaseHandler):
    #todo: rediret to the page before login
    def get(self, pre_page):
        self.check_status()
        if self.current_user:
            self.response.set_cookie('status', 'login', path='/')
        else:
            self.response.set_cookie('status', 'logout', path='/')
        if len(pre_page) != 0:
            pre_page = pre_page[0:-1]
        logging.info(pre_page)
        self.redirect('/'+pre_page)

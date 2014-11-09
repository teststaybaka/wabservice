import cgi
import urllib
import os
import logging
import jinja2
import webapp2
import facebook
from webapp2_extras import sessions
from jinja2 import Undefined
from google.appengine.ext import db

from models import *

FACEBOOK_APP_ID = '797761393603664'
FACEBOOK_APP_SECRET = 'd95c7c45b86a757f44b7c4991a0b7f47'

class SilentUndefined(Undefined):
    '''
    Dont break pageloads because vars arent there!
    '''
    def _fail_with_undefined_error(self, *args, **kwargs):
        logging.exception('JINJA2: something was undefined!')
        return None

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
    undefined=SilentUndefined)
env.globals = {
    'uri_for': webapp2.uri_for,
}

class BaseHandler(webapp2.RequestHandler):
    @property
    def current_user(self):
        cookie = facebook.get_user_from_cookie(self.request.cookies,
                                                   FACEBOOK_APP_ID,
                                                   FACEBOOK_APP_SECRET)
        logging.info(cookie)
        if cookie:
            user = User.get_by_key_name(cookie["uid"])
            if not user:
                logging.info("not existing")
                # Not an existing user so get user info
                graph = facebook.GraphAPI(cookie["access_token"])
                profile = graph.get_object("me")
                user = User(
                    key_name=str(profile["id"]),
                    id=str(profile["id"]),
                    name=profile["name"],
                    profile_url=profile["link"],
                    access_token=cookie["access_token"]
                )
                user.put()
            elif user.access_token != cookie["access_token"]:
                user.access_token = cookie["access_token"]
                user.put()
            
            self.session["user"] = dict(
                name=user.name,
                profile_url=user.profile_url,
                id=user.id,
                access_token=user.access_token
            )
            return self.session.get("user")
        else:
            return None

    def dispatch(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
<<<<<<< HEAD
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        return self.session_store.get_session()

class Home(BaseHandler):
    def one_time_runing(self, challenge_ID_Factory):
        # challenge_ID_Factory = Challenge_ID_Factory(id_counter=0);
        # challenge_ID_Factory.put();

        # query = db.GqlQuery("select * from Challenge")
        # for entry in query.run():
        #     entry.delete()

        # challenge1 = Challenge(challenge_id=challenge_ID_Factory.get_id(), 
        #     title='new challenge', summary="It's great", content='try it out!',
        #     state='ongoing', veri_method='image');
        # challenge1.category.append(available_category_list[0]);
        # challenge1.put();
        # challenge2 = Challenge(challenge_id=challenge_ID_Factory.get_id(), 
        #     title='Another one?', summary="It's great", content='really!',
        #     state='closed', veri_method='both');
        # challenge2.category.append(available_category_list[3]);
        # challenge2.put();
        user = User.get_by_key_name(u'1498084320443459')
        challenge = db.GqlQuery("select * from Challenge where challenge_id = :1 ", 1).get()
        UserChallenge(user=user, challenge=challenge, relationship='accepted').put()


    def get_id_factory(self):
=======
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class TestSignin(BaseHandler):
    def get(self):
        logging.info(self.session)
        if self.session.get('id'):
            self.response.write('Already Logged in! go back to <a href="/">Home</a>')
        else:
            self.session['id'] = 'testuserid1'
            self.session['username'] = 'testuser1'
            self.response.write('Login Success! go back to <a href="/">Home</a>')

class TestLogout(BaseHandler):
    def get(self):
        logging.info(self.session)
        if self.session.get('id'):
            self.session.pop('id')
            if self.session.get('username'):
                self.session.pop('username')
            self.response.write('Logout Success! go back to <a href="/">Home</a>')
        else:
            self.response.write('You are not logged in! go back to <a href="/">Home</a>')

class Home(BaseHandler):
    def one_time_runing(self):

>>>>>>> a848072ed8d73e16e84bed4283256038dce3fedf
        query = db.GqlQuery("select * from Challenge_ID_Factory")
        for entry in query.run():
            entry.delete()
        query = db.GqlQuery("select * from Challenge")
        for entry in query.run():
            entry.delete()
        query = db.GqlQuery("SELECT * FROM User")
        for entry in query.run():
            entry.delete()

        challenge_ID_Factory = Challenge_ID_Factory(id_counter=0);
        challenge_ID_Factory.put();

        user1 = User(
            id = 'testuserid1',
            name = 'testuser1',
            profile_url = '/images/user1profile.jpg',
            access_token = 'user1token')
        user1.put()

        user2 = User(
            id = 'testuserid2',
            name = 'testuser2',
            profile_url = '/images/user2profile.jpg',
            access_token = 'user2token')
        user2.put()
        
        challenge1 = Challenge(challenge_id=challenge_ID_Factory.get_id(), creator_id='testuserid1',
            title='new challenge', summary="It's great", content='try it out!',
            state='ongoing', veri_method='image');
        challenge1.category.append(available_category_list[0]);
        challenge1.put();
        challenge2 = Challenge(challenge_id=challenge_ID_Factory.get_id(), creator_id='testuserid2',
            title='Another one?', summary="It's great", content='really!',
            state='closed', veri_method='both');
        challenge2.category.append(available_category_list[3]);
        challenge2.put();

    # def get_id_factory(self):
    #     query = db.GqlQuery("select * from Challenge_ID_Factory")
    #     for entry in query.run():
    #         return entry

    def get_challenges(self, filters = None):
        query = db.GqlQuery("select * from Challenge")
        challenge_list = []
        for entry in query.run():
            challenge_list.append(entry);
            logging.info("category: %s\n", entry.category)
        return challenge_list

    def get(self):
<<<<<<< HEAD
        challenge_ID_Factory = self.get_id_factory();
        # logging.info("id counter: %d", challenge_ID_Factory.id_counter);
        # self.one_time_runing(challenge_ID_Factory)
=======
        # logging.info(self.request)
        # challenge_ID_Factory = self.get_id_factory();
        # logging.info("id counter: %d", challenge_ID_Factory.id_counter);
        # self.one_time_runing()
>>>>>>> a848072ed8d73e16e84bed4283256038dce3fedf

        now_category = 'for fun'
        category_list = available_category_list
        challenge_list = self.get_challenges()
        dialog = 'Hello there. Welcome.'
        # add username
        context = { 'username': self.session.get('username'), 'dialog': dialog, 'category_list': category_list, 'challenge_list': challenge_list, 'now_category': now_category}
        template = env.get_template('template/index.html')
        self.response.write(template.render(context))

<<<<<<< HEAD
    def home_info(self, status):
        if int(status) == 1 and not self.current_user:
            now_category = 'for fun'
            category_list = available_category_list
            query = db.GqlQuery("select * from Challenge")
            challenge_list = self.get_challenges()
            dialog = 'You need to log in!'
            context = { 'username': '', 'dialog': dialog, 'category_list': category_list, 'challenge_list': challenge_list, 'now_category': now_category, 'warning':'warning'}
            template = env.get_template('template/index.html')
            self.response.write(template.render(context))
        else:
            self.redirect(webapp2.uri_for('home'))

class Invite(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Detail(webapp2.RequestHandler):
    def get(self, challenge_id):
        now_category = 'for fun'
        # logging.info("%s %s", challenge_id, type(challenge_id))
        query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        for entry in query.run():
            challenge = entry
        dialog = 'Hello there. Welcome.'
        context = { 'state': 1, 'creator': 'creator', 'username': '', 'dialog': dialog, 'now_category': now_category, 'challenge': challenge, 'intro_active': 1}
        template = env.get_template('template/detail.html')
        self.response.write(template.render(context))

class Accept(webapp2.RequestHandler):
    def get(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Reject(webapp2.RequestHandler):
    def get(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')
=======
>>>>>>> a848072ed8d73e16e84bed4283256038dce3fedf

class Completions(webapp2.RequestHandler):
    def get(self, challenge_id):
        now_category = 'for fun'
        # logging.info("%s %s", challenge_id, type(challenge_id))
        query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        for entry in query.run():
            challenge = entry
        dialog = 'How is it going?'
        context = { 'dialog': dialog, 'now_category': now_category, 'challenge': challenge, 'completion_active': 1}
        template = env.get_template('template/detail.html')
        self.response.write(template.render(context))

class Discussions(webapp2.RequestHandler):
    def get(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class ServeFile(webapp2.RequestHandler):
    def get(self, file_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Create(BaseHandler):
    def get(self):
        if self.current_user:
            context = {'dialog': 'You got a good idea?', 'now_category': 'create'}
            template = env.get_template('template/create.html')
            self.response.write(template.render(context))
        else:
            self.redirect(webapp2.uri_for('home_info', status=1))

    # def post(self):

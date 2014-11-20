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
from google.appengine.ext.webapp import blobstore_handlers

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
    def check_status(self):
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
            if self.session.get('user'):
                self.session.pop('user')
            return None

    @property
    def current_user(self):
        return self.session.get('user')
        # if self.session.get('user'):
        #     return self.session.get('user')
        # else:
        #     return None
            # return self.check_status();

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
        return db.GqlQuery("select * from Challenge_ID_Factory").get()

    def get_challenges(self, filters = None):
        query = db.GqlQuery("select * from Challenge")
        challenge_list = []
        for entry in query.run():
            challenge_list.append(entry);
            logging.info("category: %s\n", entry.category)
        return challenge_list

    def get(self):
        challenge_ID_Factory = self.get_id_factory();
        # logging.info("id counter: %d", challenge_ID_Factory.id_counter);

        now_category = 'for fun'
        category_list = available_category_list
        challenge_list = self.get_challenges()
        dialog = 'Hello there. Welcome.'
        context = { 'username': '', 'dialog': dialog, 'category_list': category_list, 'challenge_list': challenge_list, 'now_category': now_category}
        template = env.get_template('template/index.html')
        self.response.write(template.render(context))

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

import cgi
import urllib
import os
import logging
import jinja2
import webapp2
from jinja2 import Undefined
from google.appengine.ext import db

from models import *

from webapp2_extras import sessions

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

# Probably should use auth module for login?
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
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

    def get(self):
        # logging.info(self.request)
        # challenge_ID_Factory = self.get_id_factory();
        # logging.info("id counter: %d", challenge_ID_Factory.id_counter);
        # self.one_time_runing()

        now_category = 'for fun'
        category_list = available_category_list
        query = db.GqlQuery("select * from Challenge")
        challenge_list = []
        for entry in query.run():
            challenge_list.append(entry);
            logging.info("category: %s\n", entry.category)
        dialog = 'Hello there. Welcome.'
        # add username
        context = { 'username': self.session.get('username'), 'dialog': dialog, 'category_list': category_list, 'challenge_list': challenge_list, 'now_category': now_category}
        template = env.get_template('template/index.html')
        self.response.write(template.render(context))


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

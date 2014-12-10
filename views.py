import facebook
import jinja2
import logging
import os
import sys
import traceback
import webapp2

from jinja2 import Undefined
from webapp2_extras import sessions

from models import *


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
    def message(self):
        if self.session.get('message'):
            words = self.session.get('message')
            self.session.pop('message')
            return words
        else:
            if self.current_user:
                words = 'Hello '+self.current_user.get('name')+'.'
            else:
                words = 'Hello there.'
            words += ' Welcome! Here you can see challenges all over the world. Take one that is challenging you!'
            return words

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

    def handle_exception(self, exception, debug):
        gen_error_page(self, exception=exception)

class Home(BaseHandler):
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

        now_category = 'for fun'
        category_list = available_category_list
        challenge_list = self.get_challenges()
        context = {
            'category_list': category_list,
            'challenge_list': challenge_list,
            'now_category': now_category,
            'dialog': self.message}
        template = env.get_template('template/index.html')
        self.response.write(template.render(context))


class Discussions(webapp2.RequestHandler):
    def get(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


def gen_error_page(handler, message=None, redirect_url=None, exception=None):
    template = env.get_template('template/error.html')

    if message is None:
        message = "An unexpected error has occurred."
    if redirect_url is None:
        redirect_url = webapp2.uri_for(RouteName.HOME)
    if exception is not None:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        exc_desc_lines = \
            traceback.format_exception(exc_type, exc_value, exc_traceback)
    else:
        exc_desc_lines = None

    context = {'redirect_url': redirect_url,
               'message': message,
               'exc_desc': exc_desc_lines}
    handler.response.write(template.render(context))
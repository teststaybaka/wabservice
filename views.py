import cgi
import urllib
import os
import logging
import jinja2
import webapp2
from jinja2 import Undefined
from google.appengine.ext import db

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

class Home(webapp2.RequestHandler):
    # def one_time_runing(self, challenge_ID_Factory):
    #     challenge_ID_Factory = Challenge_ID_Factory(id_counter=0);
    #     challenge_ID_Factory.put();

    #     query = db.GqlQuery("select * from Challenge")
    #     for entry in query.run():
    #         entry.delete()

    #     challenge1 = Challenge(challenge_id=challenge_ID_Factory.get_id(), 
    #         title='new challenge', summary="It's great", content='try it out!',
    #         state='ongoing', veri_method='image');
    #     challenge1.category.append(available_category_list[0]);
    #     challenge1.put();
    #     challenge2 = Challenge(challenge_id=challenge_ID_Factory.get_id(), 
    #         title='Another one?', summary="It's great", content='really!',
    #         state='closed', veri_method='both');
    #     challenge2.category.append(available_category_list[3]);
    #     challenge2.put();

    def get_id_factory(self):
        query = db.GqlQuery("select * from Challenge_ID_Factory")
        for entry in query.run():
            return entry

    def get(self):
        challenge_ID_Factory = self.get_id_factory();
        logging.info("id counter: %d", challenge_ID_Factory.id_counter);
        # self.one_time_runing(challenge_ID_Factory)

        now_category = 'for fun'
        category_list = available_category_list
        query = db.GqlQuery("select * from Challenge")
        challenge_list = []
        for entry in query.run():
            challenge_list.append(entry);
            logging.info("category: %s\n", entry.category)
        dialog = 'Hello there. Welcome.'
        context = { 'username': '', 'dialog': dialog, 'category_list': category_list, 'challenge_list': challenge_list, 'now_category': now_category}
        template = env.get_template('template/index.html')
        self.response.write(template.render(context))

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

class Create(webapp2.RequestHandler):
    def get(self):
        context = {'dialog': 'You got a good idea?', 'now_category': 'create'}
        template = env.get_template('template/create.html')
        self.response.write(template.render(context))

    # def post(self):

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

class Upload(webapp2.RequestHandler):
    def post(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Confirm(webapp2.RequestHandler):
    def get(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class ServeFile(webapp2.RequestHandler):
    def get(self, file_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

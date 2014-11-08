import cgi
import urllib
import logging
from google.appengine.ext import db
import webapp2
import jinja2

from models import *
from views import env

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
class Edit(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')
    
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Invite(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Accept(webapp2.RequestHandler):
    def get(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Reject(webapp2.RequestHandler):
    def get(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Upload(webapp2.RequestHandler):
    def post(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Verify(webapp2.RequestHandler):
    def get(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')
import cgi
import urllib
import logging
from google.appengine.ext import db
import webapp2
import jinja2

from models import *
from views import env

from views import BaseHandler

class Create(BaseHandler):
    def get(self):
        context = {'username': self.session['username'], 'dialog': 'You got a good idea?', 'now_category': 'create'}
        template = env.get_template('template/create.html')
        self.response.write(template.render(context))

    def post(self):
        # Naive creation with no scrutiny
        challenge_ID_Factory = db.GqlQuery("select * from Challenge_ID_Factory").get()
        challenge = Challenge(
            challenge_id      = challenge_ID_Factory.get_id(),
            creator_id        = self.session['id'],
            title             = self.request.POST.get('title'), 
            summary           = self.request.POST.get('summary'), 
            content           = self.request.POST.get('content'),
            state             = 'ongoing', 
            veri_method       = self.request.POST.get('veri_method'),
            category          = [self.request.POST.get('category')],
            completion_counts = 0,
            accept_counts     = 0,
            );
        logging.info(challenge.challenge_id)
        challenge.put();
        url = '/challenge/' + str(challenge.challenge_id)
        logging.info(url)
        # The page may not show challenge info directly since db needs time to write data, better to set up a delay before redirection
        self.redirect(url)


class Edit(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')
    
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

#########################################################################################
# Work split here, as I mentioned on Friday
#########################################################################################

class Detail(webapp2.RequestHandler):
    def get(self, challenge_id):
        now_category = 'for fun'
        # logging.info("%s %s", challenge_id, type(challenge_id))
        query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        challenge = query.get()
        if challenge is not None:
            dialog = 'Hello there. Welcome.'
            context = { 'state': 1, 'creator': 'creator', 'username': '', 'dialog': dialog, 'now_category': now_category, 'challenge': challenge, 'intro_active': 1}
            template = env.get_template('template/detail.html')
            self.response.write(template.render(context))
            # ChallengeRequest info goes here

        else: # Challenge not found
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('Challenge not found!')

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
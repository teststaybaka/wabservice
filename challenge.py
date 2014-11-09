import cgi
import urllib
import logging
from google.appengine.ext import db
import webapp2
import jinja2

from models import *
from views import env

from views import BaseHandler

def challengeKey(userid):
    return db.Key.from_path('Challenge', userid)

class Create(BaseHandler):
    def get(self):
        if self.session.get('id'):
            context = {'username': self.session.get('username'), 'dialog': 'You got a good idea?', 'now_category': 'create'}
            template = env.get_template('template/create.html')
            self.response.write(template.render(context))
        else:
            self.response.write('Please login first! <a href="/">Home</a>')

    def post(self):
        if self.session.get('id'):
            # Naive creation with no scrutiny
            challenge_ID_Factory = db.GqlQuery("select * from Challenge_ID_Factory").get()
            challenge = Challenge(
                challenge_id      = challenge_ID_Factory.get_id(),
                creator_id        = self.session['id'],
                title             = self.request.get('title'), 
                summary           = self.request.get('summary'), 
                content           = self.request.get('content'),
                state             = 'ongoing', 
                veri_method       = self.request.get('veri_method'),
                category          = [self.request.get('category')],
                completion_counts = 0,
                accept_counts     = 0,
                parent = challengeKey(self.session['id']),
                );
            challenge.put();
            url = '/challenge/' + str(challenge.challenge_id)
            self.session['message'] = 'Successfully created challenge!'
            self.redirect(url)
        else:
            self.response.write('Please login first! <a href="/">Home</a>')


class Edit(BaseHandler):
    def get(self, challenge_id):
        logging.info(challenge_id)
        query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        challenge = query.get()
        if challenge is not None:
            if challenge.creator_id != self.session.get('id'):
                self.response.write('Invalid operation!')
            else:
                context = {'username': self.session.get('username'), 'challenge': challenge}
                template = env.get_template('template/edit.html')
                self.response.write(template.render(context))
        else:
            self.response.write('Challenge not found!')

    def post(self, challenge_id):
        query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        challenge = query.get()
        if challenge is not None:
            if challenge.creator_id != self.session.get('id'):
                self.response.write('Invalid operation!')
            else:
                challenge.title = self.request.get('title')
                challenge.summary = self.request.get('summary')
                challenge.content = self.request.get('content')
                challenge.veri_method = self.request.get('veri_method')
                challenge.category = [self.request.get('category')]
                challenge.put()
                # self.response.write('Challenge updated successfully! Go back to <a href="/challenge/' 
                #     + str(challenge.challenge_id) + '"> challenge </a>')
                url = '/challenge/' + str(challenge.challenge_id)
                self.session['message'] = 'Successfully edited challenge!'
                self.redirect(url)
        else:
            self.response.write('Challenge not found!')

############################ I am the Dividing Line ############################################

class Detail(BaseHandler):
    def get(self, challenge_id):
        logging.info(self.request)
        now_category = 'for fun'
        # logging.info("%s %s", challenge_id, type(challenge_id))
        # query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        # challenge = query.get()
        key = challengeKey(self.session['id'])
        challenge = Challenge.all().ancestor(key).filter("challenge_id =", int(challenge_id)).get()

        if challenge is not None:
            dialog = 'Hello there. Welcome.'
            creator = db.GqlQuery("select * from User where id = :1", challenge.creator_id).get()
            context = { 'state': 1, 'creator': creator, 'username': self.session.get('username'), 'dialog': dialog, 'now_category': now_category, 'challenge': challenge, 'intro_active': 1}
            if self.session.get('id') == creator.id:
                context['editable'] = True
            if self.session.get('message'):
                context['message'] = self.session.get('message')
                self.session.pop('message')
            template = env.get_template('template/detail.html')
            # add ChallengeRequest info here
            self.response.write(template.render(context))

        else: # Challenge not found
            self.response.write('Challenge not found!')

class Invite(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

def challengeRequestKey(userid):
    return db.Key.from_path('ChallengeRequest', userid)

class Requests(BaseHandler):
    def get(self):
        if self.session.get('id'):
            # query = db.GqlQuery("select * from ChallengeRequest where invitee_id = :1", self.session['id'])
            # requests = query.fetch(None)
            requestKey = challengeRequestKey(self.session['id'])
            requests = ChallengeRequest.all().ancestor(requestKey).fetch(None)
            # development purpose only. if no challenge request exists, create one.
            if len(requests) == 0:
                sampleRequest = ChallengeRequest(inviter_id = 'testuserid1', challenge_id = 1, invitee_id = 'testuserid1', status = 'pending', parent = requestKey)
                sampleRequest.put()

            context = { 'requests' : requests }
            template = env.get_template('template/requests.html')
            self.response.write(template.render(context))
        else:
            self.response.write('Please login first! <a href="/">Home</a>')

class Accept(BaseHandler):
    def get(self, request_id):
        requestKey = challengeRequestKey(self.session['id'])
        request = ChallengeRequest.get_by_id(long(request_id), requestKey)
        request.status = 'accepted'
        request.put()
        self.redirect_to('requests')

class Reject(BaseHandler):
    def get(self, request_id):
        requestKey = challengeRequestKey(self.session['id'])
        request = ChallengeRequest.get_by_id(long(request_id), requestKey)
        request.status = 'rejected'
        request.put()
        self.redirect_to('requests')

class Upload(webapp2.RequestHandler):
    def post(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Verify(webapp2.RequestHandler):
    def get(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')
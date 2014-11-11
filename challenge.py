import cgi
import urllib
import logging
from google.appengine.ext import db
import webapp2
import jinja2

from models import *
from views import env

from views import BaseHandler

# def challengeKey(userid):
#     return db.Key.from_path('Challenge', userid)

class Create(BaseHandler):
    def get(self):
        if self.current_user:
            context = {'dialog': 'You got a good idea?', 'now_category': 'create'}
            template = env.get_template('template/create.html')
            self.response.write(template.render(context))
        else:
            self.session['message'] = 'You need to log in!'
            self.redirect_to('home')

    def post(self):
        current_user = self.current_user
        if current_user:
            current_user_id = current_user.get('id')
            if current_user_id:
                # Naive creation with no scrutiny
                challenge_ID_Factory = db.GqlQuery("select * from Challenge_ID_Factory").get()
                # key = challengeKey(current_user.get('id'))
                user = User.all().filter('id = ', current_user_id).get()
                if user:
                    challenge = Challenge(
                        challenge_id      = challenge_ID_Factory.get_id(),
                        creator_id        = current_user_id,
                        title             = self.request.get('title'), 
                        summary           = self.request.get('summary'), 
                        content           = self.request.get('content'),
                        state             = 'ongoing', 
                        veri_method       = self.request.get('veri_method'),
                        category          = [self.request.get('category')],
                        completion_counts = 0,
                        accept_counts     = 0,
                        parent = user,
                        );
                    challenge.put();
                    res = Challenge.all().ancestor(user).filter('challenge_id = ', challenge.challenge_id).get();
                    if res:
                        url = '/challenge/' + str(challenge.challenge_id)
                        self.session['message'] = 'Successfully created challenge!'
                        self.redirect(url)
                    else:
                        self.session['message'] = 'Failed to create challenge.'
                        self.redirect_to('home')
                else:
                    logging.info("User not found!")
                    self.response.write('User not found!')
            else:
                self.response.write("something weird happened: session has no id")
        else:
            self.session['message'] = 'You need to log in!'
            self.redirect_to('home')


class Edit(BaseHandler):
    def get(self, challenge_id):
        logging.info(challenge_id)
        query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        challenge = query.get()
        if challenge is not None:
            current_user = self.current_user
            if current_user:
                if challenge.creator_id != current_user.get('id'):
                    self.session['message'] = 'Invalid operation!'
                    url = '/challenge/' + str(challenge.challenge_id)
                    self.redirect(url)
                else:
                    context = {'challenge': challenge}
                    template = env.get_template('template/edit.html')
                    self.response.write(template.render(context))
            else:
                self.session['message'] = 'You need to log in!'
                url = '/challenge/' + str(challenge.challenge_id)
                self.redirect(url)
        else:
            self.response.write('Challenge not found!')
        

    def post(self, challenge_id):
        query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        challenge = query.get()
        if challenge is not None:
            current_user = self.current_user
            if current_user:
                if challenge.creator_id != current_user.get('id'):
                    self.session['message'] = 'Invalid operation!'
                    self.redirect_to('home')
                else:
                    challenge.title = self.request.get('title')
                    challenge.summary = self.request.get('summary')
                    challenge.content = self.request.get('content')
                    challenge.veri_method = self.request.get('veri_method')
                    challenge.category = [self.request.get('category')]
                    challenge.put()
                    # self.response.write('Challenge updated successfully! Go back to <a href="/challenge/' 
                    #     + str(challenge.challenge_id) + '"> challenge </a>')
                    res = Challenge.all().ancestor(challenge.parent()).filter('challenge_id = ', challenge.challenge_id).get();
                    url = '/challenge/' + str(challenge.challenge_id)
                    logging.info(res)
                    if res:
                        self.session['message'] = 'Successfully updated challenge!'
                        self.redirect(url)
                    else:
                        self.session['message'] = 'Failed to update challenge.'
                        self.redirect(url)

                    # url = '/challenge/' + str(challenge.challenge_id)
                    # self.session['message'] = 'Successfully edited challenge!'
                    # self.redirect(url)
            else:
                self.session['message'] = 'You need to log in!'
                self.redirect_to('home')
        else:
            self.response.write('Challenge not found!')

############################ I am the Dividing Line ############################################

class Detail(BaseHandler):
    def get(self, challenge_id):
        
        now_category = 'for fun'
        challenge = Challenge.all().filter("challenge_id =", int(challenge_id)).get()

        if challenge is not None:
            creator = db.GqlQuery("select * from User where id = :1", challenge.creator_id).get()
            context = { 'creator': creator, 'now_category': now_category, 'challenge': challenge, 'intro_active': 1}
            
            if self.session.get('message'):
                context['dialog'] = self.session.get('message')
                self.session.pop('message')
            else:
                context['dialog'] = 'Hello there. Welcome.'

            current_user = self.current_user
            if current_user:
                # key = challengeKey(current_user.get('id'))
                query = db.GqlQuery('select * from ChallengeRequest where challenge_id = :1 and invitee_id = :2', int(challenge_id), current_user.get('id'))
                request = query.get()
                if request:
                    if request.status == 'pending':
                        state = 5
                    elif request.status == 'accepted':
                        state = 4
                    elif request.status == 'rejected':
                        state = 6
                    context['request_id'] = request.key().id()
                else:
                    state = 6
                
                if current_user.get('id') == creator.id:
                    state = 2
                    context['editable'] = True
            else:
                state = 8

            context['state'] = state
            template = env.get_template('template/detail.html')
            self.response.write(template.render(context))
        else:
            self.response.write("Challenge does not exist!")
        # else:
        # now_category = 'for fun'
        # # logging.info("%s %s", challenge_id, type(challenge_id))
        # query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        # for entry in query.run():
        #     challenge = entry
        # dialog = 'Hello there. Welcome.'
        # context = { 'state': 1, 'creator': 'creator', 'username': '', 'dialog': dialog, 'now_category': now_category, 'challenge': challenge, 'intro_active': 1}
        # template = env.get_template('template/detail.html')
        # self.response.write(template.render(context))


class Invite(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

def challengeRequestKey(userid):
    return db.Key.from_path('ChallengeRequest', userid)

class Requests(BaseHandler):
    def get(self):
        current_user = self.current_user
        if current_user:
            requestKey = challengeRequestKey(current_user.get('id'))
            requests = ChallengeRequest.all().ancestor(requestKey).fetch(None)
            context = { 'requests' : requests }
            template = env.get_template('template/requests.html')
            self.response.write(template.render(context))
        else:
            self.response.write('Please login first! <a href="/">Home</a>')

class Accept(BaseHandler):
    def get(self, request_id):
        requestKey = challengeRequestKey(self.current_user.get('id'))
        request = ChallengeRequest.get_by_id(long(request_id), requestKey)
        request.status = 'accepted'
        request.put()
        self.redirect_to('detail', challenge_id=request.challenge_id)

class Reject(BaseHandler):
    def get(self, request_id):
        requestKey = challengeRequestKey(self.current_user.get('id'))
        request = ChallengeRequest.get_by_id(long(request_id), requestKey)
        request.status = 'rejected'
        request.put()
        self.redirect_to('detail', challenge_id=request.challenge_id)

class Upload(webapp2.RequestHandler):
    def post(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Verify(webapp2.RequestHandler):
    def get(self, challenge_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')
import cgi
import urllib
import logging
from google.appengine.ext import db
import webapp2
import jinja2

from models import *
from views import env

class Signin(webapp2.RequestHandler):
    def get(self):
        context = {'dialog': 'Do you have an account?'}
        template = env.get_template('template/signin.html')
        self.response.write(template.render(context))

    # def post(self):

class Signup(webapp2.RequestHandler):
    def get(self):
        context = {'dialog': 'Do you have an account?'}
        template = env.get_template('template/signup.html')
        self.response.write(template.render(context))

    # def post(self):

class Logout(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Account(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class Inbox(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

class History(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

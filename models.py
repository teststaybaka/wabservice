from google.appengine.ext import db
from google.appengine.ext import blobstore

available_category_list = ['Public', 'Closed', 'Charity', 'For fun']
challenges_states = ['ongoing', 'closed']
challenge_user_relationships = ['creator', 'accepted', 'invited', 'rejected', 'verifying', 'upon_completed']
verification_methods = ['video', 'image', 'both']

class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    messages = db.ListProperty(db.Key)

class Challenge(db.Model):
    challenge_id = db.IntegerProperty(required=True)
    title = db.StringProperty(required=True)
    summary = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    state = db.StringProperty(required=True, choices=challenges_states)
    veri_method = db.StringProperty(required=True, choices=verification_methods)
    category = db.StringListProperty()
    completion_counts = db.IntegerProperty()
    accept_counts = db.IntegerProperty()

class UserChallenge(db.Model):
    user = db.ReferenceProperty(User, required=True, collection_name='users')
    challenge = db.ReferenceProperty(Challenge, required=True, collection_name='challenges')
    relationship = db.StringProperty(required=True, choices=challenge_user_relationships)
    file_name = db.StringProperty()
    file_entity = db.BlobProperty()

class Message(object):
    message_title = db.StringProperty(required=True)
    message_content = db.StringProperty(required=True)

class Test(db.Model):
    """test database"""
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)

class Challenge_ID_Factory(db.Model):
    id_counter = db.IntegerProperty(required=True)

    def get_id(self):
        self.id_counter += 1
        self.put()
        return self.id_counter
from google.appengine.ext import db
from google.appengine.ext import blobstore

from const import *


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
    # creator = db.ReferenceProperty(User, required=True, collection_name='users')
    creator_id = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    summary = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    state = db.StringProperty(required=True, choices=challenges_states)
    veri_method = db.StringProperty(required=True, choices=verification_methods)
    category = db.StringListProperty()
    completion_counts = db.IntegerProperty()
    accept_counts = db.IntegerProperty()


class ChallengeRequest(db.Model):
    inviter_id = db.StringProperty(required=True)
    challenge_id = db.IntegerProperty(required=True)
    invitee_id = db.StringProperty(required=True)
    status = db.StringProperty(required=True, choices=[
        RequestStatus.PENDING,
        RequestStatus.ACCEPTED,
        RequestStatus.REJECTED,
        RequestStatus.VERIFYING,
        RequestStatus.VERIFIED,
        RequestStatus.COMPLETED])
    file_info = blobstore.BlobReferenceProperty()


class Message(db.Model):
    message_title = db.StringProperty(required=True)
    message_content = db.StringProperty(required=True)


class Challenge_ID_Factory(db.Model):
    id_counter = db.IntegerProperty(required=True)

    def get_id(self):
        self.id_counter += 1
        self.put()
        return self.id_counter
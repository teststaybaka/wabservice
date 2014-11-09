import webapp2
from google.appengine.ext import db

from models import *

class Init(webapp2.RequestHandler):
    def get(self):
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

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Data initialized.')
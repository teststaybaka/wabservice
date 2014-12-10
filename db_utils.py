from models import *


class KeyStore(object):
    @staticmethod
    def challenge_request_key():
        return db.Key.from_path('EntityType', 'ChallengeRequest')

    @staticmethod
    def challenge_key():
        return db.Key.from_path('EntityType', 'Challenge')

    @staticmethod
    def id_factory_key():
        return db.Key.from_path('EntityType', 'Challenge_ID_Factory')


def get_id_factory():
    challenge_id_factory = Challenge_ID_Factory.all().ancestor(
        KeyStore.challenge_request_key()).get()
    if challenge_id_factory is None:
        challenge_id_factory = Challenge_ID_Factory(id_counter=0)
        challenge_id_factory.put()
    return challenge_id_factory
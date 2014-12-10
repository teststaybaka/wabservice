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
    factory_key = KeyStore.id_factory_key()
    challenge_id_factory = Challenge_ID_Factory.all().ancestor(
        factory_key).get()
    if challenge_id_factory is not None:
        return challenge_id_factory
    else:
        challenge_id_factory = Challenge_ID_Factory(id_counter=0,
                                                    parent=factory_key)
        challenge_id_factory.put()
        return challenge_id_factory
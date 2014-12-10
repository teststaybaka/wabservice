from google.appengine.ext.db import BadValueError

from challenge_request_impl import *
from views import *


class Create(BaseHandler):
    def get(self):
        if self.current_user:
            context = {'dialog': 'You got a good idea?',
                       'now_category': 'create'}
            template = env.get_template('template/create.html')
            self.response.write(template.render(context))
        else:
            self.session['message'] = 'You need to log in!'
            self.redirect_to(RouteName.HOME)

    def post(self):
        current_user = self.current_user
        if current_user:
            current_user_id = current_user.get('id')
            if current_user_id:
                # Naive creation with no scrutiny
                challenge_id_factory = \
                    db.GqlQuery("select * from Challenge_ID_Factory").get()
                user = User.all().filter('id = ', current_user_id).get()
                if user:
                    challenge_key = KeyStore.challenge_key()

                    try:
                        challenge = Challenge(
                            challenge_id      = challenge_id_factory.get_id(),
                            creator_id        = current_user_id,
                            title             = self.request.get('title'),
                            summary           = self.request.get('summary'),
                            content           = self.request.get('content'),
                            state             = 'ongoing',
                            veri_method       = self.request.get('veri_method'),
                            category          = [self.request.get('category')],
                            completion_counts = 0,
                            accept_counts     = 0,
                            parent            = KeyStore.challenge_key())
                    except BadValueError:
                        message =\
                            'Some required fields are missing or invalid.'
                        context = {'dialog': message, 'now_category': 'create'}
                        template = env.get_template('template/create.html')
                        self.response.write(template.render(context))
                        return

                    challenge.put()
                    res = Challenge.all().ancestor(KeyStore.challenge_key())\
                        .filter('challenge_id = ', challenge.challenge_id)\
                        .get()
                    if res:
                        self.session['message'] = \
                            'Successfully created challenge!'
                        self.redirect_to(RouteName.DETAIL,
                                         challenge_id=challenge.challenge_id)
                    else:
                        self.session['message'] = 'Failed to create challenge.'
                        self.redirect_to(RouteName.HOME)
                else:
                    logging.info("User not found!")
                    self.response.write('User not found!')
            else:
                self.response.write("something weird happened: session has no id")
        else:
            self.session['message'] = 'You need to log in!'
            self.redirect_to(RouteName.HOME)


class Edit(BaseHandler):
    def get(self, challenge_id):
        challenge = Challenge.all().ancestor(KeyStore.challenge_key())\
            .filter('challenge_id =', int(challenge_id)).get()
        if challenge is not None:
            current_user = self.current_user
            if current_user:
                if challenge.creator_id != current_user.get('id'):
                    self.session['message'] = \
                        'Only the creator can edit this challenge.'
                    self.redirect_to(RouteName.DETAIL,
                                     challenge_id=challenge.challenge_id)
                else:
                    context = {'challenge': challenge}
                    template = env.get_template('template/edit.html')
                    self.response.write(template.render(context))
            else:
                self.session['message'] = 'You need to log in!'
                self.redirect_to(RouteName.DETAIL,
                                 challenge_id=challenge.challenge_id)
        else:
            self.session['message'] = 'Challenge not found.'
            self.redirect_to(RouteName.HOME)

    def post(self, challenge_id):
        challenge = Challenge.all().ancestor(KeyStore.challenge_key())\
            .filter('challenge_id =', int(challenge_id)).get()
        if challenge is not None:
            current_user = self.current_user
            if current_user:
                if challenge.creator_id != current_user.get('id'):
                    self.session['message'] = \
                        'Only the creator can edit this challenge.'
                    self.redirect_to(RouteName.DETAIL,
                                     challenge_id=challenge.challenge_id)
                else:
                    try:
                        challenge.title = self.request.get('title')
                        challenge.summary = self.request.get('summary')
                        challenge.content = self.request.get('content')
                        challenge.veri_method = self.request.get('veri_method')
                        challenge.category = [self.request.get('category')]
                        challenge.put()
                    except BadValueError:
                        context = {'challenge': challenge,
                                   'dialog': 'Some required fields are '
                                             'missing or invalid.'}
                        template = env.get_template('template/edit.html')
                        self.response.write(template.render(context))
                        return

                    res = Challenge.all().ancestor(KeyStore.challenge_key())\
                        .filter('challenge_id = ', challenge.challenge_id)\
                        .get()
                    url = webapp2.uri_for(RouteName.DETAIL,
                                          challenge_id=challenge.challenge_id)
                    if res:
                        self.session['message'] = \
                            'Successfully updated challenge!'
                        self.redirect(url)
                    else:
                        self.session['message'] = \
                            'Failed to update challenge.'
                        self.redirect_to(RouteName.HOME)
            else:
                self.session['message'] = 'You need to log in!'
                self.redirect_to(RouteName.HOME)
        else:
            self.session['message'] = 'Challenge not found.'
            self.redirect_to(RouteName.HOME)

############################ I am the Dividing Line ############################################

class Detail(BaseHandler):
    def get(self, challenge_id):

        now_category = 'for fun'
        challenge = Challenge.all().filter("challenge_id =", int(challenge_id)).get()

        if challenge is not None:
            creator = db.GqlQuery("select * from User where id = :1", challenge.creator_id).get()
            context = {'creator': creator, 'now_category': now_category,
                       'challenge': challenge, 'intro_active': 1,
                       'dialog': self.message}

            current_user = self.current_user
            if current_user:
                request_key = KeyStore.challenge_request_key()
                request = ChallengeRequest.all().ancestor(request_key) \
                    .filter("challenge_id =", int(challenge_id)) \
                    .filter("invitee_id =", current_user.get('id')) \
                    .get()

                if request:
                    if request.status == RequestStatus.PENDING:
                        state = 5
                    elif request.status == RequestStatus.ACCEPTED:
                        state = 4
                    elif request.status == RequestStatus.REJECTED:
                        state = 6
                    elif request.status == RequestStatus.VERIFYING:
                        state = 8
                    elif request.status == RequestStatus.VERIFIED:
                        state = 3
                        context['friend_list'] = self.get_invitable_friends(
                            current_user, challenge_id, challenge.creator_id)
                    else:
                        state = 7
                    context['request_id'] = request.key().id()
                else:
                    state = 9

                if current_user.get('id') == creator.id:
                    state = 2
                    context['editable'] = True
                    context['friend_list'] = self.get_invitable_friends(
                        current_user, challenge_id, challenge.creator_id)
            else:
                state = 10

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

    def get_invitable_friends(self, current_user, challenge_id, creator_id):
        # get all friends from facebook API
        try:
            graph = facebook.GraphAPI(current_user["access_token"])
            profile = graph.get_object("me")
            friends = graph.get_connections("me", "friends")
        except:
            return []

        #exclude friends who have been invited
        invitable_friend_list = []
        for friend in friends['data']:
            query = db.GqlQuery("select * from ChallengeRequest where "
                                "challenge_id=:1 AND invitee_id=:2",
                                int(challenge_id),
                                friend['id'])
            if query.get() is None and friend['id'] != creator_id:
                invitable_friend_list.append((friend['name'], friend['id']))

        return invitable_friend_list


class Invite(BaseHandler):
    def get(self, challenge_id):
        self.redirect_to('detail', challenge_id=challenge_id)

    def post(self, challenge_id):
        current_user = self.current_user
        current_user_id = None
        if current_user:
            current_user_id = current_user.get('id')

            if current_user_id is not None:
                invite(challenge_id, current_user_id, self.request.get("friend1"))

                # reload page
                self.redirect_to(RouteName.DETAIL, challenge_id=challenge_id)

        else:
            self.session['message'] = 'You need to log in!'
            self.redirect_to('home')


class Accept(BaseHandler):
    def get(self, request_id):
        logging.info("accept handler " + request_id)
        challenge_id = accept_request(request_id)
        self.redirect_to('detail', challenge_id=challenge_id)


class Reject(BaseHandler):
    def get(self, request_id):
        logging.info("reject handler " + request_id)
        challenge_id = reject_request(request_id)
        self.redirect_to('detail', challenge_id=challenge_id)


class Upload(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    def post(self, challenge_id):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        if upload_files == []:
            # self.session['message'] = 'Please select a file.'
            # self.redirect_to('detail', challenge_id=challenge_id)
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('Please select a file.')
            return
        blob_info = upload_files[0]
        query = db.GqlQuery('select * from ChallengeRequest where challenge_id = :1 and invitee_id = :2', int(challenge_id), self.current_user.get('id'))
        request = query.get()
        if request.file_info != None:
            request.file_info.delete()
        request.file_info = blob_info
        request.status = RequestStatus.VERIFYING
        request.put()
        logging.info('upload:'+blob_info.filename)
        # self.redirect_to('detail', challenge_id=challenge_id)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Upload succeeded.')


class GetUploadURL(BaseHandler):
    def get(self, challenge_id):
        upload_url = blobstore.create_upload_url('/challenge/'+challenge_id+'/upload')
        # logging.info('GetUploadURL:'+upload_url)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(upload_url)


class Verify(BaseHandler):
    def get(self, request_id):
        logging.info("verify handler " + request_id)
        challenge_id = verify_request(request_id)
        self.redirect_to('completions', challenge_id=challenge_id)


class Retry(BaseHandler):
    def get(self, request_id):
        logging.info("retry handler " + request_id)
        challenge_id = retry_request(request_id)
        self.redirect_to('completions', challenge_id=challenge_id)


class Completions(BaseHandler):
    @staticmethod
    def assemble_file_info(request):
        invitee_id = request.invitee_id
        c_type = request.file_info.content_type.split('/')
        video_type = ''
        status = request.status
        if c_type[0] == 'image':
            tag = 'img'
        else:
            tag = 'video'
            video_type = 'video/' + c_type[1]
        return {
            'name': User.get_by_key_name(invitee_id).name,
            'user_id': invitee_id,
            'filename': request.file_info.filename,
            'tag': tag,
            'type': video_type,
            'status': status,
            'request_id': request.key().id()}

    def get(self, challenge_id):
        # TODO: replace hardcoded value with real data
        now_category = 'for fun'

        query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        challenge = query.get()
        creator = 0
        completion_list = []

        request_key = KeyStore.challenge_request_key()

        if self.current_user and challenge.creator_id == self.current_user.get('id'):
            creator = 1

        if creator == 1:
            query = ChallengeRequest.all().ancestor(request_key) \
                .filter("challenge_id =", int(challenge_id))\
                .filter("status =", RequestStatus.VERIFYING)
            for request in query.run():
                completion_list.append(self.assemble_file_info(request))

        query = ChallengeRequest.all().ancestor(request_key) \
                .filter("challenge_id =", int(challenge_id))\
                .filter("status =", RequestStatus.VERIFIED)
        for request in query.run():
            completion_list.append(self.assemble_file_info(request))

        query = ChallengeRequest.all().ancestor(request_key) \
                .filter("challenge_id =", int(challenge_id))\
                .filter("status =", RequestStatus.COMPLETED)
        for request in query.run():
            completion_list.append(self.assemble_file_info(request))

        dialog = 'How is it going?'
        context = {'dialog': dialog, 'now_category': now_category,
                   'challenge': challenge,
                   'completion_list': completion_list, 'creator': creator}
        template = env.get_template('template/completions.html')
        self.response.write(template.render(context))


class ServeFile(BaseHandler, blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, challenge_id, user_id):
        query = db.GqlQuery('select * from ChallengeRequest where challenge_id = :1 and invitee_id = :2', int(challenge_id), user_id)
        request = query.get()
        logging.info(request.file_info.filename)
        # self.response.headers['Content-Type'] = 'image/jpeg'
        # self.response.write(request.file_info)
        self.send_blob(request.file_info)

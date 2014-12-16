from google.appengine.ext.db import BadValueError
from google.appengine.ext.webapp import blobstore_handlers

from db_utils import *
from views import *


class Create(BaseHandler):
    def get(self):
        current_user = self.check_login_status()
        if current_user:
            context = {'dialog': 'You got a good idea?',
                       'category_list': available_category_list}
            template = env.get_template('template/create.html')
            self.response.write(template.render(context))

    def post(self):
        current_user = self.check_login_status()
        if current_user:
            current_user_id = current_user.get('id')
            challenge_id_factory = get_id_factory()

            try:
                challenge = Challenge(
                    challenge_id      = challenge_id_factory.get_id(),
                    creator_id        = current_user_id,
                    title             = self.request.get('title'),
                    summary           = self.request.get('summary'),
                    content           = self.request.get('content'),
                    state             = 'ongoing',
                    category          = self.request.get_all('category'),
                    completion_counts = 0,
                    accept_counts     = 0,
                    parent            = KeyStore.challenge_key())
            except BadValueError:
                message = \
                    'Some required fields are missing or invalid.'
                context = {'dialog': message,
                           'category_list': available_category_list}
                template = env.get_template('template/create.html')
                self.response.write(template.render(context))
                return

            challenge.put()
            challenge = Challenge.all().ancestor(KeyStore.challenge_key()) \
                .filter('challenge_id = ', challenge.challenge_id) \
                .get()
            if challenge:
                self.session['message'] = StrConst.CHALLENGE_CREATE_SUCCESS
                self.redirect_to(RouteName.DETAIL,
                                 challenge_id=challenge.challenge_id)
            else:
                self.gen_error_page(message=StrConst.CHALLENGE_CREATE_FAIL)


class Edit(BaseHandler):
    def get(self, challenge_id):
        challenge = Challenge.all().ancestor(KeyStore.challenge_key())\
            .filter('challenge_id =', int(challenge_id)).get()
        if challenge is not None:
            current_user = self.check_login_status()
            if current_user:
                if challenge.creator_id != current_user.get('id'):
                    self.session['message'] = \
                        'Only the creator can edit this challenge.'
                    self.redirect_to(RouteName.DETAIL,
                                     challenge_id=challenge.challenge_id)
                else:
                    checked = []
                    for i in range(0, len(available_category_list)):
                        found = 0
                        for j in range(0, len(challenge.category)):
                            if challenge.category[j] == available_category_list[i]:
                                found = 1
                                break
                        checked.append(found)

                    context = {'challenge': challenge, 'category_list': available_category_list, 'checked':checked, 'dialog':'Anything you want to change?'}
                    template = env.get_template('template/edit.html')
                    self.response.write(template.render(context))
        else:
            self.gen_error_page(message=StrConst.CHALLENGE_NOT_FOUND)

    def post(self, challenge_id):
        challenge = Challenge.all().ancestor(KeyStore.challenge_key())\
            .filter('challenge_id =', int(challenge_id)).get()
        if challenge is not None:
            current_user = self.check_login_status()
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
                        challenge.category = self.request.get_all('category')
                        challenge.put()
                    except BadValueError:
                        context = {'challenge': challenge,
                                   'dialog': 'Some required fields are '
                                             'missing or invalid.'}
                        template = env.get_template('template/edit.html')
                        self.response.write(template.render(context))
                        return

                    self.session['message'] = StrConst.CHALLENGE_UPDATED
                    self.redirect(webapp2.uri_for(
                        RouteName.DETAIL, challenge_id=challenge.challenge_id))
        else:
            self.gen_error_page(message=StrConst.CHALLENGE_NOT_FOUND)


class Detail(BaseHandler):
    def get(self, challenge_id):
        challenge = Challenge.all().filter(
            "challenge_id =", int(challenge_id)).get()
        if challenge is not None:
            creator = db.GqlQuery("select * from User where id = :1",
                                  challenge.creator_id).get()
            default_message = 'How is this challenge? Do you like it?'
            context = {'creator': creator,
                       'challenge': challenge,
                       'intro_active': 1,
                       'dialog': self.message(default_message=default_message)}

            current_user = self.current_user
            if current_user:
                request_key = KeyStore.challenge_request_key()
                request = ChallengeRequest.all().ancestor(request_key) \
                    .filter("challenge_id =", int(challenge_id)) \
                    .filter("invitee_id =", current_user.get('id')) \
                    .get()

                if request:
                    if request.status == RequestStatus.PENDING:
                        state = DetailState.PENDING
                    elif request.status == RequestStatus.ACCEPTED:
                        state = DetailState.ACCEPTED
                    elif request.status == RequestStatus.REJECTED:
                        state = DetailState.REJECTED
                    elif request.status == RequestStatus.VERIFYING:
                        state = DetailState.VERIFYING
                    elif request.status == RequestStatus.VERIFIED:
                        state = DetailState.VERIFIED
                        try:
                            context['friend_list'] = self.get_invitable_friends(
                                current_user, challenge_id, challenge.creator_id)
                        except facebook.GraphAPIError:
                            self.refresh_login_status()
                            self.redirect_to(RouteName.DETAIL,
                                             challenge_id=challenge_id)
                            return
                    else:
                        state = DetailState.COMPLETED
                    context['request_id'] = request.key().id()
                else:
                    state = DetailState.NOT_INVITED

                if current_user.get('id') == creator.id:
                    state = DetailState.CREATOR
                    context['editable'] = True
                    try:
                        context['friend_list'] = self.get_invitable_friends(
                            current_user, challenge_id, challenge.creator_id)
                    except facebook.GraphAPIError:
                        self.refresh_login_status()
                        self.redirect_to(RouteName.DETAIL,
                                         challenge_id=challenge_id)
                        return
            else:
                state = DetailState.NOT_LOGGED_IN

            context['state'] = state
            template = env.get_template('template/detail.html')
            self.response.write(template.render(context))
        else:
            self.gen_error_page(message=StrConst.CHALLENGE_NOT_FOUND)

    def get_invitable_friends(self, current_user, challenge_id, creator_id):
        # get all friends from facebook API
        try:
            graph = facebook.GraphAPI(current_user["access_token"])
            profile = graph.get_object("me")
            friends = graph.get_connections("me", "friends")
            logging.info(str(friends))
        except:
            raise

        # exclude friends who have been invited
        invitable_friend_list = []
        for friend in friends['data']:
            query = db.GqlQuery("select * from ChallengeRequest where "
                                "challenge_id=:1 AND invitee_id=:2",
                                int(challenge_id),
                                friend['id'])
            if query.get() is None and friend['id'] != creator_id:
                invitable_friend_list.append((friend['name'], friend['id']))

        return invitable_friend_list


class Upload(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    def post(self, challenge_id):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        if upload_files == []:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('Please select a file.')
            self.response.set_status(500)
            return

        blob_info = upload_files[0]
        logging.info("upload content_type:"+blob_info.content_type)
        logging.info("upload size:"+str(blob_info.size))
        types = blob_info.content_type.split('/')
        if types[0] != 'image' and types[0] != 'video':
            blob_info.delete()
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('File type error.')
            self.response.set_status(500)
            return

        if blob_info.size > 50*1000000:
            blob_info.delete()
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('File is too large.')
            self.response.set_status(500)
            return

        query = db.GqlQuery('select * from ChallengeRequest where challenge_id = :1 and invitee_id = :2', int(challenge_id), self.current_user.get('id'))
        request = query.get()
        if not request:
            blob_info.delete()
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('Request doesn\'t exist.')
            self.response.set_status(500)
            return

        if request.file_info != None:
            request.file_info.delete()
        request.file_info = blob_info
        if request.status == RequestStatus.ACCEPTED:
            request.status = RequestStatus.VERIFYING
        request.put()
        # logging.info('upload:'+blob_info.filename)
        # self.redirect_to('detail', challenge_id=challenge_id)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Upload succeeded.')


class GetUploadURL(BaseHandler):
    def get(self, challenge_id):
        upload_url = blobstore.create_upload_url('/challenge/' + challenge_id
                                                 + '/upload')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(upload_url)


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
        challenge = Challenge.all().ancestor(KeyStore.challenge_key())\
            .filter('challenge_id =', int(challenge_id)).get()
        logging.info('challenge completions.'+str(challenge))
        if challenge is None:
            self.gen_error_page(message=StrConst.CHALLENGE_NOT_FOUND)
            return

        creator = False
        completion_list = []
        request_key = KeyStore.challenge_request_key()

        if self.current_user and challenge.creator_id == self.current_user.get('id'):
            creator = True

        if creator:
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
        context = {'dialog': dialog,
                   'challenge': challenge,
                   'completion_list': completion_list,
                   'creator': creator}
        template = env.get_template('template/completions.html')
        self.response.write(template.render(context))


class ServeFile(BaseHandler, blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, challenge_id, user_id):
        query = db.GqlQuery('select * from ChallengeRequest where challenge_id = :1 and invitee_id = :2', int(challenge_id), user_id)
        request = query.get()
        if request is not None:
            logging.info(request.file_info.filename)
            # self.response.headers['Content-Type'] = 'image/jpeg'
            # self.response.write(request.file_info)
            self.send_blob(request.file_info)
        else:
            self.gen_error_page(message=StrConst.RESOURCE_NOT_FOUND)

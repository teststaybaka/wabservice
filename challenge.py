from views import *
from challenge_request_impl import *

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
            context = { 'creator': creator, 'now_category': now_category, 'challenge': challenge, 'intro_active': 1, 'dialog': self.message}

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
                    elif request.status == 'verifying':
                        state = 8
                    elif request.status == 'verified':
                        state = 3
                        context['friend_list'] = self.getInvitableFriends(current_user, challenge_id, challenge.creator_id)
                    else:
                        state = 7
                    context['request_id'] = request.key().id()
                else:
                    state = 9
                
                if current_user.get('id') == creator.id:
                    state = 2
                    context['editable'] = True
                    context['friend_list'] = self.getInvitableFriends(current_user, challenge_id, challenge.creator_id)
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

    def getInvitableFriends(self, current_user, challenge_id, creator_id):
        # get all friends from facebook API
        graph = facebook.GraphAPI(current_user["access_token"])
        profile = graph.get_object("me")
        friends = graph.get_connections("me", "friends")

        #exclude friends who have been invited
        invitableFriList = []
        for friend in friends['data']:
            query = db.GqlQuery("select * from ChallengeRequest where challenge_id=:1 AND invitee_id=:2",
                                int(challenge_id),
                                friend['id'])
            if query.get() is None and friend['id'] != creator_id:
                invitableFriList.append((friend['name'], friend['id']))

        return invitableFriList

class Invite(BaseHandler):
    def get(self, challenge_id):
        self.redirect_to('detail', challenge_id=challenge_id)

    def post(self, challenge_id):
        current_user = self.current_user
        current_user_id = None
        if current_user:
            current_user_id = current_user.get('id') 

        if current_user_id is not None:
            creator_id = Challenge.all().filter("challenge_id =", int(challenge_id)).get().creator_id
            
            # user as invitee
            if current_user_id != creator_id:
                query = db.GqlQuery("select * from ChallengeRequest where invitee_id=:1 AND challenge_id=:2", 
                                    current_user_id,
                                    int(challenge_id))
                queryItem = query.get()
                queryItem.status = "completed"
                queryItem.put()

            #user as inviter
            invitee_id = self.request.get("friend1")
            # if parent is None:
            #     user = User(key_name=invitee_id,
            #                 id=invitee_id,
            #                 name=invitee_id)
            #     user.put()
            requestKey = challengeRequestKey()
            request = ChallengeRequest(inviter_id = current_user_id,
                                        invitee_id = invitee_id,
                                        challenge_id = int(challenge_id),
                                        status = "pending",
                                        parent = requestKey)
            request.put()

            # reload page
            url = '/challenge/' + challenge_id
            self.redirect(url)
        else:
            self.session['message'] = 'You need to log in!'
            self.redirect_to('home')

class Requests(BaseHandler):
    def get(self):
        current_user = self.current_user
        if current_user:
            requestKey = challengeRequestKey()
            requests = ChallengeRequest.all().ancestor(requestKey).fetch(None)
            context = { 'requests' : requests }
            template = env.get_template('template/requests.html')
            self.response.write(template.render(context))
        else:
            self.response.write('Please login first! <a href="/">Home</a>')

class Accept(BaseHandler):
    def get(self, request_id):
        challenge_id = acceptRequest(request_id)
        self.redirect_to('detail', challenge_id=challenge_id)

class Reject(BaseHandler):
    def get(self, request_id):
        requestKey = challengeRequestKey()
        request = ChallengeRequest.get_by_id(long(request_id), requestKey)
        request.status = 'rejected'
        request.put()
        self.redirect_to('detail', challenge_id=request.challenge_id)

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
        request.status = 'verifying'
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
        logging.info("verify handler "+request_id)
        requestKey = challengeRequestKey()
        request = ChallengeRequest.get_by_id(long(request_id), requestKey)
        request.status = 'verified'
        request.put()
        self.redirect_to('completions', challenge_id=request.challenge_id)

class Retry(BaseHandler):
    def get(self, request_id):
        logging.info("retry handler "+request_id)
        requestKey = challengeRequestKey()
        request = ChallengeRequest.get_by_id(long(request_id), requestKey)
        request.status = 'accepted'
        request.put()
        self.redirect_to('completions', challenge_id=request.challenge_id)

class Completions(BaseHandler):
    def assemble_file_info(self, request):
        invitee_id = request.invitee_id
        c_type = request.file_info.content_type.split('/')
        video_type = ''
        status = request.status
        if c_type[0] == 'image':
            tag = 'img'
        else:
            tag = 'video'
            video_type = 'video/'+c_type[1]
        return {'name':User.get_by_key_name(invitee_id).name, 'user_id':invitee_id, 'filename': request.file_info.filename, 'tag': tag, 'type': video_type, 'status':status, 'request_id':request.key().id()}

    def get(self, challenge_id):
        now_category = 'for fun'
        # logging.info("%s %s", challenge_id, type(challenge_id))
        completion_list = []
        query = db.GqlQuery("select * from Challenge where challenge_id = :1", int(challenge_id))
        challenge = query.get()
        creator = 0
        completion_list = []
        if self.current_user and challenge.creator_id == self.current_user.get('id'):
            creator = 1

        if creator == 1:
            query = db.GqlQuery("select * from ChallengeRequest where challenge_id = :1 and status = :2", int(challenge_id), "verifying")
            for request in query.run():
                completion_list.append(self.assemble_file_info(request))

        query = db.GqlQuery("select * from ChallengeRequest where challenge_id = :1 and status = :2", int(challenge_id), "verified")
        for request in query.run():
            completion_list.append(self.assemble_file_info(request))
        
        query = db.GqlQuery("select * from ChallengeRequest where challenge_id = :1 and status = :2", int(challenge_id), "completed")
        for request in query.run():
            completion_list.append(self.assemble_file_info(request))

        dialog = 'How is it going?'
        # logging.info("challenge "+str(challenge.challenge_id))
        context = { 'dialog': dialog, 'now_category': now_category, 'challenge': challenge, 'completion_list': completion_list, 'creator':creator}
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

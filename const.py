SECRET_KEY = 'efrghtrrouhsmvnmxdiosjdoifds68_=' \
             'iooijgrdxuihbvc97yutcivbhugd479k'
FACEBOOK_APP_ID = '797761393603664'
FACEBOOK_APP_SECRET = 'd95c7c45b86a757f44b7c4991a0b7f47'


class RequestStatus(object):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    VERIFYING = 'verifying'
    VERIFIED = 'verified'
    COMPLETED = 'completed'


class DetailState(object):
    CLOSED = 1
    CREATOR = 2
    VERIFIED = 3
    ACCEPTED = 4
    PENDING = 5
    REJECTED = 6
    COMPLETED = 7
    VERIFYING = 8
    NOT_INVITED = 9
    NOT_LOGGED_IN = 10


class RouteName(object):
    # account related
    HOME = 'home'
    LOGIN_STATUS_CHANGE = 'loginstatuschange'
    ACCOUNT = 'account'
    INBOX = 'inbox'
    HISTORY = 'history'

    # challenge related
    CREATE = 'create'
    DETAIL = 'detail'
    EDIT = 'edit'
    INVITE = 'invite'
    UPLOAD = 'upload'
    GET_UPLOAD_URL = 'get_upload_url'
    SERVE_FILE = 'serve_file'
    COMPLETIONS = 'completions'
    DISCUSSIONS = 'discussions'

    # challenge request related
    ACCEPT = 'accept'
    REJECT = 'reject'
    CONFIRM = 'confirm'
    RETRY = 'retry'

    # misc
    ERROR = 'error'
    TEST = 'test'
    INIT = 'init'
    ADD_NEW_ENTITY = 'add_new_entity'


class StrConst(object):
    NOT_LOGGED_IN = "Please login in first."
    DEFAULT_ERROR_MSG = "An unexpected error has occurred."
    CHALLENGE_CREATE_SUCCESS = "Successfully created challenge!"
    CHALLENGE_CREATE_FAIL = "Failed to create challenge."
    CHALLENGE_NOT_FOUND = "Challenge not found."
    CHALLENGE_UPDATED = "Challenge Updated!"
    INVITE_SUCCESS = "Invitation sent to the selected friends."
    INVITE_FAILED = "Failed to invite the selected friend."
    INVITE_NOT_AUTHORIZED = "You cannot invite others to this challenge."
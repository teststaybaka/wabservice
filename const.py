SECRET_KEY = 'efrghtrrouhsmvnmxdiosjdoifds68_=' \
             'iooijgrdxuihbvc97yutcivbhugd479k'


class RequestStatus(object):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    VERIFYING = 'verifying'
    VERIFIED = 'verified'
    COMPLETED = 'completed'


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
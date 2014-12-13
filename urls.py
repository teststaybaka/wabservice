import webapp2

import views, account, challenge, admin, challenge_request
from const import *


secret_key = SECRET_KEY
session_arg = dict(secret_key=secret_key)  # , session_max_age=10)
config = {'webapp2_extras.sessions': session_arg}

def handle_404(request, response, exception):
    views.gen_error_page(response, message='Oops! Page not found!')
    response.set_status(404)

def handle_500(request, response, exception):
    views.gen_error_page(response, message='A server error occurred!')
    response.set_status(500)

application = webapp2.WSGIApplication(
    [
        # account related
        webapp2.Route(r'/', views.Home, name=RouteName.HOME),
        webapp2.Route(r'/loginstatuschange/<pre_page:.*>',
                      account.LoginStatusChange,
                      name=RouteName.LOGIN_STATUS_CHANGE),
        webapp2.Route(r'/account', account.Account, name=RouteName.ACCOUNT),
        webapp2.Route(r'/inbox', account.Inbox, name=RouteName.INBOX),
        webapp2.Route(r'/history', account.History, name=RouteName.HISTORY),

        # challenge related
        webapp2.Route(r'/create', challenge.Create, name=RouteName.CREATE),
        webapp2.Route(r'/challenge/<challenge_id:\d+>',
                      challenge.Detail, name=RouteName.DETAIL),
        webapp2.Route(r'/challenge/<challenge_id:\d+>/edit',
                      challenge.Edit, name=RouteName.EDIT),
        webapp2.Route(r'/challenge/<challenge_id:\d+>/upload',
                      challenge.Upload, name=RouteName.UPLOAD),
        webapp2.Route(r'/challenge/<challenge_id:\d+>/getUploadURL',
                      challenge.GetUploadURL, name=RouteName.GET_UPLOAD_URL),
        webapp2.Route(r'/file/<challenge_id:\d+>/<user_id:\d+>',
                      challenge.ServeFile, name=RouteName.SERVE_FILE),
        webapp2.Route(r'/challenge/<challenge_id:\d+>/completions',
                      challenge.Completions, name=RouteName.COMPLETIONS),
        webapp2.Route(r'/challenge/<challenge_id:\d+>/discussions',
                      views.Discussions, name=RouteName.DISCUSSIONS),

        # challenge request related
        webapp2.Route(r'/invite/<challenge_id:\d+>',
                      challenge_request.Invite, name=RouteName.INVITE),
        webapp2.Route(r'/requests/<request_id:\d+>/accept',
                      challenge_request.Accept, name=RouteName.ACCEPT),
        webapp2.Route(r'/requests/<request_id:\d+>/reject',
                      challenge_request.Reject, name=RouteName.REJECT),
        webapp2.Route(r'/requests/<request_id:\d+>/confirm',
                      challenge_request.Verify, name=RouteName.CONFIRM),
        webapp2.Route(r'/requests/<request_id:\d+>/retry',
                      challenge_request.Retry, name=RouteName.RETRY),

        # misc
        webapp2.Route(r'/error', name='error'),
        webapp2.Route(r'/test', account.TestFacebook, name=RouteName.TEST),
        webapp2.Route(r'/admin/init', admin.Init, name=RouteName.INIT),
        webapp2.Route(r'/admin/add_new_entity', admin.AddNewEntity,
                      name=RouteName.ADD_NEW_ENTITY),
        ], debug=True
    , config=config)

application.error_handlers[404] = handle_404
application.error_handlers[500] = handle_500

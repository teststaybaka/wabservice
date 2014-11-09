import webapp2
import views, account, challenge, admin

# config for session key, create config.py for configurations
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}
application = webapp2.WSGIApplication([
    webapp2.Route(r'/', views.Home, name='home'),
    webapp2.Route(r'/testsignin', views.TestSignin, name='testsignin'),
    webapp2.Route(r'/testlogout', views.TestLogout, name='testlogout'),
    webapp2.Route(r'/signin', account.Signin, name='signin'),
    webapp2.Route(r'/signup', account.Signup, name='signup'),
    webapp2.Route(r'/logout', account.Logout, name='logout'),
    webapp2.Route(r'/account', account.Account, name='account'),
    webapp2.Route(r'/inbox', account.Inbox, name='inbox'),
    webapp2.Route(r'/history', account.History, name='history'),

    webapp2.Route(r'/invite', challenge.Invite, name='invite'),
    webapp2.Route(r'/create', challenge.Create, name='create'),
    webapp2.Route(r'/challenge/<challenge_id:\d+>/edit', challenge.Edit, name='edit'),

    webapp2.Route(r'/requests', challenge.Requests, name='requests'),
    webapp2.Route(r'/requests/<request_id:\d+>/accept', challenge.Accept, name='accept'),
    webapp2.Route(r'/requests/<request_id:\d+>/reject', challenge.Reject, name='reject'),

    webapp2.Route(r'/challenge/<challenge_id:\d+>/upload', challenge.Upload, name='upload'),
    webapp2.Route(r'/challenge/<challenge_id:\d+>/confirm', challenge.Verify, name='confirm'),

    webapp2.Route(r'/challenge/<challenge_id:\d+>', challenge.Detail, name='detail'),

    webapp2.Route(r'/challenge/<challenge_id:\d+>/completions', views.Completions, name='completions'),
    webapp2.Route(r'/challenge/<challenge_id:\d+>/discussions', views.Discussions, name='discussions'),

    webapp2.Route(r'/file/<file_id:\d+>', views.ServeFile, name='serve_file'),

    webapp2.Route(r'/admin/init', admin.Init, name='init')
], debug=True, config=config)

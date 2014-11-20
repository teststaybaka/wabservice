import webapp2
import views, account, challenge, admin

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='efrghtrrouhsmvnmxdiosjdoifds68_=iooijgrdxuihbvc97yutcivbhugd479k')#, session_max_age=10)
application = webapp2.WSGIApplication([
    webapp2.Route(r'/', views.Home, name='home'),
    webapp2.Route(r'/loginstatuschange/<pre_page:.*>', account.LoginStatusChange, name='loginstatuschange'),
    webapp2.Route(r'/account', account.Account, name='account'),
    webapp2.Route(r'/inbox', account.Inbox, name='inbox'),
    webapp2.Route(r'/history', account.History, name='history'),

    webapp2.Route(r'/invite/<challenge_id:\d+>', challenge.Invite, name='invite'),
    webapp2.Route(r'/create', challenge.Create, name='create'),
    webapp2.Route(r'/challenge/<challenge_id:\d+>/edit', challenge.Edit, name='edit'),

    webapp2.Route(r'/requests', challenge.Requests, name='requests'),
    webapp2.Route(r'/requests/<request_id:\d+>/accept', challenge.Accept, name='accept'),
    webapp2.Route(r'/requests/<request_id:\d+>/reject', challenge.Reject, name='reject'),

    webapp2.Route(r'/challenge/<challenge_id:\d+>/upload', challenge.Upload, name='upload'),
    webapp2.Route(r'/challenge/<challenge_id:\d+>/confirm', challenge.Verify, name='confirm'),

    webapp2.Route(r'/challenge/<challenge_id:\d+>', challenge.Detail, name='detail'),

    webapp2.Route(r'/challenge/<challenge_id:\d+>/completions', challenge.Completions, name='completions'),
    webapp2.Route(r'/challenge/<challenge_id:\d+>/discussions', views.Discussions, name='discussions'),

    webapp2.Route(r'/file/<challenge_id:\d+>/<user_id:\d+>', challenge.ServeFile, name='serve_file'),

    webapp2.Route(r'/test', account.TestFacebook, name='test'),
    webapp2.Route(r'/admin/init', admin.Init, name='init'),
    webapp2.Route(r'/admin/add_new_entity', admin.AddNewEntity, name='add_new_entity'),
], debug=True
, config=config)

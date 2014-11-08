import webapp2
import views, account

application = webapp2.WSGIApplication([
    webapp2.Route(r'/', views.Home, name='home'),
    webapp2.Route(r'/signin', account.Signin, name='signin'),
    webapp2.Route(r'/signup', account.Signup, name='signup'),
    webapp2.Route(r'/logout', account.Logout, name='logout'),
    webapp2.Route(r'/account', account.Account, name='account'),
    webapp2.Route(r'/inbox', account.Inbox, name='inbox'),
    webapp2.Route(r'/history', account.History, name='history'),
    webapp2.Route(r'/invite', views.Invite, name='invite'),
    webapp2.Route(r'/create', views.Create, name='create'),
    
    webapp2.Route(r'/challenge/<challenge_id:\d+>/completions', views.Completions, name='completions'),
    webapp2.Route(r'/challenge/<challenge_id:\d+>/discussions', views.Discussions, name='discussions'),
    
    webapp2.Route(r'/challenge/<challenge_id:\d+>/accept', views.Accept, name='accept'),
    webapp2.Route(r'/challenge/<challenge_id:\d+>/reject', views.Reject, name='reject'),

    webapp2.Route(r'/challenge/<challenge_id:\d+>/upload', views.Upload, name='upload'),
    webapp2.Route(r'/challenge/<challenge_id:\d+>/confirm', views.Confirm, name='confirm'),

    webapp2.Route(r'/challenge/<challenge_id:\d+>', views.Detail, name='detail'),

    webapp2.Route(r'/file/<file_id:\d+>', views.ServeFile, name='serve_file')
], debug=True)

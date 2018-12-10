from google.appengine.api import users

class Authnz:
    def __init__(self):
        pass

    def check_logged_in(self):
        """
        Returns a tuple indicating whether the user is logged in, and the url to change that status.
        """
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            logout_url = users.create_logout_url('/')
            return True, logout_url,
        else:
            login_url = users.create_login_url('/')
            return False, login_url,
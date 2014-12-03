import pyramid_httpauth


def get_user_password(login):
    """Get the password of the specified user.
    Called by pyramid_httpauth.
    """

    # TODO Implement.

    return 'test'


def setup(config):
    """Setup HTTP auth - to be called when the app starts."""

    class Hacked_HttpAuthPolicy(pyramid_httpauth.HttpAuthPolicy):
        """Rename the "WWW-Authenticate" header of 401 HTTP responses so
        browsers ignore it but clients still get it, so they can provide their
        own auth form. Probably not entirely legit...
        """
        def login_required(self, request):
            ret = super(Hacked_HttpAuthPolicy, self).login_required(request)
            for index, header in enumerate(ret.headerlist):
                if header[0] == 'WWW-Authenticate':
                    header = list(header)
                    header[0] = 'X-WWW-Authenticate'
                    ret.headerlist[index] = tuple(header)
            return ret
    pyramid_httpauth.HttpAuthPolicy = Hacked_HttpAuthPolicy

import urllib
import urllib2
import urlparse

#try:
import simplejson
#except ImportError:
#    # Have django or are running in the Google App Engine?
#    from django.utils import simplejson

class Error(RuntimeError):
    """Generic exception class."""

    def __init__(self, message='OAuth error occured.'):
        self._message = message

    @property
    def message(self):
        """A hack to get around the deprecation errors in 2.6."""
        return self._message

    def __str__(self):
        return self._message

class Client(object):
    """ Client for OAuth 2.0 'Bearer Token' """
    redirect_uri = None
    auth_uri = None
    redeem_uri = None
    refresh_uri = None
    user_agent = None
    scope = None

    def __init__(self, client_id, client_secret=None, access_token=None,
                 refresh_token=None, timeout=None):

        if not client_id:
            raise ValueError("Client_id must be set.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self.access_token = access_token
        self.refresh_token = refresh_token

    def authorization_url(self, auth_uri=None, redirect_uri=None, scope=None,
                          state=None, access_type='offline', approval_prompt=None):
        """ Get the URL to redirect the user for client authorization """
        if redirect_uri is None:
            redirect_uri = self.redirect_uri
        if auth_uri is None:
            auth_uri = self.auth_uri
        if scope is None:
            scope = self.scope

        params = {'client_id' : self.client_id,
                  'redirect_uri' : redirect_uri,
                  'response_type' : 'code',
                 }
        if scope:
            params['scope'] = scope

        if state:
            params['state'] = state

        if access_type:
            # defaults to 'offline' which requests a refresh_token too
            params['access_type'] = access_type

        if approval_prompt:
            params['approval_prompt'] = approval_prompt

        return '%s?%s' % (auth_uri, urllib.urlencode(params))

    def redeem_code(self, redeem_uri=None, redirect_uri=None, code=None,
        scope=None):
        """Get an access token from the supplied code """

        # prepare required args
        if code is None:
            raise ValueError("Code must be set.")

        if redirect_uri is None:
            redirect_uri = self.redirect_uri

        if redeem_uri is None:
            redeem_uri = self.redeem_uri

        if scope is None:
            scope = self.scope

        data = {
            'client_id': self.client_id,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type' : 'authorization_code',
        }

        if self.client_secret:
            data['client_secret'] = self.client_secret

        if scope is not None:
            data['scope'] = scope

        body = urllib.urlencode(data)

        headers = {'Content-type' : 'application/x-www-form-urlencoded'}

        if self.user_agent:
            headers['user-agent'] = self.user_agent

        # use _request here so we don't try to refresh_token if it fails
        try:
            response = self._request(redeem_uri, body=body, method='POST',
                headers=headers
            )
        except urllib2.HTTPError as e:
            print redeem_uri
            print headers
            print body
            print e.readlines()
            raise

        if response.code != 200:
            raise Error(response.read())

        response_args = simplejson.loads(response.read())

        error = response_args.pop('error', None)

        if error is not None:
            raise Error(error)

        self.access_token = response_args['access_token']

        # refresh token is optional
        self.refresh_token = response_args.get('refresh_token', '')

        return self.access_token, self.refresh_token

    def refresh_access_token(self, refresh_uri=None, refresh_token=None):
        """  Get a new access token from the supplied refresh token """

        if refresh_uri is None:
            refresh_uri = self.refresh_uri

        if refresh_token is None:
            refresh_token = self.refresh_token

        # prepare required args
        args = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type' : 'refresh_token',
        }
        body = urllib.urlencode(args)

        headers = {'Content-type' : 'application/x-www-form-urlencoded'}
        if self.user_agent:
            headers['user-agent'] = self.user_agent

        # use _request here so it doesn't retry on HTTPError
        response = self._request(refresh_uri, method='POST', body=body, headers=headers)

        if response.code != 200:
            raise Error(response.read())

        response_args = simplejson.loads(response.read())

        self.access_token = response_args['access_token']
        # server may or may not supply a new refresh token
        self.refresh_token = response_args.get('refresh_token', self.refresh_token)
        return self.access_token, self.refresh_token

    def _request(self, uri, body=None, headers=None, method='GET'):
        if method == 'POST' and not body:
            raise ValueError('POST requests must have a body')

        request = urllib2.Request(uri, body, headers)
        response = urllib2.urlopen(request, timeout=self.timeout)

        return response

    def request(self, uri, body, headers, method='GET'):
        """ perform a HTTP request using OAuth authentication.
            If the request fails because the access token is expired it will
            try to refresh the token and try the request again.
        """
        headers['Authorization'] = 'Bearer %s' % self.access_token

        try:
            response = self._request(uri, body=body, headers=headers, method=method)
        except urllib2.HTTPError as e:
            if 400 <= e.code < 500 and e.code != 404:
                # any 400 code is acceptable to signal that the access token is expired.
                self.refresh_access_token()
                headers['Authorization'] = 'Bearer %s' % self.access_token
                response = self._request(uri, body=body, headers=headers, method=method)
            else:
                raise

        if response.code == 200:
            return simplejson.loads(response.read())

        raise ValueError(response.read())

class GooglAPI(Client):
    #user_agent = 'python_oauth2_client'
    # OAuth API
    auth_uri = 'https://accounts.google.com/o/oauth2/auth'
    redeem_uri = 'https://accounts.google.com/o/oauth2/token'
    refresh_uri = 'https://accounts.google.com/o/oauth2/token'
    scope = 'https://www.googleapis.com/auth/urlshortener'
    # data API
    api_uri = 'https://www.googleapis.com/urlshortener/v1/url'

    def shorten(self, long_url):
        data = simplejson.dumps({'longUrl' : long_url})
        headers = {'Content-Type': 'application/json'}
        json_d = self.request(self.api_uri, data, headers, 'POST')
        return json_d['id']

    def stats(self, short_url):
        params = {'shortUrl': short_url,
                  'projection' : 'ANALYTICS_CLICKS',
                 }
        stat_url = self.api_uri + '?' + urllib.urlencode(params)
        headers = {'Content-Type': 'application/json'}
        return self.request(stat_url, None, headers)

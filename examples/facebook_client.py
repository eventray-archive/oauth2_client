import urlparse
import oauth2_client

FACEBOOK_APP_ID = ''
FACEBOOK_APP_SECRET = ''

redirect_url = 'http://localhost/'
client = oauth2_client.FacebookAPI(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)

print "cut-n-paste the following URL to start the auth dance",
print client.authorization_url(redirect_uri=redirect_url)
print "and copy the resulting link below"
answer = raw_input()

query_str = urlparse.urlparse(answer).query
params = urlparse.parse_qs(query_str, keep_blank_values=True)
code = params['code'][0]

access_token, refresh_token = client.redeem_code(code=code,
    redirect_uri=redirect_url
)

print 'access_token', access_token
print 'refresh_token', refresh_token

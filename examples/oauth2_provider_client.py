import urlparse
import oauth2_client

client_id = 'sontek.net'

class OAuth2Client(oauth2_client.Client):
    auth_uri = 'http://0.0.0.0:6543/authorize'
    redeem_uri = 'http://0.0.0.0:6543/token'
    redirect_uri = 'http://0.0.0.0:6543/callback'

client = OAuth2Client(client_id)

print "cut-n-paste the following URL to start the auth dance",
print client.authorization_url()
print "and copy the resulting link below"
answer = raw_input()

query_str = urlparse.urlparse(answer).query
params = urlparse.parse_qs(query_str, keep_blank_values=True)
code = params['code'][0]
access_token, refresh_token = client.redeem_code(code=code)

print 'access_token', access_token
print 'refresh_token', refresh_token

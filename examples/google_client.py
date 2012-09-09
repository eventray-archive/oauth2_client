client_id = '724177387809.apps.googleusercontent.com'
client_secret = 'SeLv02KkjKazY7_vYon4eWft'
auth_url = 'https://accounts.google.com/o/oauth2/auth'
access_url = 'https://accounts.google.com/o/oauth2/token'
scope = 'https://www.googleapis.com/auth/urlshortener'
redirect_url = 'http://localhost/'

import urlparse
import oauth2_client
client = oauth2_client.GooglAPI(client_id, client_secret)
print "cut-n-paste the following URL to start the auth dance",
print client.authorization_url(redirect_uri=redirect_url)
print "and copy the resulting link below"
answer = raw_input()

query_str = urlparse.urlparse(answer).query
params = urlparse.parse_qs(query_str, keep_blank_values=True)
code = params['code'][0]
access_token, refresh_token = client.redeem_token(code=code)

# make a short url
short_url = client.shorten('http://example.com')
print short_url
# get stats
print client.stats(short_url)

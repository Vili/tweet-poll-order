import json
import urllib.parse
import requests
from requests.auth import AuthBase
from datetime import datetime

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
DEBUG = False

url = f"https://api.twitter.com/labs/2/tweets/search?query="

headers = {
    "Accept-Encoding": "gzip"
}

# Generates a bearer token with consumer key and secret via https://api.twitter.com/oauth2/token.
class BearerTokenAuth(AuthBase):
    def __init__(self, consumer_key, consumer_secret):
        self.bearer_token_url = "https://api.twitter.com/oauth2/token"
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.bearer_token = self.get_bearer_token()

    def get_bearer_token(self):
        response = requests.post(
            self.bearer_token_url,
            auth=(self.consumer_key, self.consumer_secret),
            data={'grant_type': 'client_credentials'},
            headers={'User-Agent': 'LabsRecentSearchQuickStartPython'})

        if response.status_code is not 200:
            raise Exception("Cannot get a Bearer token (HTTP %d): %s" % (response.status_code, response.text))

        body = response.json()
        return body['access_token']

    def __call__(self, r):
        r.headers['Authorization'] = f"Bearer %s" % self.bearer_token
        r.headers['User-Agent'] = 'LabsResearchSearchQuickStartPython'
        return r

# Script starts here.

#Create Bearer Token for authenticating with recent search.
bearer_token = BearerTokenAuth(CONSUMER_KEY, CONSUMER_SECRET)

#Retrieve next_token from file
next_token = None
with open('next_token.txt', 'r') as next_token_file:
  next_token = next_token_file.read()
  if len(next_token) == 0:
    next_token = None
if DEBUG:
    print("Using next_token:", next_token)

#Construct query
query = f"%23poll -is:retweet -has:images -has:videos&expansions=attachments.poll_ids&max_results=100"
if next_token != None:
    query += "&next_token=" + next_token
if DEBUG:
    print("Query:", query)

#Make a GET request to the Labs recent search endpoint.
response = requests.get(url + query, auth=bearer_token, headers = headers)

if response.status_code is not 200:
    raise Exception(f"Request returned an error: %s %s" % (response.status_code, response.text))

#Display the returned Tweet JSON.
parsed = json.loads(response.text)
if DEBUG:
    pretty_print = json.dumps(parsed, indent=2, sort_keys=True)
    print (pretty_print)

#Save the next_token for the next time the script is run
next_token = None
try:
    next_token = parsed['meta']['next_token']
except:
    print("No next_token returned")
with open('next_token.txt', 'w') as next_token_file:
  if next_token == None:
    next_token_file.write("")
  else:
    next_token_file.write(next_token)
if DEBUG:
    print("Saved next_token:", next_token)

#Append poll data to csv file
with open('polls.csv','a') as csv_file:
  for poll in (parsed['includes']['polls']):
    csv_row = str(datetime.now()) + "," + str(next_token) + "," + str(poll['id']) + "," + str(len(poll['options']))
    for option in (poll['options']):
      csv_row += "," + str(option['votes'])
    csv_file.write(csv_row + '\n')
    if DEBUG:
        print(csv_row)

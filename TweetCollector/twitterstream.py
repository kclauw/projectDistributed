import oauth2 as oauth
import urllib2 as urllib
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
import re
import csv


api_key = "MFLZmhylmM8ULVia639mC1EJO"
api_secret = "M72GjbYc22SzX0nBkd62NcofN9KbLraITa01C7Ith0BscgAEHC"
access_token_key = "935578525326888961-epg3NX7tFH0iZZr8KOmf3zhapfII5JC"
access_token_secret = "UDmvBciJXZqNV6isvVKrtTnR4yMlbt6CrV27UWsEie1kC"
_debug = 0

oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=api_key, secret=api_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = "GET"


http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
def twitterreq(url, method, parameters):
  req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             token=oauth_token,
                                             http_method=http_method,
                                             http_url=url, 
                                             parameters=parameters)

  req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

  headers = req.to_header()

  if http_method == "POST":
    encoded_post_data = req.to_postdata()
  else:
    encoded_post_data = None
    url = req.to_url()

  opener = urllib.OpenerDirector()
  opener.add_handler(http_handler)
  opener.add_handler(https_handler)

  response = opener.open(url, encoded_post_data)

  return response


def extract_hash_tags(s):
  return set([re.sub(r"#+", "#", k) for k in set([re.sub(r"(\W+)$", "", j, flags = re.UNICODE) for j in set([i for i in text.split() if i.startswith("#")])])])



def fetchsamples(limit):
  
  tweets = []
  url = "https://stream.twitter.com/1.1/statuses/sample.json?geocode=-122.995004,-67.799695,49.893813"
  parameters = []
  response = twitterreq(url, "GET", parameters)

  tweets = []


  for index,line in enumerate(response):
    tweets.append(line.strip())
    if index == limit+1:
        break

  return tweets
   


def preProcess(tweets):
  #Pre-processing
  special = ['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}','#']
  determiners = ["the","a","an","another","for","nor","but","or","yet","so","in","under","towards","before"]
  stop = set(stopwords.words('english'))
  stop.update(determiners)
  stop.update(special) 
  tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
  tweets = [tknzr.tokenize(item.lower()) for item in tweets]
  return tweets

def extractTweets(tweets):
  hashtags = []
  for sentence in tweets:
    for word in sentence:
        if word.startswith('#') and len(word) > 4:
          hashtags.append(word[1:])
  return hashtags


if __name__ == '__main__':

  #Retrieve tweets
  tweets = fetchsamples(25000)

  tweets = preProcess(tweets)
  hashtags = extractTweets(tweets) 
 

  with open('tweets.csv', 'wb') as tweetFile:
    wr = csv.writer(tweetFile, quoting=csv.QUOTE_ALL)
    wr.writerow(hashtags)


  

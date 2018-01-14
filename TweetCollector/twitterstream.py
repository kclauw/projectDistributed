import oauth2 as oauth
import urllib2 as urllib
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from twokenize import tokenize
from emoticons import analyze_tweet
import argparse
import twokenize

import re
import csv
import json


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

def fetchsamples(limit):
  
  tweets = []
  url = "https://stream.twitter.com/1.1/statuses/filter.json?locations=-122.995004,32.323198,-67.799695,49.893813&lang=en"
  parameters = []
  response = twitterreq(url, "GET", parameters)

  tweets = []
  it=0
  #Fetch sample as a JSON object
  for index,line in enumerate(response):
    tweet_object = json.loads(line.strip())
    if 'text' in tweet_object:
      tweet = json.loads(line.strip())["text"]
      it+=1
      print(tweet)
    tweets.append(tweet)
    if index == limit+1:
        break

  return tweets
   

#Extract the hashtags from the text
def extractHashtags(tweets):
  hashtags = []
  for sentence in tweets:
    for word in sentence.split():
      if word[0] == "#":
        filtered_tag = " ".join(re.findall("[a-zA-Z]+", word))
        hashtags.append(filtered_tag.lower())

  return hashtags

#Tokenize the tweets and remove words containing hashtags or httptags
def tokenizeTweets(tweets):
    total_tweets = []
    filter_prefix_set = ('@', 'http', 'www')
    # filter for english
    for status in tweets:
        tokenized = tokenize(status)
        # remove http tags and hashtags
        words = [re.sub(r'[^\w\s]','', word).lower() for word in tokenized if not word.startswith(filter_prefix_set)]
        if words:
            total_tweets.append(words)

    return total_tweets


#Preprocess the data by removing stop words and determiners
def processTweets(tweets):

    determiners = ["the","a","an","another","for","nor","but","or","yet","so","in","under","towards","before","or","im"]
    stop = set(stopwords.words('english'))
    stop.update(determiners)
    words = []
    for tweet in tweets:
      for word in tweet:
        if not word in stop and len(word) > 1:
          words += words

    return words





if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('--n', type=int,
    help='The amount of tweets to be received')


  #Retrieve the raw tweets
  tweets = fetchsamples(parser.parse_args().n)  

  #Extract the hashtags from the tweets
  hashtags = extractHashtags(tweets) 

  #Tokenize the tweets
  tweets = tokenizeTweets(tweets)

  #Preprocess
  tweets = processTweets(tweets)

  
  #Write results to file
  with open('tweets.csv', 'wb') as tweetFile:

    for word in tweets:
      w = word.lower()
      if w != "":
        wr = csv.writer(tweetFile)
        wr.writerow([word])

  with open('hashtags.csv', 'wb') as tagFile:
    for tag in hashtags:
      wr = csv.writer(tagFile)
      wr.writerow([tag])
  

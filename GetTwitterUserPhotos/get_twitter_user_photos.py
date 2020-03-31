import pandas as pd
import sys
from datetime import datetime, date, timedelta
import twint
import requests
from bs4 import BeautifulSoup
import re
import wget
import os

def get_img_tweets_df(username, since, until=(date.today() + timedelta(days=1)).strftime('%Y-%m-%d')):
    '''
    Given
        username, the username of the Twitter account to pull photos from
        since, the start date of the date range you wish to pull from
        until, the end date, specified as the day after, the date you wish to pull from, tomorrow by default (optional)
    Return
        tweets_df, dataframe of twint output describing tweets with images from this username for the specified date range
    '''
    
    # check first to see if the username is valid, then if each date is valid, then if the date range is valid
    if requests.get('https://www.twitter.com/' + username).status_code == 404:
        raise Exception('Please enter a valid username.')    
    if not re.match('\d{4}\-\d{2}\-\d{2}', since):
        raise Exception('Please use the date format YYYY-MM-DD for the start date.')
    if not re.match('\d{4}\-\d{2}\-\d{2}', until):
        raise Exception('Please use the date format YYYY-MM-DD for the end date.')
    if datetime.strptime(since, '%Y-%m-%d') >= datetime.strptime(until, '%Y-%m-%d'):
        raise Exception('Please enter a valid date range (the start date must be earlier than the end date, or tomorrow).')
    
    # configure and run the twint search for the tweets associated with the username and save to a dataframe
    c = twint.Config()
    c.Since = since
    c.Until = until
    c.Username = username
    c.Pandas = True
    c.Filter_retweets = True
    c.Images = True
    c.Hide_output=True
    twint.run.Search(c)
    tweets_df = twint.storage.panda.Tweets_df
    
    # check if there are any tweets with imags to download and if so, print out how many
    if len(tweets_df) == 0:
        raise Exception('Nothing to download.')
    print(f'Collected {len(tweets_df)} tweets with images from {username}')
    
    return tweets_df

def dl_images(tweets):
    '''
    Given
        tweets, dataframe of twint output describing tweets with images
    Download images from the given tweets into the current directory (of this script)
    '''
    
    # get the urls for each tweet
    tweet_links = tweets['link'].tolist()
    
    # for each tweet, get url of image to download and then download it
    for i, tweet in enumerate(tweet_links):
        response = requests.get(tweet)
        page = response.text
        soup = BeautifulSoup(re.sub('<!--|-->', '', page), 'html5lib')
        imgs = soup.find_all('img', {'src': re.compile("^https://pbs.twimg.com/media")})
        for img in imgs:
            img_name = img['src'].split('/')[-1].split('?')[0]
            if not os.path.exists(os.path.join(os.getcwd(), img_name)):
                wget.download(img['src'], bar=None)
        if i+1 == len(tweet_links) or (i+1) % 5 == 0:
            print(f'Downloaded all images from tweet {i+1} of {len(tweet_links)}')

# first make sure the correct number of arguments are specified, namely the username and the start of the date range
# if so, then get the tweets for the username and then download the images from the tweets if there is anything download
if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print('Please specify command in the following format [script file] [username] [start date] [end date (optional)]')
    else:
        try:
            if len(sys.argv) < 4:
                tweets = get_img_tweets_df(sys.argv[1], sys.argv[2])
            else:
                tweets = get_img_tweets_df(sys.argv[1], sys.argv[2], sys.argv[3])
        except Exception as e:
            print(e)
        else:
            dl_images(tweets)
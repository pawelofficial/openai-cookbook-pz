
import os 
from requests_oauthlib import OAuth1Session
import tweepy
import dotenv
dotenv.load_dotenv()



#os.environ['API_KEY'] = 'xxx'
#os.environ['API_SECRET']='xxx'
#os.environ['BEARER_TOKEN']='xx%xxx%xxx'
#os.environ['ACCESS_TOKEN']='x-xx'
#os.environ['ACCESS_TOKEN_SECRET']='xxxx'
#
#os.environ['CLIENT_SECRET']='6O-xx-xxx'
#os.environ['CLIENT_ID']='xxxx'


def prep_tweet(s):
    words=s.split(' ')
    tweets=[]
    tweet=''
    j=1
    N=len(s)//250
    for word in words:
        tweet+=word+' '
        if len(tweet)>=250:
            if N>1:
                tweet+=f' {j}/{N}'
            tweets.append(tweet)
            tweet=''
            j+=1
    tweets.append(tweet)
    return tweets
    

def send_tweet(tweet_text,reply_id=None):
    consumer_key = os.getenv('API_KEY')
    consumer_secret =os.getenv('API_SECRET')
    access_token = os.getenv('ACCESS_TOKEN')
    access_token_secret =os.getenv('ACCESS_TOKEN_SECRET')
    bearer_token=os.getenv('BEARER_TOKEN')
    # Authenticate to Twitter
    client = tweepy.Client(consumer_key=consumer_key,
                    consumer_secret=consumer_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                    bearer_token=bearer_token)
    # Send tweet
    #tweet_text='Political complexities and outside interests often transform regulatory agencies meant to protect consumers into agencies protecting existing firms. #EconomicComplexities #RegulatoryAgencies'
    #tweet_text=''.join(['a' for a in range(280)])
    tweet_text=tweet_text.replace('"','')
    print(tweet_text)
    try:
        if reply_id is not None:
            response=client.create_tweet(text=tweet_text
                                     ,in_reply_to_tweet_id= reply_id
                                     )
        else:
            response=client.create_tweet(text=tweet_text)
            
        print("Tweet sent successfully!")
        

        return response.data['id']
    except Exception as e:
        print(f"Error sending tweet: {e}")
        return None
    

    

import os 
import openai as oa 
import requests 
import json 
import random 
from twitter import send_tweet,prep_tweet
import time 
import dotenv

dotenv.load_dotenv()

#os.environ['OPENAI_API_KEY']='sk-xxxx'
OPENAI_API_KEY=os.environ['OPENAI_API_KEY']
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
dumps_dir = os.path.join(current_dir, 'book_dumps')


def completion_request(s,prompt=''):
    url = "https://api.openai.com/v1/chat/completions"
    in_language ='in Polish language'
    prompt=f"Please extract a singble valuable excerpt of information or strong opinions from below piece of text and put it into a tweet of around 500 characters {in_language}, don't add any hashtags."
    model='gpt-3.5-turbo-0613'
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": f"{prompt}\n{s}"}],
        "temperature": 0.2
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    output=response.json()['choices'][0]['message']['content']
    return response.json() ,output


def read_text(delete_file=False):
    files=os.listdir(dumps_dir)
    r=random.randint(0,len(files)-1)
    fp=os.path.join(dumps_dir,files[r])
    with open(fp,'r',encoding='utf-8') as f:
        s=f.read()
    if delete_file:
        os.remove(os.path.join(fp))
            
    return s 



if __name__=='__main__':
    s=read_text()                   # get text from flatfile 
    r,o=completion_request(s)       # do completions on openai
    tweets=prep_tweet(o)            # parse text into tweets 
    #tweets.reverse()                # reverse tweets
    id=None                         # send tweets in a thread 
    for t in tweets:    
        if id is None:
            id=send_tweet(t)
        else:
            send_tweet(t,reply_id=id)



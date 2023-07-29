import os 
import openai as oa 
import requests 
import json 
import random 
from twitter import send_tweet,prep_tweet
import time 
import dotenv
from newspaper import Article,fulltext

dotenv.load_dotenv()

#os.environ['OPENAI_API_KEY']='sk-xxxx'
OPENAI_API_KEY=os.environ['OPENAI_API_KEY']
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
dumps_dir = os.path.join(current_dir, 'book_dumps')

def check_models():
    url = "https://api.openai.com/v1/models"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    response = requests.request("GET", url, headers=headers)
    d=json.loads(response.text)
    d=d['data']
    models=[m['id'] for m in d]
    return d,models 


def completion_request(s,prompt=''):
    url = "https://api.openai.com/v1/chat/completions"
    in_language =''
    prompt=f"Extract key information from text above and write them down in  better english."
    model='gpt-3.5-turbo-0613'
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": f"{s}\n{prompt}"}],
        "temperature": 0.2
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    output=response.json()['choices'][0]['message']['content']
    return response.json() ,output


# reads link from a file nearby 
def get_links():
    with open('./all_links.txt','r') as f:
        links=f.readlines()
    filters=['sql-reference']
    links=[l for l in links if not any([f in l for f in filters])]    
    return links 

# gets text behing the link 
def get_text(links):
    r=random.randint(0,len(links)-1)
    url=links[r].replace('.html','' ).strip()
    article = Article(url)
    article.download()
    article.parse()
    text=article.text.split('\n\n')
    return text, url







if __name__=='__main__':
    d,m=check_models()
    print(d)
    print(m)
    exit(1)


if __name__=='__main__':
    links=get_links()               # get links from flatfile
    s,url=get_text(links)                   # get text from flatfile 
    
    r,o=completion_request(s)       # do completions on openai
    print(s)
    print('-----')
    print(o)
    tweets=prep_tweet(o)            # parse text into tweets 
    tweets+=[url]
    #tweets.reverse()                # reverse tweets
    id=None                         # send tweets in a thread 
    for t in tweets:    
        if id is None:
            id=send_tweet(t)
        else:
            send_tweet(t,reply_id=id)



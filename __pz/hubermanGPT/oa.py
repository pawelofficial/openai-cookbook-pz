import os 
import openai as oa 
import requests 
import json 
import random 

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
    #prompt=f"Please extract a singble valuable excerpt of information or strong opinions from below piece of text and put it into a tweet of around 500 characters {in_language}, don't add any hashtags."
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
    try:
        output=response.json()['choices'][0]['message']['content']
    except:
        output=f'something went wrong {response.stat} '
        output=''
    return response.json() ,output


def oa_chat(question,prompt='',chat_history=[]):
    url = "https://api.openai.com/v1/chat/completions"
    #prompt=f"Please extract a singble valuable excerpt of information or strong opinions from below piece of text and put it into a tweet of around 500 characters {in_language}, don't add any hashtags."
    model='gpt-3.5-turbo-0613'
    context={'role': 'system', 'content': prompt}   # context prompt 
    chat_history=[d for d in chat_history]          # chat history 
    q={'role': 'user', 'content': question}         # current question 

    messages=[context,*chat_history,q]
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    try:
        output=response.json()['choices'][0]['message']['content']
    except:
        output=f'something went wrong {response.status_code}  {response.text} '
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




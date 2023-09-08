import dotenv
import os 
import requests
import json 
from url_to_text import * 
dotenv.load_dotenv()

#os.environ['OPENAI_API_KEY']='sk-xxx'
OPENAI_API_KEY=os.environ['OPENAI_API_KEY']
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
dumps_dir = os.path.join(current_dir, 'book_dumps')


def shoot(url=None):
    
    url = url or  "https://api.openai.com/v1/models"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    response = requests.request("GET", url, headers=headers)
    
    return response
    




def completion_request(s,prompt=None):
    url = "https://api.openai.com/v1/chat/completions"
    
    if prompt is None:
        prompt=f""
    model='gpt-4-0314'
#    model='gpt-3.5-turbo'
    payload = {
        "model": model,
        "messages": [{"role":"system","content":"""Create five multi-answer (ABCD) exam like questions based on the snowflake documentation the user provided you with, include answers at the end.
                      Don't ask questions like 'what is the subject of text provided' """}
                     ,{"role": "user", "content": f"{s}"}],
        "temperature": 0.7
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    output=response.json()['choices'][0]['message']['content']
    return response.json() ,output


def save_text(s,c=None,url=None,title=None,dir='collaboration'):
    
    d={'url':url,'context':c,'questions':s}
    with open(f'./data/{dir}/QA_{title}.txt','a',encoding='utf-8') as f:
        f.write('\n---------------------------------\n')
        f.write(s)

    with open(f'./data/{dir}/RAW_{title}.txt','a',encoding='utf-8') as f:
        f.write('\n---------------------------------\n')
        f.write(json.dumps(d,indent=4,ensure_ascii=False))


def read_list(fp='./links_lists/collaboration.txt'):
    with open(fp,'r') as f:
        urls=f.read().split('\n')
    return urls


if __name__=='__main__':
    #r=shoot()
    #print(r.text)
    
    #urls=read_list()
    urls=['https://docs.snowflake.com/en/user-guide/security-column-intro']
    DIR='random'
    for url in urls:
        title=url.split('/')[-1]    
        save_text(s=f'QUESTIONS: {title} source: {url}',title=title,dir=DIR)
        t=get_article2(url=url)
        
        chunks=split_article(t,N=1000)
        
        for no in range(0,len(chunks)):
            c1=chunks[no]                                  # WHOLE FIRST CHUNK
            try:
                c2=chunks[no+1].split('. ')[0]             # second chunk up to . 
            except:
                c2=chunks[no]                               # if very last chunk - use whole chunk 
                c1=chunks[no-1][-100:]                      # use previous chunk last 100 chars
            c=f'{c1}{c2}'
            

            j,o=completion_request(s=c)
            save_text(o,c,url,title,dir=DIR)
            #input('wait')


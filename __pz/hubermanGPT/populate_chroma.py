#
#   1. put a lot of data into vector db with enrichment 
#   2. send a query to chat-gpt which will return results from vector db into gpt prompt 
#   3. 
##
import pandas as pd 
import chromadb
from chromadb.config import Settings
from utils import Utils
from oa import completion_request,oa_chat
import logging 
import re 
from ytd import * 
import random 
import requests 
import json 
import time 
import unicodedata
from unidecode import unidecode


def remove_non_alphanumeric(input_string):

    result = re.sub(r'\W+', '', input_string)[:60].replace('_',' ').replace('  ',' ').replace('.','').replace(',','')
    result='_'.join(result.split(' ')[:10])[:60]
    if result[-1]=='_':
        result=result[:-1]
    
    return unidecode(result)




# returns generator of agg df and meta fod a hdf 
def yield_hdf(fp,N=60):
    u=Utils()
    df,meta=u.read_hdf(fp)
    ytd.subs_df=df
    agg_df=ytd.concat_on_time(N=N)
    gen_df=u.yield_df(agg_df,n_rows=1)
    return gen_df,meta 

def oa_enrich_text(txt,prompt):
    try:
        r,o=completion_request(txt,prompt=prompt)
    except:
        print('error in oa_enrich_text')
        r,o='',''
    return r,o

def make_chroma(fp='./huberman_chroma',cor=True):
# 1. create persistent chroma db 
    chroma_client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=fp # Optional, defaults to .chromadb/ in the current directory
        #,metadata={"hnsw:space": "cosine"} # l2 is the default - change distance function 
    ))
    if cor:
        chroma_client.reset()  # destroy whole db 
    #collection = chroma_client.create_collection(name="huberman_all_agg_60")
    #collection = chroma_client.get_or_create_collection(name="huberman_all_agg_60")  # get or create 
    return chroma_client  

def parse_completion(s):
    # Split the text into lines
    lines = s.split('\n')
    
    # Initialize an empty dictionary to hold the parsed data
    parsed_dict = {}
    
    # Loop through the lines
    for line in lines:
        # If the line is not empty
        if line:
            # Find the start and end of the key
            start_key_index = line.find('<') + 1
            end_key_index = line.find('>')
            # Extract the key from the line
            key = line[start_key_index:end_key_index]
            
            # Find the start and end of the value
            start_val_index = line.find('>', end_key_index) + 1
            end_val_index = line.find('<', start_val_index)
            # Extract the value from the line
            value = line[start_val_index:end_val_index].strip()

            # Add the key-value pair to the dictionary
            parsed_dict[key] = value

    return parsed_dict

def parse_completion2(s):
    # Define a regular expression pattern to match
    pattern = r'<(.*?)>(.*?)</\1>'
    matches = re.findall(pattern, s, re.MULTILINE | re.DOTALL)
    # Use a dict comprehension to build a dictionary from the matches
    parsed_dict = {key: value.strip() for key, value in matches}
    return parsed_dict

def parse_completion3(s):
    # Define a regular expression pattern to match pairs of <question> <answer>
    #pattern = r'<question>(.*?)</question>\s*<answer>(.*?)</answer>'
    pattern = r'<question>(.*?)</question>\s*<answer>(.*?)</answer>'
    matches = re.findall(pattern, s, re.MULTILINE | re.DOTALL)

    # Use a list comprehension to build a list of dictionaries from the matches
    parsed_list = [{"question": q.strip(), "answer": a.strip()} for q, a in matches]

    return parsed_list


s='''
<question>What are the benefits of using Ketone IQ?</end_of_question>
<answer>The benefits of using Ketone IQ include increased energy and cognitive focus, the ability to do extended bouts of focused work without getting hungry, and the ability to exercise without having a full stomach. It can be particularly useful for tasks such as preparing for podcasts, research, writing grants, and when there is limited time to eat.</end_of_answer>

<question>Where can one go to try Ketone IQ?</end_of_question>
<answer>To try Ketone IQ, you can go to hvmn.com/huberman and use the code "huberman" to save 20% off.</end_of_answer>

<question>What are the upcoming live events hosted by the speaker?</end_of_question>
<answer>The speaker will be hosting two live events in September of 2023. The first event will take place in Toronto on September 12th, and the second event will take place in Chicago on September 28th. Both events will include a lecture and a question and answer period, focusing on tools and science related to mental health, physical health, and performance.</end_of_answer>

<question>Where can one get early access to tickets for the live events?</end_of_question>
<answer>To get early access to tickets for the live events, you can go to hubermanlab.com/tour and enter the code "huberman".</end_of_answer>

<question>What brain networks are involved in attention?</end_of_question>
<answer>Several different brain networks are involved in attention, including those responsible for suppressing noise and irrelevant stimuli, as well as those involved in focusing on specific tasks or stimuli. The prefrontal cortex, located just behind the forehead, plays a critical role in orchestrating the activity of these networks.</end_of_answer>

<question>Why are stimulant treatments effective for ADHD?</end_of_question>
<answer>Stimulant treatments are effective for ADHD because they target the specific brain networks involved in attention. The prefrontal cortex, which plays a critical role in attention, can be regulated by stimulant medications, helping to improve focus, task switching, and the ability to multitask.</end_of_answer>
'''

#print(parse_completion2(s))
#print(parse_completion3(s))
#exit(1)

def save_d(d,fp):
    with open(fp,'a',encoding='utf-8') as f:
        json.dump(d,f,indent=4)


def append_dict_to_jsonfile(dict_data, filepath):
    # Read the existing data from the file
    try:
        with open(filepath, 'r') as jsonfile:
            try:
                data = json.load(jsonfile)
            except Exception as er:
                # If the file is empty, initialize an empty list
                data = []
    except Exception as err:
        data=[]
        pass 
    
    # Append the new data to the existing data
    data.append(dict_data)

    # Write the data back to the file
    with open(filepath, 'w') as jsonfile:
        json.dump(data, jsonfile)


def validate_collection_name(collection_name,chroma_client):
    collections=list(chroma_client.list_collections())
    if collection_name in collections:
        current_timestamp = int(time.time())
        collection_name=collection_name+f'_{current_timestamp}'
    return collection_name

u=Utils()
ytd=Ytd()
this_logger=u.setup_logger(log_name='test.log')
chroma_client=make_chroma()
collection_names=[]

files=os.listdir('./data/hdfs')
hd_fps=[os.path.join('./data/hdfs',f) for f in files]



for hd in hd_fps:
    gen_df,meta=yield_hdf(fp=hd,N=180)
    collection_name=remove_non_alphanumeric(meta['title'])
    collection_name2=collection_name.replace(' ','_')
    collection = chroma_client.get_or_create_collection(name=collection_name)  # get or create



    j=0
    for df_chunk in gen_df:
        print(f'---------{j} ')
        j+=1
        txt=' '.join(df_chunk['txt'].values)
        r,o=oa_enrich_text(txt,prompt='''extract a viable question and answer from above text in following format: 
                           <question></question>
                           <answer></answer>
                           ''')
        #print(r)
        #print(o)


        dics_l=parse_completion3(o)
        #print(o)
        with open('./data/tmp/completion.txt','a') as f:
            
            f.write(o)
            f.write(json.dumps(meta))
            if dics_l==[]:
                o+='\n above text didnt parse into question and answer with a parsing method'
            f.write(f'\n-------------{j}-------------\n')

        #print(dics_l)

        #input('wait')
        #d1=parse_completion(o)
        #d2=parse_completion2(o)

        meta2={'start_ts':df_chunk['st'].values[0]
              ,'end_ts':df_chunk['en'].values[-1]
              ,'url':meta['url']+f'&t=' + str(u.ts_to_flt(df_chunk['st'].values[0])) +'s'
              ,'title':meta['title']  
              ,'completion':o
              }

        for d in dics_l:   
            d_chroma=d
            d_chroma['source']=meta['url']
            d['meta']=meta2
            if len(d['question'])<10 or len(d['answer'])<10:
                print('sus!')
                append_dict_to_jsonfile(d,f'./data/ds/sus_ds_{collection_name2}.json')    
            else:
                print('ok!')
                append_dict_to_jsonfile(d,f'./data/ds/viable_ds_{collection_name2}.json') 

                prompt='\n\n'.join([f'{k}:\n {v}' for k,v in d_chroma.items()])
                collection.add(documents=prompt,metadatas=[meta],ids=[str(j)])
        
#        if j==2:
#            print('breaking loop')
#            break
    
    

exit(1)
#    append_dict_to_jsonfile(d1,'./data/ds/viable_ds.json')    
#    input('wait')






# 2. create a collection 

start_of_text=''  #'<start_of_text>'
end_of_text=''    #'<end_of_text>'









for fp in hd_fps[:5]:
    df,meta=u.read_hdf(fp)
    print(meta)
    ytd.subs_df=df
    agg_df=ytd.concat_on_time(N=60)
    df=agg_df
    url=meta['url']
    title=meta['title']
if 1: # loop for loading data into chroma
    #df=pd.read_csv('./data/tmp/agg_df.csv')
    gen_df=u.yield_df(df,n_rows=1)
    j=0
    for df_chunk  in gen_df:
        txt=' '.join(df_chunk['txt'].values)
        #_,text_summary=oa_enrich_text(txt,prompt='quickly summarize text below')
        #this_logger.log(msg=f'response json summary : {_}\n',level=logging.INFO)
        #
        #_,text_questions=oa_enrich_text(txt,prompt='what questions below text may answer?')
        #this_logger.log(msg=f'response json questions : {_}\n',level=logging.INFO)        
        #d={'summary_of_text:': text_summary,'questions_for_text:':text_questions,'the_text:':'\n'+start_of_text+'\n'+txt+'\n'+end_of_text+'\n'  }
        d={'the_text:':'\n'+start_of_text+'\n'+txt+'\n'+end_of_text+'\n'  }        
        prompt='\n\n'.join([f'{k}:\n {v}' for k,v in d.items()])
        tss=u.ts_to_flt(df_chunk['st'].values[0])
        meta={'start_ts':df_chunk['st'].values[0],'end_ts':df_chunk['en'].values[-1],'url':url+f'&t={tss}s','title':title  }
        collection.add(documents=prompt,metadatas=[meta],ids=[str(j)])
        this_logger.log(msg=f'prompt : {prompt} \n',level=logging.INFO)


        j+=1


last_id=collection.count()
q=collection.get(ids=[f"1"])
print(q)
exit(1)

def shorten_url(url):
    # replace 'your_bitly_token' with your actual bit.ly token
    headers = {
        'Authorization': 'Bearer your_bitly_token',
        'Content-Type': 'application/json',
    }
    data = {
        "long_url": url
    }
    response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers, json=data)
    link = response.json().get("link", "")
    return link



def get_some(coll):
    last_id=coll.count()-1-2 # last ids are not very relevant 
    id=random.randint(2,last_id) # inclusive 
    q=coll.get(ids=[f"{last_id-1}"])              # get a random text from chroma 
    url=q['metadatas'][0]['url']

    


    
    r,o=oa_enrich_text(q['documents'][0],prompt='quickly summarize text below in 200 character long tweet without hashtags')
    o=o+' '+url
    if len(o)>280:
        print('tweet too long !')
        print(o)
    
    return o ,len(o)




o=get_some(coll=collection)
print(o)

exit(1)

def ask_chroma(q,coll=collection):
    context = coll.query(
        query_texts=[q],
        n_results=1
    )
    ids=context['ids'][0][:]
    return ' '.join(context['documents'][0][:]) ,context, ids # ids is a list 


#a,b,c=ask_chroma('how are you?')
#print(c)
#exit(1)


def strip_chroma_answer(chroma_answer,start_of_text=start_of_text,end_of_text=end_of_text):
    prompt=[]
    bl=False
    for no,line in enumerate(chroma_answer.split('\n')):
        if bl:
            prompt.append(line) 
        if  start_of_text in line:
            bl=True
        if end_of_text in line:
            prompt.pop(-1)
            bl=False
    return '\n'.join(prompt) 

def merge_ids(parent_ids,new_ids):
    new_parent_ids=parent_ids
    for id in new_ids:
        if id not in parent_ids:
            new_parent_ids.append(id)
    return new_parent_ids
    

    
    



question='What percentage increase has Bitcoin experienced since its lows last year?'
prompt,context, ids =ask_chroma(question)
prompt=strip_chroma_answer(prompt)


this_logger.log(msg=f'prompt: {prompt}\n',level=logging.INFO)

chat_history=[]
while True:
    print(prompt)
    question = f'Based on the text above, + {question}'
    _,answer=oa_chat(prompt=prompt,question=question,chat_history=chat_history)
    print(answer)
    chat_history.append({'role': 'system', 'content': 'question asked by user: ' + question})
    chat_history.append({'role': 'system', 'content': 'answer provided by assistant: '+answer})
    
    question=input('>: ')
    

    chroma_prompt,context, new_ids =ask_chroma(question)
    chroma_prompt=strip_chroma_answer(chroma_prompt)
    if new_ids[0] not in ids:
        ids.append(new_ids[0])
    
        prompt += prompt +'....\n' +chroma_prompt
        print('prompt updated')
        print(len(prompt))
        x=prompt.split('\n')
        this_logger.log(msg=f"""updated prompt: {x}""",level=logging.INFO)
        
    if question=='bye':
        exit(1)

    if 'fetch more context:' in question:
        q=question.split('fetch more context:')[1]
        more_context,_=ask_chroma(q)
        chat_history.append({'role': 'system', 'content': more_context})  # context added to chat history 
        print('more context fetched succesfully')
    if 'replace context:' in question:                                    
        q=question.split('replace context:')[1]
        new_context,_=ask_chroma(q)
        prompt=q                                                         # original context replaced 
        print('context replaced succesfully')



this_logger.log(msg=f'prompt: {prompt}\n',level=logging.INFO)


gpt_query=f'{prompt} \n\n Given the text summaries and text itself: {chroma_query}'


this_logger.log(msg=f'gpt_query: {gpt_query}\n',level=logging.INFO)


r,final_answer=oa_enrich_text(gpt_query,prompt='')
final_answer+='\n source:'+source
this_logger.log(msg=f'final_answer: {final_answer}\n',level=logging.INFO)


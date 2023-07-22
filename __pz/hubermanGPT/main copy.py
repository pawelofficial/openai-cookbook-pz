#
#   1. put a lot of data into vector db with enrichment 
#   2. send a query to chat-gpt which will return results from vector db into gpt prompt 
#   3. 
#
import pandas as pd 
import chromadb
from chromadb.config import Settings
from utils import Utils
from oa import completion_request,oa_chat
import logging 
import re 
from ytd import *

u=Utils()
this_logger=u.setup_logger(log_name='test.log')



def oa_enrich_text(txt,prompt):
    r,o=completion_request(txt,prompt=prompt)
    return r,o

# 1. create persistent chroma db 
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./tut2_persistent_chroma" # Optional, defaults to .chromadb/ in the current directory
    #,metadata={"hnsw:space": "cosine"} # l2 is the default - change distance function 
))


# 2. create a collection 
chroma_client.reset()  # destroy whole db 
collection = chroma_client.create_collection(name="subs_tests")
#collection = chroma_client.get_or_create_collection(name="subs_tests")  # get or create 

start_of_text='<start_of_text>'
end_of_text='<end_of_text>'

if 0: # loop for loading data into chroma
    df=pd.read_csv('./data/tmp/agg_df.csv')
    gen_df=u.yield_df(df,n_rows=1)
    j=0
    for df_chunk  in gen_df:
        txt=' '.join(df_chunk['txt'].values)

        
        
        _,text_summary=oa_enrich_text(txt,prompt='quickly summarize text below')
        this_logger.log(msg=f'response json summary : {_}\n',level=logging.INFO)
        
        _,text_questions=oa_enrich_text(txt,prompt='what questions below text may answer?')
        this_logger.log(msg=f'response json questions : {_}\n',level=logging.INFO)
        
        d={'summary_of_text:': text_summary,'questions_for_text:':text_questions,'the_text:':'\n'+start_of_text+'\n'+txt+'\n'+end_of_text+'\n'  }
        
        prompt='\n\n'.join([f'{k}:\n {v}' for k,v in d.items()])
        meta={'start_ts':df_chunk['st'].values[0],'end_ts':df_chunk['en'].values[-1],'url':'unknown'}
        collection.add(documents=prompt,metadatas=[meta],ids=[str(j)])
        this_logger.log(msg=f'prompt : {prompt} \n',level=logging.INFO)
        this_logger.log(msg=f'text quersions: {text_questions} \n',level=logging.INFO)
        this_logger.log(msg=f'text summary: {text_summary}\n',level=logging.INFO)


        j+=1


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


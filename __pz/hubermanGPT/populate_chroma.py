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





urls=[
'www.youtube.com/watch?v=H-XfCl-HpRM'
,'www.youtube.com/watch?v=nm1TxQj9IsQ'
,'www.youtube.com/watch?v=nwSkFq4tyC0'
,'www.youtube.com/watch?v=NAATB55oxeQ'
,'www.youtube.com/watch?v=FFwA0QFmpQ4'
,'www.youtube.com/watch?v=LG53Vxum0as'
,'www.youtube.com/watch?v=hx3U64IXFOY'
,'www.youtube.com/watch?v=uuP-1ioh4LY'
,'www.youtube.com/watch?v=mcPSRWUYCv0'
,'www.youtube.com/watch?v=ntfcfJ28eiU'
,'www.youtube.com/watch?v=XfURDjegrAw'
,'www.youtube.com/watch?v=vA50EK70whE'
,'www.youtube.com/watch?v=hcuMLQVAgEg'
,'www.youtube.com/watch?v=J7SrAEacyf8'
,'www.youtube.com/watch?v=qJXKhu5UZwk'
,'www.youtube.com/watch?v=17O5mgXZ9ZU'
,'www.youtube.com/watch?v=x7qbJeRxWGw'
,'www.youtube.com/watch?v=JPX8g8ibKFc'
,'www.youtube.com/watch?v=xaE9XyMMAHY'
,'www.youtube.com/watch?v=xJ0IBzCjEPk'
,'www.youtube.com/watch?v=GqPGXG5TlZw'
#,'www.youtube.com/watch?v=XLr2RKoD-oY'  # lame norton 
,'www.youtube.com/watch?v=VQLU7gpk_X8'
,'www.youtube.com/watch?v=ObtW353d5i0'
,'www.youtube.com/watch?v=Mwz8JprPeMc'
,'www.youtube.com/watch?v=w9MXqXBZy9U'
,'www.youtube.com/watch?v=JVRyzYB9JSY'
,'www.youtube.com/watch?v=aXvDEmo6uS4'
,'www.youtube.com/watch?v=VRvn3Oj5r3E'
,'www.youtube.com/watch?v=rW9QKc-iFoY'
,'www.youtube.com/watch?v=gbQFSMayJxk'
,'www.youtube.com/watch?v=xmhsWAqP_0Y'
,'www.youtube.com/watch?v=p3JLaF_4Tz8'
,'www.youtube.com/watch?v=Xu1FMCxoEFc'
,'www.youtube.com/watch?v=DtmwtjOoSYU'
,'www.youtube.com/watch?v=2XGREPnlI8U'
,'www.youtube.com/watch?v=hFL6qRIJZ_Y'
,'www.youtube.com/watch?v=GzvzWO0NU50'
,'www.youtube.com/watch?v=QmOF0crdyRU'
,'www.youtube.com/watch?v=77CdVSpnUX4'
,'www.youtube.com/watch?v=9tRohh0gErM'
,'www.youtube.com/watch?v=E7W4OQfJWdw'
,'www.youtube.com/watch?v=oUu3f0ETMJQ'
,'www.youtube.com/watch?v=poOf8b2WE2g'
,'www.youtube.com/watch?v=iMvtHqLmEkI'
,'www.youtube.com/watch?v=8IWDAqodDas'
,'www.youtube.com/watch?v=KVjfFN89qvQ'
,'www.youtube.com/watch?v=HXzTbCEqCJc'
,'www.youtube.com/watch?v=31wjVhCcI5Y'
,'www.youtube.com/watch?v=oC3fhUjg30E'
,'www.youtube.com/watch?v=oC3fhUjg30E'
,'www.youtube.com/watch?v=RgAcOqVRfYA'
,'www.youtube.com/watch?v=n9IxomBusuw'
,'www.youtube.com/watch?v=Wcs2PFz5q6g'
,'www.youtube.com/watch?v=GLgKkG44MGo'
,'www.youtube.com/watch?v=t1F7EEGPQwo'
,'www.youtube.com/watch?v=dFR_wFN23ZY'
,'www.youtube.com/watch?v=Ze2pc6NwsHQ'
,'www.youtube.com/watch?v=BwyZIWeBpRw'
,'www.youtube.com/watch?v=gMRph_BvHB4'
,'www.youtube.com/watch?v=PctD-ki8dCc'
,'www.youtube.com/watch?v=15R2pMqU2ok'
,'www.youtube.com/watch?v=ouCWNRvPk20'
,'www.youtube.com/watch?v=azb3Ih68awQ'
,'www.youtube.com/watch?v=VAEzZeaV5zM'
,'www.youtube.com/watch?v=IAnhFUUCq6c'
,'www.youtube.com/watch?v=pq6WHJzOkno'
,'www.youtube.com/watch?v=ncSoor2Iw8k'
,'www.youtube.com/watch?v=UF0nqolsNZc'
,'www.youtube.com/watch?v=EQ3GjpGq5Y8'
,'www.youtube.com/watch?v=XcvhERcZpWw'
,'www.youtube.com/watch?v=RBK5KLA5Jjg'
,'www.youtube.com/watch?v=szqPAPKE5tQ'
,'www.youtube.com/watch?v=099hgtRoUZw'
,'www.youtube.com/watch?v=dzOvi0Aa2EA'
,'www.youtube.com/watch?v=IOl28gj_RXw'
,'www.youtube.com/watch?v=tkH2-_jMCSk'
,'www.youtube.com/watch?v=a9yFKPmPZ90'
,'www.youtube.com/watch?v=OadokY8fcAA'
,'www.youtube.com/watch?v=UNCwdFxPtE8'
,'www.youtube.com/watch?v=T65RDBiB5Hs'
,'www.youtube.com/watch?v=UChhXiFPRgg'
,'www.youtube.com/watch?v=m_OazsImOiI'
,'www.youtube.com/watch?v=7YGZZcXqKxE'
,'www.youtube.com/watch?v=h2aWYjSA1Jc'
,'www.youtube.com/watch?v=DTCmprPCDqc'
,'www.youtube.com/watch?v=DkS1pkKpILY'
,'www.youtube.com/watch?v=LVxL_p_kToc'
,'www.youtube.com/watch?v=yb5zpo5WDG4'
,'www.youtube.com/watch?v=uxZFl4BDOGk'
,'www.youtube.com/watch?v=uXs-zPc63kM'
,'www.youtube.com/watch?v=Nr5xb-QCBGA'
,'www.youtube.com/watch?v=gXvuJu1kt48'
,'www.youtube.com/watch?v=X4QE6t-MkYE'
,'www.youtube.com/watch?v=q1Ss8sTbFBY'
,'www.youtube.com/watch?v=Z7MU6zrAXsM'
,'www.youtube.com/watch?v=wTBSGgbIvsY'
,'www.youtube.com/watch?v=lsODSDmY4CY'
,'www.youtube.com/watch?v=TO0WUTq5zYI'
,'www.youtube.com/watch?v=LTGGyQS1fZE'
,'www.youtube.com/watch?v=xjEFo3a1AnI'
,'www.youtube.com/watch?v=6I5I56uVvLw'
,'www.youtube.com/watch?v=iw97uvIge7c'
,'www.youtube.com/watch?v=vZ4kOr38JhY'
,'www.youtube.com/watch?v=O640yAgq5f8'
,'www.youtube.com/watch?v=KPlJcD-o-4Q'
,'www.youtube.com/watch?v=__RAXBLt1iM'
,'www.youtube.com/watch?v=-wIt_WsJGfw'
,'www.youtube.com/watch?v=tLS6t3FVOTI'
,'www.youtube.com/watch?v=ycOBZZeVeAc'
,'www.youtube.com/watch?v=zEYE-vcVKy8'
,'www.youtube.com/watch?v=O1YRwWmue4Y'
,'www.youtube.com/watch?v=CyDLbrZK75U'
,'www.youtube.com/watch?v=uak_dXHh6s4'
,'www.youtube.com/watch?v=GVRDGQhoEYQ'
,'www.youtube.com/watch?v=oNkDA2F7CjM'
,'www.youtube.com/watch?v=CGjdgy0cwGk'
,'www.youtube.com/watch?v=UIy-WQCZd4M'
,'www.youtube.com/watch?v=BMTt8gSl13s'
,'www.youtube.com/watch?v=juD99_sPWGU'
,'www.youtube.com/watch?v=x4m_PdFbu-s'
,'www.youtube.com/watch?v=q37ARYnRDGc'
,'www.youtube.com/watch?v=S8nPJU9xkNw'
,'www.youtube.com/watch?v=CDUetQMKM6g'
,'www.youtube.com/watch?v=at37Y8rKDlA'
,'www.youtube.com/watch?v=7R3-3HR6-u4'
,'www.youtube.com/watch?v=ufsIA5NARIo'
,'www.youtube.com/watch?v=cp9GXl9Qk_s'
,'www.youtube.com/watch?v=K-TW2Chpz4k'
,'www.youtube.com/watch?v=ulHrUVV3Kq4'
,'www.youtube.com/watch?v=6ZrlsVx85ek'
,'www.youtube.com/watch?v=3ZGItIAUQmI'
,'www.youtube.com/watch?v=0RYyQRQFgFk'
,'www.youtube.com/watch?v=uWV9a3zEaL4'
,'www.youtube.com/watch?v=cS7cNaBrkxo'
,'www.youtube.com/watch?v=eIxVfln02Ss'
,'www.youtube.com/watch?v=x3MgDtZovks'
,'www.youtube.com/watch?v=fcxjwA4C4Cw'
,'www.youtube.com/watch?v=sxgCC4H1dl8'
,'www.youtube.com/watch?v=dicP_kA-RA0'
,'www.youtube.com/watch?v=S8jWFcDGz4Y'
,'www.youtube.com/watch?v=slUCmZJDXrk'
,'www.youtube.com/watch?v=doupx8SAs5Y'
,'www.youtube.com/watch?v=FE0lTEUa7EY'
,'www.youtube.com/watch?v=_ltcLEM-5HU'
,'www.youtube.com/watch?v=LYYyQcAJZfk'
,'www.youtube.com/watch?v=RI112zW8GDw'
]

u=Utils()
ytd=Ytd()
this_logger=u.setup_logger(log_name='test.log')

files=os.listdir('./data/hdfs')
hd_fps=[os.path.join('./data/hdfs',f) for f in files]
print(len(files))
print(len(urls))

# loop for downloading - if something is too short download it manualy through ytd 
#for no,f in enumerate(files):
#    fp=os.path.join('./data/hdfs',f)
#    df,meta=u.read_hdf(fp)
#    file_urls.append(meta['url'])
#    if len(df)<300:
#        print(f)
#        os.remove(fp)
#        #wf__download_subs(url=meta['url'])
#        #fp=os.path.join('./data/hdfs',f)
#        #df,meta=u.read_hdf(fp)
#        print(meta,len(df))
#        #input('wait')
#print(len(files))
#print(len(urls))
#print(set(urls)-set(file_urls))
#print(set(file_urls)-set(urls))





def oa_enrich_text(txt,prompt):
    r,o=completion_request(txt,prompt=prompt)
    return r,o

# 1. create persistent chroma db 
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./huberman_chroma" # Optional, defaults to .chromadb/ in the current directory
    #,metadata={"hnsw:space": "cosine"} # l2 is the default - change distance function 
))

# 2. create a collection 
chroma_client.reset()  # destroy whole db 
collection = chroma_client.create_collection(name="huberman_all_agg_60")
collection = chroma_client.get_or_create_collection(name="huberman_all_agg_60")  # get or create 



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


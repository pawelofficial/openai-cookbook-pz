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

#£oop for downloading - if something is too short download it manualy through ytd 
file_urls=[]
for no,f in enumerate(files):
    fp=os.path.join('./data/hdfs',f)
    df,meta=u.read_hdf(fp)
    file_urls.append(meta['url'])
    if len(df)<300:
        print(f)
        os.remove(fp)
        #wf__download_subs(url=meta['url'])
        #fp=os.path.join('./data/hdfs',f)
        #df,meta=u.read_hdf(fp)
        print(meta,len(df))
        #input('wait')
print(len(files))
print(len(urls))
print(set(urls)-set(file_urls))
print(set(file_urls)-set(urls))





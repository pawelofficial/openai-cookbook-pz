
import inspect 
import logging 
import chardet
import json 
import pandas as pd 
import numpy as np 
import re 
import os
import logging
import subprocess 
import inspect 
import re 
import pandas as pd 
# i will never learn how to do the imports in python 



class Utils:
    def __init__(self) -> None:
        self.BASIC_FORMAT="%(levelname)s:%(name)s:%(message)s"
        self.BASIC_FORMAT="%(levelname)s:%(name)s:%(asctime)s:%(message)s"
        self.level=logging.INFO
        self.mode='w'
        self.formatter= logging.Formatter(self.BASIC_FORMAT)
        self.logs_dir='logs'
        self.cur_dir=os.path.dirname(os.path.abspath(__file__))
        self.logger=None
        self.log_fp=None    # log filepath 
        self.log_name=None  # log name
        

    def setup_logger(self,log_name='log',level=None,mode=None,formatter=None):
        if self.logger is not None:
            self.log_variable(msg=f'closing {self.log_name} recreating a new log  {log_name}')
            self.close_logger()

        level=  level or self.level 
        mode=mode or self.mode
        formatter=formatter or self.formatter
        self.log_name=log_name
        self.log_fp = self.path_join(self.logs_dir, log_name)
        handler = logging.FileHandler(self.log_fp, mode=mode, encoding="utf-8") 
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)
        self.logger.propagate = False
        self.log_variable( msg=f'setting up {log_name} at {self.log_fp} ')
        return self.logger 
        
    def log_variable(self, msg,lvl=None, **kwargs ):
        if self.logger is None:
            print('no logger')
            return 
        lvl=lvl or self.level
        s=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}'

        
        self.logger.log(self.level,s)
        s=''
        for k,v in kwargs.items():
            s+= f'\n{k} : {v}'
        self.logger.log(lvl, f'{msg} {s} '   )

    def path_join(self,*args) -> str:
        if self.logger is not None:
            self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')   
        try:
            return os.path.join(self.cur_dir, *args)
        except TypeError:
            #logging.error("Arguments must be strings.")
            raise ValueError("All arguments to path_join must be strings.") from None
            return None
        
    def close_logger(self):
        if self.logger is None:
            self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')

        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def subprocess_run(self,l,logger=None,**kwargs):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ',l=l)
        q=subprocess.run(l,capture_output=True, text=True,shell=True,**kwargs)  
        self.log_variable(msg='subprocess run',l=l,stdout=q.stdout,stderr=q.stderr,returncode=q.returncode)
        if q.returncode !=1:
            self.log_variable(msg='error in executing subprocess run',lvl=logging.ERROR)
        
        return q.stdout,q.stderr,q.returncode

    def make_dir(self,fp):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if not os.path.exists(fp):
            os.makedirs(fp)
            self.log_variable(msg=f'creating {fp} ')

    def remove_dir(self,fp):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if os.path.exists(fp):
            os.rmdir(fp)
            self.log_variable(msg=f'removed {fp} ')
    def build_url(self,id):
        prefix='https://www.youtube.com/watch?v='
        return prefix+id

    def parse_url(self,url) -> dict:
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        id_reg=r'v=([^&]+)'
        channel_reg=r'ab_channel=(.*)|(\@.*)'
        vid_reg=r'\&ab_channel.*'
        vid_reg=r'watch\?v=([aA0-zZ9]+)'
        base_reg=r'(.*com/)'    
        id=re.findall(id_reg,url)
        #print('id: ', id)
        channel=re.findall(channel_reg,url)
        #print('channel: ',channel)
        vid_url=re.findall(vid_reg,url)
        base_url=re.findall(base_reg,url)[0]
        channel_url = None 
        vid_url = None 
        if id==[]:
            id=None 
        else:
            id=id[0]
        if channel==[]:
            channel=None
        else:
            channel=max(channel[0])
        if id is not None:
            vid_url=base_url+'watch?v='+id 
        if channel is not None:
            channel_url = base_url+channel+'/videos'

        d={"id":id
           ,"channel":channel
           ,"vid_url":vid_url
           ,"channel_url":channel_url
           ,"orig_url":url }
        return d

    def df_insert_d(self,df: pd.DataFrame, d : dict,clear_d=True ):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        df.loc[len(df)]=d 
        if clear_d:
            for k,v in d.items():
                d[k]=None
                
    def dump_df(self,df,fp=None,dir_fp=None,fname=None,to_html=False,**kwargs):
     
        if 'split_rows' in kwargs.keys():
            split_rows=kwargs['split_rows']
            self.dump_df_split_rows(df,fp=fp,split_rows=split_rows)
        else:
            self.dump_df_csv(df,fp=fp,dir_fp=dir_fp,fname=fname,to_html=to_html) 
    # dumps df of number of rows into separate files
    def dump_df_split_rows(self,df,fp=None,split_rows=1):
        N=len(df)
        j=0
        while True:
            tmp_df=df.iloc[j:j+split_rows]
            temp_fp=fp.split('.')[0]+'_'+str(j)+'.csv'
            self.dump_df_csv(tmp_df,fp=temp_fp)
            j=j+split_rows
            if j>=N:
                break
    
    def dump_df_csv(self,df,fp=None,dir_fp=None,fname=None,to_html=False):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if fp is None:
            fp=self.path_join(dir_fp,fname)
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if not to_html:
            x=df.to_csv(fp,index=False)
        else:
            df.to_htmp(fp,index=False)

    def dump_hdf(self,df,fp=None,dir_fp=None,fname=None,meta_dic={}):
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if fp is None:
            fp=self.path_join(dir_fp,fname)
        self.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')

        metadata_df=pd.DataFrame(meta_dic,index=[0])
        print(meta_dic)
        fp=fp.replace('.h5','')+'.h5'
        with pd.HDFStore(f'{fp}') as hdf:
            hdf.put('data', df, format='table', data_columns=True)
            hdf.put('metadata', metadata_df, format='table', data_columns=True)

    def yield_df(self,df,n_rows=1):
        N=len(df)
        j=0
        while True:
            tmp_df=df.iloc[j:j+n_rows]
            yield tmp_df
            j=j+n_rows
            if j>=N:
                break


    def parse_stdout(self,stdout):
        out=[]
        for l in stdout.splitlines():
            out.append(l.strip())
        return out
    
    def read_csv(self,df_fp):
        return pd.read_csv(df_fp)
    
    def read_hdf(self,hdf_fp,keys=['data','metadata']):
        with pd.HDFStore(hdf_fp) as hdf:
            if keys is None:
                keys = hdf.keys()
            df = hdf[keys[0]]
            metadata_df = hdf[keys[1]]

        # Convert the metadata dataframe back to a dict
        metadata = metadata_df.to_dict('records')[0]
        return df,metadata
    
    def ts_to_flt(self,st,to_int=True,prepend=0):
        h, m, s = map(float, st.split(':'))
        out= h * 3600 + m * 60 + s + prepend 
        if out <0:
            out=0
        if to_int:
            return int(out)
        return out 
    def flt_to_ts(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return "{}:{:02d}:{:02d}".format(h, m, s)

    def move_col_to_end(self,df,column_to_move):

        columns = [col for col in df.columns if col != column_to_move]
        columns.append(column_to_move)
        return df[columns]

    def calculate_url_ts_old(self,st,url,key='vid_url',prepend=-5,to_link=True):
        ff=self.ts_to_flt(st,prepend=prepend)
        d=self.parse_url(url)
        if to_link:
            if ff==0:
                return f'<a href="{url}">link</a>' 
            ts_url = f'{d[key]}#t={ff}'
            return f'<a href="{ts_url}">link</a>'
        
        if ff==0:
            return url 
        ts_url=f'{d[key]}#t={ff}'
        return ts_url

    def calculate_url_ts(self, st, url, key='vid_url', prepend=-3, to_link=True):
        ff = self.ts_to_flt(st, prepend=prepend)
        d = self.parse_url(url)
        ts_url = url if ff==0 else f'{d[key]}#t={ff}'
        return f'<a href="{ts_url}"  target="_blank" >link</a>' if to_link else ts_url


class Ytd:
    def __init__(self) -> None:
        # objects 
        self.utils = Utils()
        self.logger=self.utils.setup_logger(log_name='ytd.log')
        
        # settings
        self.tmp_dir=self.utils.path_join(self.utils.cur_dir,'data','tmp')  # used by download_subs,parse_subs
        self.subs_lang='eu-en-US'# 'en-en-US'                                                 # used by download_subs                                  
        self.subs_format='json3'                                            # used by download_subs
        
        # results
        self.vid_title=None                                                 # set by get_url_title  |
        self.raw_fp=None                                                    # set by download_subs  | used by parse_subs
        self.subs_fp=None                                                   # set by parse_subs     |
        self.subs_df=None                                                   # set by parse_subs     |
        
    # gets url title 
    def get_url_title(self,url):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        vid_url=self.utils.parse_url(url)['vid_url'] 
        l=["yt-dlp","--skip-download",vid_url,"--get-title"]
        stdout, stderr,returncode =self.utils.subprocess_run(l) 
        title=stdout.replace(' ','_').replace('|','').strip() 
        title=''.join([c for c in title if c.isalnum() or c in ('_') ])
        self.vid_title=title
        return title 
    
    # checks if lang is available 
    def check_available_langs(self,url):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')   
        vid_url=self.utils.parse_url(url)['vid_url']
        l=["yt-dlp","--skip-download",vid_url,"--list-subs"]    
        stdout, stderr,returncode =self.utils.subprocess_run(l) 
        langs_d={}
        isavailable = False 
        for line in stdout.splitlines():
            if 'json3' not in line: # skip lines that do not specify language 
                continue
            line=[i.strip() for i in line.split(' ') if i!='']
            ytlang=line[0]
            lang_long=line[1] # not used 
            formats_available=line[1:]
            langs_d[ytlang]=[formats_available]
        isavailable=any([self.subs_lang == k for k in langs_d.keys()]) # check if lang is available
        return isavailable, langs_d
    
    # downloads subs 
    def download_subs(self,url,out_dir=None):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')   
        vid_url=self.utils.parse_url(url)['vid_url'] 
        if out_dir is None:
            out_dir=self.tmp_dir
        if self.vid_title is None:
            fname=f'raw_subs_' 
        else:
            fname=f'raw_subs_{self.vid_title}_'
        self.raw_fp=self.utils.path_join(out_dir,fname)
#        self.raw_fp=self.utils.path_join(self.tmp_dir,fname)+f'.{self.subs_lang}.{self.subs_format}'
        l=["yt-dlp","-o", f"{self.raw_fp}","--skip-download"]
        l+=[vid_url,"--force-overwrites",
            "--no-write-subs",  
            "--write-auto-sub",
            "--sub-format",self.subs_format,
            "--sub-langs",self.subs_lang] # en.* might be better here 
        stdout, stderr,returncode  =self.utils.subprocess_run(l) 
        self.raw_fp=self.utils.path_join(out_dir,fname)+f'.{self.subs_lang}.{self.subs_format}'
        return self.raw_fp
        
    def parse_subs(self,dump_df=True,fname='subs_df',output_dir_fp=None):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if self.raw_fp is None:
            self.utils.log_variable(lvl=logging.ERROR, msg='raw_fp is None cant parse subs')
            return None
        cols=['no','st','en','st_flt','en_flt','dif','pause_flt','txt']
        subs_d={k:None for k in cols}  
        
        with open(self.raw_fp,'rb') as f:                       # getting encoding 
            encoding=chardet.detect(f.read())['encoding']
            
        with open(self.raw_fp,'r',encoding=encoding) as f:     # read data to list 
            pld=json.load(f)['events']                  
        
        pld=[i for i in pld if 'segs' in i.keys()]      # remove items without text 
        tmp_df=pd.DataFrame(columns=subs_d.keys())      # declare temporary df 
        
        for no,p in enumerate(pld):                     # insert data to temporary df 
            subs_d=self._parse_json_pld(p=p,no=no)
            txt=subs_d['txt'].strip()
            if txt not in ['']:                         # don't write empty rows 
                self.utils.df_insert_d(df=tmp_df,d=subs_d)
        tmp_df['dif']=np.round(tmp_df['en_flt']-tmp_df['st_flt'],2 ) # calculate dif col 
        self.subs_df=tmp_df
        if dump_df:
            fname=fname.replace('.csv','')+'.csv'
            output_dir_fp=output_dir_fp or self.tmp_dir
            self.utils.dump_df(df=self.subs_df,dir_fp=output_dir_fp,fname=fname)
            self.subs_fp=self.utils.path_join(output_dir_fp,fname)
        self.subs_df=tmp_df    
        return self.subs_df,self.subs_fp
        
        # concats df on time 
    def concat_on_time(self, subs_df=None, N=60):
        # Determine whether the input dataframe was provided or not
        external = False if subs_df is None else True
        subs_df = self.subs_df if subs_df is None else subs_df

        # Define the function that will be applied to 'txt' column
        def replace_double_spaces(s):
            return s.replace('  ', ' ')

        # Apply the function to 'txt' column
        for no, row in subs_df.iterrows():
            subs_df.loc[no, 'txt'] = replace_double_spaces(row['txt'])

        # Define the condition for '_concat_on_condition' method
        cond = lambda prev_row, cur_row:  cur_row['st_flt'] // N == prev_row['st_flt'] // N

        # Define the function for '_concat_on_condition' method
        def concatenate_rows(prev_row, cur_row):
            prev_row['txt'] += ' ' + cur_row['txt']
            prev_row['en_flt'] = cur_row['en_flt']
            prev_row['en'] = cur_row['en']
            return prev_row, cur_row, True

        # Apply '_concat_on_condition' method
        subs_df = self._concat_on_condition(subs_df=subs_df, cond=cond, func=concatenate_rows)

        # Calculate 'dif' column
        subs_df['dif'] = np.round(subs_df['en_flt'] - subs_df['st_flt'], 2 )

        # Update self.subs_df if the input dataframe was not provided
        if not external:
            self.subs_df = subs_df

        return subs_df


    def _concat_on_condition(self,subs_df,cond = None,func=None ):
        df=subs_df.copy(deep=True)
        no=1                            
        df['index']=df.index
        while no<len(df):
            #self._calculate_pause_to_next(df=df)
            df['dif']=np.round(df['en_flt']-df['st_flt'],2 ) # calculate dif col 
            prev_row=df.iloc[no-1].to_dict()
            cur_row=df.iloc[no].to_dict()
            c=cond(prev_row,cur_row)
            if not c:
                no+=1
            else:
                prev_row,cur_row,bl = func(prev_row,cur_row)
                df.loc[prev_row['index']]=prev_row
                df.loc[cur_row['index']]=cur_row
                if bl:
                    df.drop(cur_row['index'],inplace=True)
                    no-=1
                no+=1
        df.drop('index',axis=1,inplace=True)
        return df
        
    def _clean_txt(self,s : str,**kwargs): # cleans up string 
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        
        custom_d={k:v for k,v in kwargs.items()}
        translation_table = str.maketrans({'\xa0': ' ', '\n': ' ', '\t': ' ', '\r': ' ','\u200b':''})
        translation_table.update(custom_d)
        translation_table[ord("\n")] = " "
        clean_string = s.translate(translation_table)
        return clean_string.strip().replace('  ',' ')
        
    def _parse_json_pld(self,p,no):
        subs_d={}
        subs_d['no']=no
        subs_d['st_flt']=np.round(int(p['tStartMs'])/1000.0,2)
        if 'dDurationMs' not in p.keys():       # some rows don't have this key 
            subs_d['en_flt']=subs_d['st_flt']+0 # so much math 
        else:
            subs_d['en_flt']=np.round(subs_d['st_flt']+int(p['dDurationMs'])/1000.0,2)
            
        subs_d['st']=self._flt_to_ts(ff=subs_d['st_flt'])
        subs_d['en']=self._flt_to_ts(ff=subs_d['en_flt'])
        txt=' '.join([d['utf8'] for d in p['segs'] if d['utf8']!='\n']  ).replace('  ',' ').strip()
        
        rs=[r'\[.*\]',r"^,|,$",r"^\[\w+",r"[aA-zZ]*\]"] # clean up stuff from yt 
        for r in rs:
            txt=re.sub(r,'',txt).replace('[','').replace(']','') # 
        subs_d['txt']=self._clean_txt(txt)
        return subs_d    
    
    def _flt_to_ts(self,ff : float): # float to timestamp string
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        if ff != ff: # float is nan:
            ff=0
        hh=ff/60/60//1
        mm=(ff-hh*60*60)/60//1
        ss=(ff-hh*60*60-mm*60)//1
        fff=(ff-hh*60*60-mm*60-ss)*1000
        return '{:02d}:{:02d}:{:02d}.{:03d}'.format(int(hh), int(mm), int(ss),int(fff))

    # tessted up to n = 100 
    def scan_channel(self,url,n=10):
        self.utils.log_variable(msg=f'executing {self.__class__.__name__}.{inspect.currentframe().f_code.co_name} ')
        vid_url=self.utils.parse_url(url)['channel_url']   
        l=["yt-dlp","--get-id","--skip-download",vid_url,"--playlist-end", f"{n}"]
        stdout, stderr,returncode =self.utils.subprocess_run(l)
        ids=self.utils.parse_stdout(stdout=stdout)
        urls=[self.utils.build_url(id) for id in ids]
        ds=[self.utils.parse_url(url) for url in urls]
        return ds,urls
    
    ###def scan_channel_scrape(self,url,n=10): # needs this wierd id of a channel 
    ###    d=self.utils.parse_url(url)
    ###    videos = scrapetube.get_channel("KitcoNEWS")
    ###    for video in videos:
    ###        print(video['videoId'])
        
        
def wf__download_subs(url = None):
    """ downloads and parses subs into data tmp directory """
    if url is None:
        url='https://www.youtube.com/watch?v=KvJ2tF7d6yM&ab_channel=DavidLin'
        url='https://www.youtube.com/watch?v=zKVz7A5XBe0&ab_channel=DavidLin'
        url='https://www.youtube.com/watch?v=uuP-1ioh4LY'
        url='www.youtube.com/watch?v=4b6bwcWK6GE'
        url='www.youtube.com/watch?v=XLr2RKoD-oY'
        url='www.youtube.com/watch?v=uuP-1ioh4LY'
    #url='https://www.youtube.com/watch?v=QuTkczqLAU8&t=180s&ab_channel=MindsetRx'
    ytd=Ytd()
    a,b=ytd.check_available_langs(url=url)
#    print(a,b)
#    exit(1)
    ytd.download_subs(url=url)
    ytd.parse_subs()
    subs_df=ytd.subs_df.copy()
    agg_df=ytd.concat_on_time(N=60)
    title=ytd.get_url_title(url=url)
    ytd.utils.dump_df(df=subs_df,fp=ytd.utils.path_join('data','tmp','subs_df.csv'))
    ytd.utils.dump_hdf(df=subs_df,fp=ytd.utils.path_join('data','hdfs',f'subs_df_{title}.h5'),meta_dic={'title':title,'url':url} )
    #print(len(ytd.subs_df))
    #df,meta=ytd.utils.read_hdf(hdf_fp=ytd.utils.path_join('data','hdfs',f'subs_df_{title}.h5'))
    #ytd.utils.dump_df(ytd.subs_df,fp=ytd.utils.path_join('data','tmp','subs_df.csv'))
    #print(title)
    print(len(subs_df))
if __name__=='__main__':
    ytd=Ytd()
    wf__download_subs()
#    ytd.subs_df=ytd.utils.read_csv(df_fp=ytd.utils.path_join('data','tmp','agg_df.csv'))
#    ytd.utils.dump_df_split_rows(ytd.subs_df,fp=ytd.utils.path_join('data','tmp','agg_df.csv'),split_rows=1)
#    print(ytd.subs_df)   
#    wf__download_subs()

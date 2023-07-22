import os
import logging
import subprocess 
import inspect 
import re 
import pandas as pd 
#logging.DEBUG (10)
#logging.INFO (20)
#logging.WARNING (30)
#logging.ERROR (40)
#logging.CRITICAL (50)

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

if __name__=='__main__':
    u=Utils() 
    u.setup_logger(log_name='test.log')
    u.log_variable(msg='test',u_logger=u.logger,mode=u.mode)
    u.close_logger
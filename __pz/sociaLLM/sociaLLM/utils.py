import logging 
import os 
import inspect 

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


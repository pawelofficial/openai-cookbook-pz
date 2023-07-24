import openai as oa 
import dotenv 
dotenv.load_dotenv()
import os 
import requests,json


if __name__ == '__main__':
    from utils import Utils
else:
    from .utils import Utils


class oa:
    def __init__(self) -> None:
        self.utils=Utils()
        self.loggeer=self.utils.setup_logger(log_name='oa.log')
        self.OPENAI_API_KEY=os.environ['OPENAI_API_KEY']
        self.url = "https://api.openai.com/v1/chat/completions"
        self.model='gpt-3.5-turbo-0613'
        self.chat_history=[]
        

    def complete_request(self,s='hello there !',prompt=''):
        message={"role": "user", "content": f"{prompt}{s}"}
        self.chat_history.append(message)
        
        payload = {
                "model": self.model,
                "messages": self.chat_history,
                "temperature": 0.2
            }
        headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.OPENAI_API_KEY}'
            }
        response = requests.request("POST", self.url, headers=headers, data=json.dumps(payload))

        try:
            output=response.json()['choices'][0]['message']['content']
        except:
            print('something went wrong with completion')
            self.utils.log_variable(msg=f'something went wrong status {response.status_code} ',variable=response.text)
            output=f'something went wrong {response.stat} '
        
        self.chat_history.append({"role": "system", "content": output})
        
        return response.json() ,output
        
    # spins up chat loop with gpt 
    def start_chat(self):
        while True:
            print('welcome to chat, type exit to exit ')
            s=input('s> ')
            r,o=self.complete_request(s)
            print(o)
            if s=='exit':
                break
            else:
                pass
        
        
if __name__=='__main__':
    oa=oa()

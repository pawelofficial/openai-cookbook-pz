from newspaper import Article,fulltext
from bs4 import BeautifulSoup
import time 
import datetime
import requests 

# Specify the article URL

def get_article(url=None):
    url = url or  "https://docs.snowflake.com/en/sql-reference/data-types-semistructured"
    article = Article(url)
    article.download()
    article.parse()
    text=article.text.replace('\n\n','\n') #.split('\n\n')
    t2=article.text
    return text , t2 

def get_article2(url=None):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    soup = BeautifulSoup(response.content, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()

# Get text
    text = " ".join(t.strip() for t in soup.stripped_strings)
    
    #text = soup.get_text().replace('\n\n','\n')
    return text 


def split_article(text,N=500): # splits article into chunks of N characters
    L=len(text)
    st=0 
    chunks=[]
    while True:
        st,en=st,st+N
        c=text[st:en]
        chunks.append(c)
        st=en
        if en>=L:
            break
        
    return chunks 



if __name__=='__main__':
    url='https://other-docs.snowflake.com/en/collaboration/collaboration-listings-about'
    url='https://other-docs.snowflake.com/en/collaboration/provider-listings-reference'
    url='https://docs.snowflake.com/en/sql-reference/sql/create-stage'
    t=get_article2(url)
    
    print(t)


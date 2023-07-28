import requests 
from newspaper import Article,fulltext
import re 

import requests
from bs4 import BeautifulSoup
 
def get_links(url):
    base_url='/'.join(url.split('/')[:-1])+'/'      # removes last part of url

    end_urls=[]
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    urls = []
    for link in soup.find_all('a'):
        urls.append(link.get('href'))
    
    c1= lambda pattern,url: re.search(pattern,url)   # no /fr/sql-reference/commands-account links 
    c2 = lambda str,url: str in url                  # no links to external sites 
        
    pattern = r'\/[a-z]{2}\/'
    pattern2=r'\#'
    pattern3 = r'.*http.*http.*'                          # remove links to other sites 
    # get urls that are .html 
    end_urls=[]
    for url in urls:
        conditions=[c1(pattern,url),c2('http',url),c1(pattern2,url),c2('..',url),c1(pattern3,url)  ] 
        yes_conditions=[c2('.html',url)]
        if not any(conditions) and all(yes_conditions):
            end_urls.append(base_url+url)
    # get urls that are not .html
    not_end_urls=[]
    for url in urls:
        conditions=[c1(pattern,url),c2('https',url),c1(pattern2,url),c2('.html',url)] 
        if not any(conditions):
            not_end_urls.append(url)
    return end_urls

def get_links_recursively(link,links):
    urls=get_links(link)                # get urls 
    try:
        print('yay',len(links),links[-1])
    except Exception as e:
        pass
    # check if urls are already in links    
    
    new_urls = [url for url in urls if url not in links] 
    if not new_urls:
        return 
    
    links += new_urls
    for url in new_urls:
        get_links_recursively(url,links)
        
    
    
        
#s='https://docs.snowflake.com/user-guide/http://docs.aws.amazon.com/AmazonS3/latest/dev/object-lifecycle-mgmt.html'
#s='yay 37 https://docs.snowflake.com/user-guide/http://docs.aws.amazon.com/AmazonS3/latest/dev/object-lifecycle-mgmt.html'
#pattern3 = r'.*http.*http.*' 
#r=re.search(pattern3,s)
#
#if r:
#    print('yay')
#exit(1)


base_urls=[]

base_urls.append('https://docs.snowflake.com/en/sql-reference/commands-account')

url=base_urls[0]
url='https://docs.snowflake.com/guides-overview'



links=[]
link=url
get_links_recursively(link,links)

print(links)

with open('./all_links.txt','w') as f: 
    f.write('\n'.join(links))



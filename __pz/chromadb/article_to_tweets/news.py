from newspaper import Article,fulltext
from oa import completion_request,read_text
from read_mail import readEmails
from twitter import send_tweet,prep_tweet
import time 
import datetime

# Specify the article URL
url = "https://cointelegraph.com/news/everything-that-s-happened-with-celsius-and-alex-mashinsky-so-far"


while True:
    # get last email ! 
    date,subject,url,date_object=readEmails()
    now = datetime.datetime.now(datetime.timezone.utc)
    dt=now-date_object
    dt=dt.total_seconds()
    
    if dt>60: # 50 requests per 24hours thank you Elon ! 
        time.sleep(10)
        print('waiting')
    else:
        print('tweeting!')
        # Use the Article class to download and parse the article
        article = Article(url)
        # Download and parse the article
        article.download()
        article.parse()

        text=article.text.split('\n\n')
        r,clickbait_title=completion_request(text,prompt='Write a short clickbait title for this article in Polish.')
        clickbait_title='🧵 ' + clickbait_title.replace('"','') + '🧵 ' 


        chunks=[text[:len(text)//2],text[len(text)//2:] ]
        chunks2=[' '.join(c) for c in chunks]

        prompt='Can you summarize this piece of text in three distinct paragraphs in Polish?'

        texts=[]
        for c in chunks2:
            r,o=completion_request(c,prompt=prompt)
            texts+=o.split('\n\n')

        texts=' '.join(texts)
        tweets=prep_tweet(texts)

        tweets.reverse()


        for t in tweets:
            print(t)

        id=send_tweet(clickbait_title)
        for t in tweets:    
            send_tweet(t,reply_id=id)
            time.sleep(1)
        time.sleep(120)


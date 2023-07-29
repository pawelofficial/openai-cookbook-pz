import os 
import openai as oa 
import requests 
import json 
import random 
import time 
import dotenv
from newspaper import Article,fulltext
from PIL import Image
from PIL import Image, ImageDraw
import random


dotenv.load_dotenv()

#os.environ['OPENAI_API_KEY']='sk-xxxx'
OPENAI_API_KEY=os.environ['OPENAI_API_KEY']
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
dumps_dir = os.path.join(current_dir, 'book_dumps')

def check_models():
    url = "https://api.openai.com/v1/models"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    response = requests.request("GET", url, headers=headers)
    d=json.loads(response.text)
    d=d['data']
    models=[m['id'] for m in d]
    return d,models 

def convert_image(fp):
    img=Image.open(fp)
    rgba_image = img.convert('RGBA')
    rgba_image.save('tmp.png')
    return open('tmp.png','rb').read(), './tmp.png'
    
def add_transparent_circle(image_path,r=0.3):
    # Open the image and ensure it's RGBA
    with Image.open(image_path) as img:
        img = img.convert('RGBA')

        # Create a draw object
        draw = ImageDraw.Draw(img)

        # Random circle size and position
        radius = int(img.size[1]*r)  # Ensure circle is within image bounds
        center = (
            random.randint(radius, img.size[0] - radius),  # x-position
            random.randint(radius, img.size[1] - radius)   # y-position
        )

        # Draw a transparent circle on the image
        draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=(0, 0, 0, 0))

        # Save the image
        img.save('output_with_transparent_blob.png', 'PNG')
        return open('output_with_transparent_blob.png','rb').read(), 'output_with_transparent_blob.png'



def edit_image(s='',prompt=''):
    url = "https://api.openai.com/v1/images/edits"
    prompt=f"add white noise to this image"
    base_fp='./images/p4.jpg'
    mask_fp='./images/p4.jpg'
    
    base,base_fp=convert_image(base_fp)                               # convert image to valid format 
    mask,mask_fp=convert_image(mask_fp)
    
    base,base_fp=add_transparent_circle(base_fp)                       # add transparent blobs 
    headers = {
    "Authorization":  f'Bearer {OPENAI_API_KEY}'
    }
    data={
        'prompt':'fill transparent blob with spacex rocket'
        ,'n':'1'
    }
    files={
        'image':base
    }
    
    response = requests.request("POST", url, headers=headers, data=data,files=files)
    print(response.status_code)
    print(response.text)
#    return response.json() ,output


# reads link from a file nearby 
def get_links():
    with open('./all_links.txt','r') as f:
        links=f.readlines()
    filters=['sql-reference']
    links=[l for l in links if not any([f in l for f in filters])]    
    return links 

# gets text behing the link 
def get_text(links):
    r=random.randint(0,len(links)-1)
    url=links[r].replace('.html','' ).strip()
    article = Article(url)
    article.download()
    article.parse()
    text=article.text.split('\n\n')
    return text, url







if __name__=='__main__':
    fp='./images/inputs/barbecue.png'
    
    edit_image()
    exit(1)

if __name__=='__main__':
    links=get_links()               # get links from flatfile
    s,url=get_text(links)                   # get text from flatfile 
    
    r,o=completion_request(s)       # do completions on openai
    print(s)
    print('-----')
    print(o)
    tweets=prep_tweet(o)            # parse text into tweets 
    tweets+=[url]
    #tweets.reverse()                # reverse tweets
    id=None                         # send tweets in a thread 
    for t in tweets:    
        if id is None:
            id=send_tweet(t)
        else:
            send_tweet(t,reply_id=id)



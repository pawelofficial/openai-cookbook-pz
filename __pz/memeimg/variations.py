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


def convert_image(fp):
    img=Image.open(fp)
    rgba_image = img.convert('RGBA')
    rgba_image.save('tmp.png')
    return open('tmp.png','rb').read(), './tmp.png'
    
def add_transparent_circle(image_path,r=0.1):
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



def variate(s='',prompt=''):
    url = "https://api.openai.com/v1/images/variations"
    base_fp='./images/p3.jpg'

    
    base,base_fp=convert_image(base_fp)                               # convert image to valid format 

    
    headers = {
    "Authorization":  f'Bearer {OPENAI_API_KEY}'
    }
    data={
        'n':'2'
        
    }
    files={
        'image':base
    }

    
    response = requests.request("POST", url, headers=headers, data=data,files=files)
    print(response.status_code)
    print(response.text)
#    return response.json() ,output










if __name__=='__main__':
    fp='./images/inputs/barbecue.png'
    
    variate()
    exit(1)

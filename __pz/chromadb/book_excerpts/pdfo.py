# https://www.askpython.com/python/examples/convert-pdf-to-txt
import PyPDF2
import os
import datetime  



def clear_dir(fp):
    for f in os.listdir(fp):
        os.remove(os.path.join(fp,f))
def dump_string(s,**kwargs):
    ts=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    vals='_'.join([f'{k}_{v}' for k,v in kwargs.items()])
    f=f'zump_{ts}_{vals}.txt'
    fp=os.path.join(dumps_dir,f)
    with open(fp,'w',encoding='utf-8') as f:
        f.write(s)



current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
dumps_dir = os.path.join(current_dir, 'book_dumps')
start_pg=13
end_pg=860
text_len=500

# clear dumps dir 
clear_dir(dumps_dir)
fp=os.path.join(current_dir,'basic_economics.pdf')


# get pdf 
pdffileobj=open(fp,'rb')

#make reader object 
r=PyPDF2.PdfReader(pdffileobj)
 
#This will store the number of pages of this pdf file
num_pages=len(r.pages)
print(num_pages)

text=''
j=0
for i in range(start_pg,end_pg):
    text+=r.pages[i].extract_text()
    if len(text)>text_len:
        dump_string(text,page_start=start_pg,page_end=i)
        j+=1
        text=''
    if j>10:
        pass
#        exit(1)
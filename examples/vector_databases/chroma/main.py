import chromadb

import openai

from typing import List, Iterator
import pandas as pd
import numpy as np
import os
import wget
from ast import literal_eval

from dotenv import load_dotenv
import os

load_dotenv()

# Chroma's client library for Python

os.environ["OPENAI_API_KEY"] = 'sk-xxxx'
#pytho /mnt/c/gh/openai-cookbook-pz/examples/vector_databases/chroma

# I've set this to our new embeddings model, this can be changed to the embedding model of your choice
EMBEDDING_MODEL = "text-embedding-ada-002"
# Ignore unclosed SSL socket warnings - optional in case you get these errors
import warnings

warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning) 

embeddings_url = 'https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip'

# The file is ~700 MB so this will take some time
if 0:
    fp=wget.download(embeddings_url)
    print(fp)
if 0:
    import zipfile
    with zipfile.ZipFile("vector_database_wikipedia_articles_embedded.zip","r") as zip_ref:
        zip_ref.extractall("../data")
    
article_df = pd.read_csv('../data/very_small_vector_database_wikipedia_articles_embedded.csv')



# Read vectors from strings back into a list
article_df['title_vector'] = article_df.title_vector.apply(literal_eval)
article_df['content_vector'] = article_df.content_vector.apply(literal_eval)

# Set vector_id to be a string
article_df['vector_id'] = article_df['vector_id'].apply(str)

article_df.info(show_counts=True)

chroma_client = chromadb.Client() # Ephemeral. Comment out for the persistent version.
# Uncomment the following for the persistent version. 
# import chromadb.config.Settings
# persist_directory = 'chroma_persistence' # Directory to store persisted Chroma data. 
# client = chromadb.Client(
#     Settings(
#         persist_directory=persist_directory,
#         chroma_db_impl="duckdb+parquet",
#     )
# )

from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# Test that your OpenAI API key is correctly set as an environment variable
# Note. if you run this notebook locally, you will need to reload your terminal and the notebook for the env variables to be live.

# Note. alternatively you can set a temporary env variable like this:
# os.environ["OPENAI_API_KEY"] = 'sk-'

if os.getenv("OPENAI_API_KEY") is not None:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print ("OPENAI_API_KEY is ready")
else:
    print ("OPENAI_API_KEY environment variable not found")
    

embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=EMBEDDING_MODEL)

wikipedia_content_collection = chroma_client.create_collection(name='wikipedia_content', embedding_function=embedding_function)
wikipedia_title_collection = chroma_client.create_collection(name='wikipedia_titles', embedding_function=embedding_function)

# Add the content vectors
wikipedia_content_collection.add(
    ids=article_df.vector_id.tolist(),
    embeddings=article_df.content_vector.tolist(),
)

# Add the title vectors
wikipedia_title_collection.add(
    ids=article_df.vector_id.tolist(),
    embeddings=article_df.title_vector.tolist(),
)


def query_collection(collection, query, max_results, dataframe):
    results = collection.query(query_texts=query, n_results=max_results, include=['distances']) 
    df = pd.DataFrame({
                'id':results['ids'][0], 
                'score':results['distances'][0],
                'title': dataframe[dataframe.vector_id.isin(results['ids'][0])]['title'],
                'content': dataframe[dataframe.vector_id.isin(results['ids'][0])]['text'],
                })
    
    return df

title_query_result = query_collection(
    collection=wikipedia_title_collection,
    query="modern art in Europe",
    max_results=10,
    dataframe=article_df
)
df=title_query_result.head()
print(df)
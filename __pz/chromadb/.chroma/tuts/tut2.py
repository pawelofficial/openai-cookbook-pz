# persistent chroma  https://docs.trychroma.com/usage-guide
import chromadb
from chromadb.config import Settings

# 1. create persistent chroma db 
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./tut2_persistent_chroma" # Optional, defaults to .chromadb/ in the current directory
    #,metadata={"hnsw:space": "cosine"} # l2 is the default - change distance function 
))

# 2. create a collection 
chroma_client.reset()  # destroy whole db 
collection = chroma_client.create_collection(name="my_collection")
#collection = chroma_client.get_or_create_collection(name="my_collection")  # get or create 

# 3. add documents to your collection 
collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "my_source"}, {"source": "my_source"}],
    ids=["id1", "id2"]
)

# 4. query chroma ! 
results = collection.query(
    query_texts=["This is a query document"],
    n_results=2
)
if 0:
    print(results)

#5. get chroma timestamp 
hb = chroma_client.heartbeat() # returns a nanosecond heartbeat. Useful for making sure the client remains connected.

# 6. nispect your collections 
x = chroma_client.get_collection(name="my_collection")
if 0:
    print(x)

if 0:
    x=collection.peek() # returns a list of the first 10 items in the collection
    print(x)
if 1:
    x=collection.count() # returns the number of items in the collection
    print(x)
if 0:
    x=collection.modify(name="new_name") # Rename the collection
    
    
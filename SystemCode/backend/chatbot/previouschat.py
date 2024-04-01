import chromadb
import uuid

client = chromadb.Client()
collection = client.get_or_create_collection("previous_chats")


def store_previouschat(prevchat):
    guid = str(uuid.uuid4())
    collection.add(documents=prevchat, ids=guid)

def retrieve_previouschats(query,n_results=3):
    

    results = collection.query(
        query_texts=query,
        n_results=n_results)
    
    return results
import chromadb
import uuid

client = chromadb.PersistentClient(path="./database")
collection = client.get_or_create_collection("previous_chats")


# Function to store previous chat in the collection
def store_previouschat(prevchat, username=None):
    """
    Store previous chat in the collection.
    
    Args:
        prevchat (str): The previous chat to be stored.
        username (str): The username associated with the chat (default is None).
    """
    guid = str(uuid.uuid4())
    if username is None:
        username = "default_user"
    collection.add(documents=prevchat, metadatas={"username": username}, ids=guid)


# Function to retrieve previous chats based on a query
def retrieve_previouschats(query, n_results=5, username=None):
    """
    Retrieve previous chats based on a query.git
    
    Args:
        query (str): The query to search for previous chats.
        n_results (int): The number of results to retrieve (default is 5).
        username (str): The username associated with the chat (default is None).
    
    Returns:
        list: A list of previous chats matching the query.
    """
    if username is None:
        username = "default_user"
    results = collection.query(
        query_texts=query,
        n_results=n_results,
        where={"username": username}
    )
    
    return results 
from tensorflow.python.keras.models import  save_model,load_model
from deepmatch.layers import custom_objects
from db import UserPreference, engine
from sqlalchemy import select
from actions.search import movie_id_to_genre
import tensorflow as tf
import chromadb
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
from utils import logger

pad_sequences = tf.keras.utils.pad_sequences
SEQ_LEN = 50
chroma_client = chromadb.PersistentClient(path="../experiments/chroma_data")
collection = chroma_client.get_or_create_collection("movie_rec_25m-2")



def load_rec_model():
    user_embedding_model = load_model('../experiments/user_emb_25m-3.h5', custom_objects)# load_model,just add a parameter
    return user_embedding_model

user_embedding_model = load_rec_model()



def load_user_preference_for_model(user_id):
    stmt = select(UserPreference).where(UserPreference.user_id==user_id)
    df = pd.read_sql(stmt, engine)
    logger.info(df)
    df["genres"] = df["movie_id"].apply(movie_id_to_genre)
    # model_input = {
    #     "hist_movie_ids": [pad_sequences(df["movie_id"], maxlen=SEQ_LEN, padding='post', truncating='post', value=0).tolist()],
    #     "hist_genres": [pad_sequences(df["genres"], maxlen=SEQ_LEN, padding='post', truncating='post', value=0).tolist()]
    # }
    model_input = {
        "hist_movie_id": pad_sequences(np.array([df["movie_id"].tolist()]), maxlen=SEQ_LEN, padding='post', truncating='post', value=0),
        "hist_genres": pad_sequences(np.array([df["genres"].tolist()]), maxlen=SEQ_LEN, padding='post', truncating='post', value=0),
        "hist_len": np.array([len(df["genres"].tolist())])
    }
    return model_input


def model_recommend(user_id, n_results=10):
    model_input = load_user_preference_for_model(user_id)
    logger.info(model_input)
    user_embs = user_embedding_model.predict(model_input)
    query_result_1 = collection.query(query_embeddings=user_embs[:, 1, :], n_results=n_results)
    query_result_2 = collection.query(query_embeddings=user_embs[:, 0, :], n_results=n_results)
    result_1 = []
    for i,x in enumerate(query_result_1["metadatas"][0]):
        x["distance"] = query_result_1["distances"][0][i]
        result_1.append(x)

    result_2 = []
    for i,x in enumerate(query_result_2["metadatas"][0]):
        x["distance"] = query_result_2["distances"][0][i]
        result_2.append(x)

    results = result_1 + result_2
    logger.info(results)
    op = []
    tmp = set()
    for x in results:
        if x["movie_id"] not in tmp:
            tmp.add(x["movie_id"])
            op.append(x)
        else:
            pass
    
    df = pd.DataFrame(op).sort_values('distance')
    return df

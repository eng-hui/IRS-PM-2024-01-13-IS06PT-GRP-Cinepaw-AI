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
collection = chroma_client.get_or_create_collection("movie_rec")



def load_rec_model():
    user_embedding_model = load_model('../experiments/user_emb.h5', custom_objects)# load_model,just add a parameter
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


def model_recommend(user_id):
    model_input = load_user_preference_for_model(user_id)
    logger.info(model_input)
    user_embs = user_embedding_model.predict(model_input)
    results = [x for x in collection.query(query_embeddings=user_embs[:, 1, :], n_results=5)["metadatas"][0]] + \
    [x for x in collection.query(query_embeddings=user_embs[:, 0, :], n_results=5)["metadatas"][0]]
    return results

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
import os 
file_location = os.path.abspath(__file__)
exp_folder = os.path.join(os.path.dirname(file_location),"..","experiments")    


movies = pd.read_csv(os.path.join(exp_folder,"datasets","ml-25m","xdf.csv"))
movies["movie_id"] = movies["movieId"]
lbe = LabelEncoder()
movies["raw_genres"] = movies["genres"].copy()
#movies["genres"] = movies["genres"].apply(lambda x:x.split("|")[0])
movies["genres"] = lbe.fit_transform(movies["genres"]) + 1

pad_sequences = tf.keras.utils.pad_sequences
SEQ_LEN = 50
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection("movie_rec_0426")


def load_rec_model():
    user_embedding_model = load_model(os.path.join(exp_folder,"user_emb_25m_0402.h5"), custom_objects)# load_model,just add a parameter
    return user_embedding_model

user_embedding_model = load_rec_model()



def load_user_history(user_id):
    stmt = select(UserPreference).where(UserPreference.user_id==user_id)
    df = pd.read_sql(stmt, engine)
    logger.info(df)
    df = pd.merge(df, movies, how="left", on="movie_id")
    return df

def load_user_preference_for_model(user_id):
    stmt = select(UserPreference).where(UserPreference.user_id==user_id)
    df = pd.read_sql(stmt, engine)
    logger.info(df)
    df = pd.merge(df, movies, how="left", on="movie_id")

    # model_input = {
    #     "hist_movie_ids": [pad_sequences(df["movie_id"], maxlen=SEQ_LEN, padding='post', truncating='post', value=0).tolist()],
    #     "hist_genres": [pad_sequences(df["genres"], maxlen=SEQ_LEN, padding='post', truncating='post', value=0).tolist()]
    # }
    model_input = {
        "hist_movie_id": pad_sequences(np.array([df["movie_id"].tolist()]), maxlen=SEQ_LEN, padding='pre', truncating='post', value=0),
        "hist_genres": pad_sequences(np.array([df["genres"].tolist()]), maxlen=SEQ_LEN, padding='pre', truncating='post', value=0),
        "hist_hot": pad_sequences(np.array([df["hot"].tolist()]), maxlen=SEQ_LEN, padding='pre', truncating='post', value=0),
        "hist_grade": pad_sequences(np.array([df["grade"].tolist()]), maxlen=SEQ_LEN, padding='pre', truncating='post', value=0),
        "hist_len": np.array([len(df["genres"].tolist())])
    }
    return model_input
    

def get_user_embedding(user_id):
    model_input = load_user_preference_for_model(user_id)
    logger.info(model_input)
    user_emb = user_embedding_model.predict(model_input)[0]
    return user_emb

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

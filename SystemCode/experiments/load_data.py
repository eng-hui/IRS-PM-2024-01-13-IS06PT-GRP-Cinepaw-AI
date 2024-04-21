import pandas as pd
from deepctr.feature_column import SparseFeat, VarLenSparseFeat
from sklearn.preprocessing import LabelEncoder
from tensorflow.python.keras import backend as K
from tensorflow.python.keras.models import Model
import numpy as np
import random
from tqdm import tqdm
from deepmatch.models import ComiRec, NCF
from deepmatch.utils import sampledsoftmaxloss, NegativeSampler
import tensorflow as tf
import gc

from deepctr.feature_column import DenseFeat

pad_sequences = tf.keras.utils.pad_sequences
SEQ_LEN = 50


def load_25m():
    df = pd.read_csv("./datasets/ml-25m/ratings.csv")
    movies = pd.read_csv("./datasets/ml-25m/movies.csv")

    links_df = pd.read_csv('./datasets/ml-25m/links.csv')
    tags_df = pd.read_csv('./datasets/ml-25m/tags.csv')
    genome_scores_df = pd.read_csv('./datasets/ml-25m/genome-scores.csv')
    genome_tags_df = pd.read_csv('./datasets/ml-25m/genome-tags.csv')

    xdf = df.groupby("movieId").agg({"rating":"mean", "userId":"count"})

    xdf = xdf.reset_index()

    xdf["hot"] = 0
    xdf["grade"] = 0

    # create movie popular feature
    xdf.loc[xdf["userId"]>0, "hot"] = 1
    xdf.loc[xdf["userId"]>100, "hot"] = 2
    xdf.loc[xdf["userId"]>1000, "hot"] = 3
    xdf.loc[xdf["userId"]>10000, "hot"] = 4
    xdf.loc[xdf["userId"]>30000, "hot"] = 5
    xdf.loc[xdf["userId"]>50000, "hot"] = 6

    # create movie rating zone feature
    xdf.loc[xdf["rating"]>1, "grade"] = 1
    xdf.loc[xdf["rating"]>2, "grade"] = 2
    xdf.loc[xdf["rating"]>3, "grade"] = 3
    xdf.loc[xdf["rating"]>4, "grade"] = 4
    xdf.loc[xdf["rating"]>4.5, "grade"] = 5

    movies = pd.merge(movies, xdf)
    del movies["userId"]
    del movies["rating"]

    def get_year(title):
        tmp = title.split("(")[-1].split(")")[0]
        try:
            return int(tmp)
        except:
            return 0

    movies["year"] = movies["title"].apply(get_year)

    data = pd.merge(df,movies, on="movieId")
    data.columns = ["user_id", "movie_id", "rating", "timestamp", "title", "genres", "hot", "grade", "year"]
    return data, movies

def load_1m():
    data_path = "./datasets/"

    unames = ['userId','gender','age','occupation','zip']
    user = pd.read_csv(data_path+'ml-1m/users.dat',sep='::',header=None,names=unames)
    rnames = ['userId','movieId','rating','timestamp']
    ratings = pd.read_csv(data_path+'ml-1m/ratings.dat',sep='::',header=None,names=rnames)
    mnames = ['movieId','title','genres']
    movies = pd.read_csv(data_path+'ml-1m/movies.dat',sep='::',header=None,names=mnames,encoding="unicode_escape")
    xdf = ratings.groupby("movieId").agg({"rating":"mean", "userId":"count"})

    xdf = xdf.reset_index()

    xdf["hot"] = 0
    xdf["grade"] = 0

    # create movie popular feature
    xdf.loc[xdf["userId"]>0, "hot"] = 1
    xdf.loc[xdf["userId"]>100, "hot"] = 2
    xdf.loc[xdf["userId"]>1000, "hot"] = 3
    xdf.loc[xdf["userId"]>10000, "hot"] = 4
    xdf.loc[xdf["userId"]>30000, "hot"] = 5
    xdf.loc[xdf["userId"]>50000, "hot"] = 6

    # create movie rating zone feature
    xdf.loc[xdf["rating"]>1, "grade"] = 1
    xdf.loc[xdf["rating"]>2, "grade"] = 2
    xdf.loc[xdf["rating"]>3, "grade"] = 3
    xdf.loc[xdf["rating"]>4, "grade"] = 4
    xdf.loc[xdf["rating"]>4.5, "grade"] = 5

    movies = pd.merge(movies, xdf)
    del movies["userId"]
    del movies["rating"]

    def get_year(title):
        tmp = title.split("(")[-1].split(")")[0]
        try:
            return int(tmp)
        except:
            return 0

    movies["year"] = movies["title"].apply(get_year)
    # movies.to_csv("./datasets/ml-25m/processed_movies.csv", index=False)

    data = pd.merge(pd.merge(ratings,movies),user)#.iloc[:10000]
    return data, movies

import sqlalchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy import Text, String, Integer, ForeignKey
from sqlalchemy import Column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session
import json
import redis
USER_ID=10000 # tmp later change to true user_id

# tmp
engine = sqlalchemy.create_engine("sqlite:////tmp.db")
Base = declarative_base()

class UserPreference(Base):
    __tablename__ = 'user_preference'
    id = Column(Integer, primary_key=True)
    quote = Column(Text)
    user_id = Column(Integer, nullable=False)
    movie_id = Column(Integer, nullable=False)
    movie_title = Column(Text, nullable=False)
    score = Column(Integer)


class ConversationHistory(Base):
    __tablename__="conversation_history"
    id = Column(Integer, primary_key=True)
    session_key = Column(Text, nullable=False)
    content = Column(Text)
    role = Column(Text)
    blocks = Column(Text)

def save_user_preference(data):
    with Session(engine) as session:
        obj = UserPreference(**data)
        session.add_all([obj])
        session.commit()
        obj_id = obj.id
    return {"status": "ok", "id":obj_id}


def save_msg(msg):
    msg = {
        "session_key": msg.get("session_key"),
        "content": msg.get("content"),
        "role": msg.get("role"),
        "blocks": json.dumps(msg.get("blocks", []))
    }

    with Session(engine) as session:
        obj = ConversationHistory(**msg)
        session.add_all([obj])
        session.commit()
        obj_id = obj.id
    return {"status": "ok", "id":obj_id}


REDIS_HOST = 'localhost'
redis_pool = None
def init_redis():
    import os
    global redis_pool
    print("PID %d: initializing redis pool..." % os.getpid())
    redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=6379, db=0,  decode_responses=True)
init_redis()

def get_redis_conn():
    redis_conn = redis.Redis(connection_pool=redis_pool)
    return redis_conn


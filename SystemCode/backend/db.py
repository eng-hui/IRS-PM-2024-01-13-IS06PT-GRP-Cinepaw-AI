
import sqlalchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy import Text, String, Integer, ForeignKey



# tmp
engine = sqlalchemy.create_engine("sqlite:////tmp.db")
Base = declarative_base()

class UserPreference(Base):
    __tablename__ = 'user_preference'
    id = Column(Integer, primary_key=True)
    quote = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=False)
    movie_id = Column(Integer, nullable=False)

import uvicorn

from app import app
from db import Base, engine

if __name__ == "__main__":
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    uvicorn.run("manage:app", host="0.0.0.0", port=8890, workers=2)

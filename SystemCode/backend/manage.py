import uvicorn

from app import app

if __name__ == "__main__":
    uvicorn.run("manage:app", host="0.0.0.0", port=8890, reload=True)

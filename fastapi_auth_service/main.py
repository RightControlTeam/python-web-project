from fastapi import FastAPI
from uvicorn import run

app = FastAPI()

if __name__ == "__main__":
    run(app, host="localhost", port=8000)


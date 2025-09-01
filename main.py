from fastapi import FastAPI
from db import get_db, Base, engine
from models import User, Transaction

app = FastAPI()

@app.get("/")
def hello_world():
    return {'message': "HELLO WORLD"}




@app.on_event('startup')
def starting_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("Created the database tables.")
    except Exception as e:
        print("Error creating database tables", e)
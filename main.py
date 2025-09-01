from fastapi import FastAPI
from db import get_db, Base, engine
from models import User, Transaction
from routes.users import router as user_router

app = FastAPI()

@app.get("/")
def hello_world():
    return {'message': "HELLO WORLD"}



app.include_router(user_router)

@app.on_event('startup')
def starting_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("Created the database tables.")
    except Exception as e:
        print("Error creating database tables", e)
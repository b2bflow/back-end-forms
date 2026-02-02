from mongoengine import connect
import os

def init_db():
    connect(
        db=os.getenv("MONGO_DB"),
        host=os.getenv("MONGO_URI"),
    )

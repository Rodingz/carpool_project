from fastapi import FastAPI, Query
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from passlib.context import CryptContext
import os
import certifi
import datetime as dt
from routers import user, party

app = FastAPI()

app.include_router(party.router, prefix="/party", tags=["party"])
app.include_router(user.router, prefix="/user", tags=["user"])


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient("mongodb+srv://kevinkim9443:0509@carpool.3bukgzs.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=certifi.where())
    app.database = app.mongodb_client["Carpool"]
    # app.mongodb_client = MongoClient("mongodb+srv://root:root@cluster0.tenpf2n.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())
    # app.database = app.mongodb_client["Cluster0"]
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

@app.get("/")
async def index():
    return {"welcome to carpool project"}






    







    

        
    




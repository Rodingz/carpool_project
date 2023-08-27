from fastapi import FastAPI, Query
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from passlib.context import CryptContext
import os
import certifi
import datetime as dt

router = APIRouter(
    prefix ='/user', 
    tags=['user'],
)

pwd_cxt = CryptContext(schemes=["bcrypt"],deprecated="auto")

class Hash():
   def bcrypt(password:str):    # Input: User가 입력한 기존 비밀번호, Output: Hashing된 비밀번호
      return pwd_cxt.hash(password)
   def verify(hashed, normal):  # Input: User가 입력한 기존 비밀번호와 그 비밀번호를 Hashing한 비밀번호, Output: True / False
      return pwd_cxt.verify(normal, hashed)


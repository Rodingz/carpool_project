from fastapi import APIRouter
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from passlib.context import CryptContext
import os
import certifi
import datetime as dt
from models.user import User
from models.user import User_login
from models.user import email
from models.user import EP



router = APIRouter(
    prefix ='/user', 
    tags=['user'],
)
#Hashing
pwd_cxt = CryptContext(schemes=["bcrypt"],deprecated="auto")

class Hash():
   def bcrypt(password:str):    # Input: User가 입력한 기존 비밀번호, Output: Hashing된 비밀번호
      return pwd_cxt.hash(password)
   def verify(hashed, normal):  # Input: User가 입력한 기존 비밀번호와 그 비밀번호를 Hashing한 비밀번호, Output: True / False
      return pwd_cxt.verify(normal, hashed)
# crete user
@router.post("/create")
async def create_user(new_user: User):
    data = new_user.dict()
    hashed_pw = Hash.bcrypt(new_user.password)
    data["password"] = hashed_pw
    result = router.database.user.insert_one(data)
    return {"message": "User registration successful."}

# login user
@router.post("/login")
async def user_login(login_user: User_login):
    user = router.database.user.find_one({"user_name": login_user.username})

    if not user:
        return {"message: No such username exist."}
    
    verified = Hash.verify(user["password"], login_user.password)   # True: 고객이 입력한 비번과 DB 안의 비번이 일치할때, False: 고객이 입력한 비번과 DB 비번이 일치하지않을때

    # 고객이 입력한 데이터를 가져오는 방법
    # 기존에 DB에 입력되어있는 데이터를 가져오는 방법
    
    if verified == False:
        return {"message": "Password is wrong."}
    else:
        return {"message": "Login successful."}
# edit user
@router.put("/edit/{user_id}")
async def edit_user(user_id: str, edited_user: User):

    data = edited_user.dict(exclude_unset=True)

    if edited_user.password:
        hashed_pw = Hash.bcrypt(edited_user.password)
        data["password"] = hashed_pw

    result = router.database.user.update_one({"_id": ObjectId(user_id)}, {"$set": data})   # 1번째 param: 수정할 document 추적, 2번째 param: 덮어씌울 데이터

    if result.modified_count == 1:
        return {"message": "User updated successfully."}
    else:
        return {"message": "User not found."}
#delete user
@router.delete("/delete/{user_id}")
async def delete_user(user_id: str):

    result = router.database.user.delete_one({"_id": ObjectId(user_id)})   # 삭제할 document 추적

    if result.deleted_count == 1:
        return {"message": "User deleted successfully."}
    else:
        return {"message": "User not found."}

# find ID
@router.post("/find")
async def find_user(request: email):
    user = router.database.user.find_one({"email": request.email})
    
    if user == None:
        return {"message": "There is no user with such email address"}
 
    username = user["user_name"]   
    return{"message":"Your username is " + username}

 # change password
@router.put("/login/edit_password")
async def edit_password(request: EP):
    user = router.database.user.find_one({"email": request.email})

    if user == None:
        return {"message": "There is no user with such email address"}
    
    hashed_pw = Hash.bcrypt(request.password)

    result = router.database.user.update_one({"_id": ObjectId(user["_id"])}, {"$set": {"password": hashed_pw}})   # 1번째 param: 수정할 document 추적, 2번째 param: 덮어씌울 데이터

# warning 
@router.put("/warning/{reporter_user_id}/{reported_user_id}")
async def give_warning(reporter_user_id: str, reported_user_id: str):
    docs = router.database.user.find_one({'_id': ObjectId(reported_user_id)})
    docs["warning"].append(reporter_user_id)
    result = router.database.user.update_one({"_id": ObjectId(reported_user_id)}, {"$set": docs})
    warning_list = docs["warning"] 
    list = []
    for i in warning_list:
        if i not in list:
            list.append(i)
        else:
            continue
    if len(list) >= 3:
        docs["penalty"] +=1
        docs['warning'].clear 
        result = router.database.user.update_one({"_id": ObjectId(reported_user_id)}, {"$set": docs})

# 정지 시키는 api 필요

# party sort
# party type sorting
# @app.get("/party/sort/type/{party_type}")
# async def sort_party_type(party_type: str):
#     docs = app.database.user.find({"party_type": party_type})
#     docs = str(docs["_id"])
#     for party in docs:
#         party["_id"] = str(party["_id"]) 

# # party destination sort
# @app.get("/party/sort/destination/{destination}")
# async def sort_party_destination(destination: str):
#     docs = app.database.user.find({"destination": destination})
#     docs = str(docs["_id"])
#     for party in docs:
#         party["_id"] = str(party["_id"]) 
# # date
# @app.get("/party/sort/date/{date_time}")
# async def sort_party_date_time(date_time: str):
#     docs = app.database.user.find()
#     for party in docs:
#         if party["date_time"].split(" ").index(0) = date_time
#             docs = str(docs["date_time"])

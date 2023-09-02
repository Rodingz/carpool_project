from fastapi import APIRouter
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from passlib.context import CryptContext
import os
import certifi
import datetime as dt
from models.party import Party

router = APIRouter(
    prefix ='/party', 
    tags=['party'],
)
#party create

@router.post("/create/{user_id}")
async def create_party(user_id: str, new_party:Party):
    data = new_party.dict()
    data["party_recruiter_id"] = user_id
    result = router.database.party.insert_one(data)

    return {"message": "Party registration is successful."}

#party edit

@router.put("/edit/{party_id}")
async def edit_party(party_id: str, edited_party: Party):

    data = edited_party.dict(exclude_unset=True)

    result = router.database.party.update_one({"_id": ObjectId(party_id)}, {"$set": data})   # 1번째 param: 수정할 document 추적, 2번째 param: 덮어씌울 데이터

    if result.modified_count == 1:
        return {"message": "Party updated successfully."}
    else:
        return {"message": "Party not found."}

#party delete

@router.delete("/delete/{party_id}")
async def delete_party(party_id: str):

    result = router.database.party.delete_one({"_id": ObjectId(party_id)})   # 삭제할 document 추적

    if result.deleted_count == 1:
        return {"message": "Party deleted successfully."}
    else:
        return {"message": "Party not found."}

#find_party
@router.get("/my_page/find")
# async def get_party_list():
#     docs =  app.database.party.find()
#     all_party_list = []
#     party_list = []
    
#     crt_time = str(dt.datetime.now())
#     print("Current time is" + crt_time)

    
#     for party in docs:
#         party["_id"] = str(party["_id"]) 

#         if party["date_time"] > crt_time:
#             party_list.append(party)
#     for each in party_list:
#         print(each)
async def get_party_list():
    docs = router.database.party.find()

    party_list = []
    all_party_list = []

    # 현재 시간을 string으로 저장한 변수
    crt_time = str(dt.datetime.now())
    print("Current time is " + crt_time)

    for party in docs:
        party["_id"] = str(party["_id"])
        all_party_list.append(party)

        if party["date_time"] > crt_time:
            party_list.append(party)
    
    for each in party_list:
        print(each)
        
#current_party
@router.get("/my_page/find/current/{user_id}")
async def get_current_party(user_id):
    docs = router.database.party.find({'party_recruiter_id': user_id})
    crt_time = str(dt.datetime.now())

    for party in docs:
        party["_id"] = str(party["_id"]) 

        if party["date_time"] > crt_time:
            print(party)

#past_party
@router.get("/my_page/find/past/{user_id}")
async def get_past_party(user_id):
    docs = router.database.party.find({'party_recruiter_id': user_id})
    crt_time = str(dt.datetime.now())

    for party in docs:
        party["_id"] = str(party["_id"]) 

        if party["date_time"] < crt_time:
            print(party)

#one_party
@router.get("/my_page/find/one/{party_id}")
async def get_one_party(party_id: str):
    docs =  router.database.party.find_one({'_id': ObjectId(party_id)})
    docs["_id"] = str(docs["_id"])
    print(docs)

#join_party
@router.put("/join/{party_id}/{user_id}")
async def join_party(party_id: str, user_id: str):
    docs =  router.database.party.find_one({'_id': ObjectId(party_id)})
    docs["party_member_id"].append(user_id)
    docs["cur_recruitment"] += 1
    result = router.database.party.update_one({"_id": ObjectId(party_id)}, {"$set": docs})

# withdraw party 숙제
@router.put("/drop/{party_id}/{user_id}")
async def drop_party(party_id: str, user_id: str):
    docs =  router.database.party.find_one({'_id': ObjectId(party_id)})
    docs["party_member_id"].remove(user_id)
    docs["cur_recruitment"] -= 1
    result = router.database.party.update_one({"_id": ObjectId(party_id)}, {"$set": docs})


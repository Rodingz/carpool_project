from fastapi import FastAPI, Query
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from passlib.context import CryptContext
import os
import certifi
import datetime as dt


pwd_cxt = CryptContext(schemes=["bcrypt"],deprecated="auto")

class Hash():
   def bcrypt(password:str):    # Input: User가 입력한 기존 비밀번호, Output: Hashing된 비밀번호
      return pwd_cxt.hash(password)
   def verify(hashed, normal):  # Input: User가 입력한 기존 비밀번호와 그 비밀번호를 Hashing한 비밀번호, Output: True / False
      return pwd_cxt.verify(normal, hashed)

app = FastAPI()

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

class User(BaseModel):
    user_name: str
    real_name: str
    password: str
    phone_number: str
    email: str
    student_email: str
    car_number: int
    car_color: str
    car_type: str
    car_license: str
    homeroom: str
    user_type: str
    warning: list[str]
    penalty: int

class User_login(BaseModel):
    username: str
    password: str

class Party(BaseModel):
    date_time: str
    destination: str
    departure: str
    max_recruitment: int
    cur_recruitment: int
    party_type: str
    party_recruiter_id: str
    party_member_id: list[str]

class email(BaseModel):
    email:str

class EP(BaseModel):
    email: str
    password: str


@app.get("/")
async def index():
    return {"welcome to carpool project"}


@app.post("/user/create")
async def create_user(new_user: User):
    data = new_user.dict()
    hashed_pw = Hash.bcrypt(new_user.password)
    data["password"] = hashed_pw
    result = app.database.user.insert_one(data)
    return {"message": "User registration successful."}


@app.post("/user/login")
async def user_login(login_user: User_login):
    user = app.database.user.find_one({"user_name": login_user.username})

    if not user:
        return {"message: No such username exist."}
    
    verified = Hash.verify(user["password"], login_user.password)   # True: 고객이 입력한 비번과 DB 안의 비번이 일치할때, False: 고객이 입력한 비번과 DB 비번이 일치하지않을때

    # 고객이 입력한 데이터를 가져오는 방법
    # 기존에 DB에 입력되어있는 데이터를 가져오는 방법
    
    if verified == False:
        return {"message": "Password is wrong."}
    else:
        return {"message": "Login successful."}


@app.put("/user/edit/{user_id}")
async def edit_user(user_id: str, edited_user: User):

    data = edited_user.dict(exclude_unset=True)

    if edited_user.password:
        hashed_pw = Hash.bcrypt(edited_user.password)
        data["password"] = hashed_pw

    result = app.database.user.update_one({"_id": ObjectId(user_id)}, {"$set": data})   # 1번째 param: 수정할 document 추적, 2번째 param: 덮어씌울 데이터

    if result.modified_count == 1:
        return {"message": "User updated successfully."}
    else:
        return {"message": "User not found."}


@app.delete("/user/delete/{user_id}")
async def delete_user(user_id: str):

    result = app.database.user.delete_one({"_id": ObjectId(user_id)})   # 삭제할 document 추적

    if result.deleted_count == 1:
        return {"message": "User deleted successfully."}
    else:
        return {"message": "User not found."}
    
#party create

@app.post("/party/create/{user_id}")
async def create_party(user_id: str, new_party:Party):
    data = new_party.dict()
    data["party_recruiter_id"] = user_id
    result = app.database.party.insert_one(data)

    return {"message": "Party registration is successful."}

#party edit

@app.put("/party/edit/{party_id}")
async def edit_party(party_id: str, edited_party: Party):

    data = edited_party.dict(exclude_unset=True)

    result = app.database.party.update_one({"_id": ObjectId(party_id)}, {"$set": data})   # 1번째 param: 수정할 document 추적, 2번째 param: 덮어씌울 데이터

    if result.modified_count == 1:
        return {"message": "Party updated successfully."}
    else:
        return {"message": "Party not found."}

#party delete

@app.delete("/party/delete/{party_id}")
async def delete_party(party_id: str):

    result = app.database.party.delete_one({"_id": ObjectId(party_id)})   # 삭제할 document 추적

    if result.deleted_count == 1:
        return {"message": "Party deleted successfully."}
    else:
        return {"message": "Party not found."}

# find ID
@app.post("/user/find")
async def find_user(request: email):
    user = app.database.user.find_one({"email": request.email})
    
    if user == None:
        return {"message": "There is no user with such email address"}
 
    username = user["user_name"]   
    return{"message":"Your username is " + username}

 # change password
@app.put("/user/login/edit_password")
async def edit_password(request: EP):
    user = app.database.user.find_one({"email": request.email})

    if user == None:
        return {"message": "There is no user with such email address"}
    
    hashed_pw = Hash.bcrypt(request.password)

    result = app.database.user.update_one({"_id": ObjectId(user["_id"])}, {"$set": {"password": hashed_pw}})   # 1번째 param: 수정할 document 추적, 2번째 param: 덮어씌울 데이터


#find_party
@app.get("/my_page/party/find")
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
    docs = app.database.party.find()

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
@app.get("/my_page/party/find/current/{user_id}")
async def get_current_party(user_id):
    docs = app.database.party.find({'party_recruiter_id': user_id})
    crt_time = str(dt.datetime.now())

    for party in docs:
        party["_id"] = str(party["_id"]) 

        if party["date_time"] > crt_time:
            print(party)

#past_party
@app.get("/my_page/party/find/past/{user_id}")
async def get_past_party(user_id):
    docs = app.database.party.find({'party_recruiter_id': user_id})
    crt_time = str(dt.datetime.now())

    for party in docs:
        party["_id"] = str(party["_id"]) 

        if party["date_time"] < crt_time:
            print(party)

#one_party
@app.get("/my_page/party/find/one/{party_id}")
async def get_one_party(party_id: str):
    docs =  app.database.party.find_one({'_id': ObjectId(party_id)})
    docs["_id"] = str(docs["_id"])
    print(docs)

#join_party
@app.put("/party/join/{party_id}/{user_id}")
async def join_party(party_id: str, user_id: str):
    docs =  app.database.party.find_one({'_id': ObjectId(party_id)})
    docs["party_member_id"].append(user_id)
    docs["cur_recruitment"] += 1
    result = app.database.party.update_one({"_id": ObjectId(party_id)}, {"$set": docs})

# withdraw party 숙제
@app.put("/party/drop/{party_id}/{user_id}")
async def drop_party(party_id: str, user_id: str):
    docs =  app.database.party.find_one({'_id': ObjectId(party_id)})
    docs["party_member_id"].remove(user_id)
    docs["cur_recruitment"] -= 1
    result = app.database.party.update_one({"_id": ObjectId(party_id)}, {"$set": docs})

# warning 
@app.put("/warning/{reporter_user_id}/{reported_user_id}")
async def give_warning(reporter_user_id: str, reported_user_id: str):
    docs = app.database.user.find_one({'_id': ObjectId(reported_user_id)})
    docs["warning"].append(reporter_user_id)
    result = app.database.user.update_one({"_id": ObjectId(reported_user_id)}, {"$set": docs})

# penalty --> warning 추가될때마다 실행
@app.put("/penalty/{reported_user_id}")
async def give_penalty(reported_user_id: str):
    docs = app.database.user.find_one({'_id': ObjectId(reported_user_id)})
    warning_list = docs["warning"] 
    list = []
    for i in warning_list:
        if i not in list:
            list.append(i)
        else:
            continue
    if len(list) >= 3:
        docs["penalty"] +=1
        result = app.database.user.update_one({"_id": ObjectId(reported_user_id)}, {"$set": docs})
    
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

@app.get("/party/sort/")
async def sort_party(party_type: str = Query(None), destination: str = Query(None), date: str = Query(None), time: str = Query(None)):
    party_list = []
    if party_type is not None and destination is not None:
        party = app.database.party.find({ "$and": [{"destination": destination},{"party_type":party_type}]})
        for each in party:
            party_list.append(each)
   
    if party_type is not None and destination is None:
        party = app.database.party.find({"party_type":party_type})
        for each in party:
            party_list.append(each)

    
    if party_type is None and destination is None:
        party = app.database.party.find()
        for each in party:
            party_list.append(each)

    
    if party_type is None and destination is not None:
        party = app.database.party.find({"destination":destination})
        for each in party:
            party_list.append(each)
    
    final_party = []
    for i in party_list:
        if date is not None and time is None:    
            if i["date_time"].split(" ")[0] >= date:
                final_party.append(i)
        
        if date is None and time is not None:
            if i["date_time"].split(" ")[1][0:7] >= time:
                if i["date_time"].split(" ")[0] >= dt.today():    
                    final_party.append(i)

        if date is not None and time is not None:
            if i["date_time"].split(" ")[0] >= date:
                if i["date_time"].split(" ")[1][0:7] >= time:
                    final_party.append(i)
    

    print(final_party)
        
    




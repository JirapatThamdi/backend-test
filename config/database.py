
import os
import motor.motor_asyncio
from bson import ObjectId

# export MONGODB_URL='mongodb+srv://plam2544:RULiHPvYiDIFL3KE@cluster0.0x0qdjp.mongodb.net/'

# Create a MongoClient object
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])

class MongoDbInterface:

    def __init__(self, collection_name: str, c_database=None):
        if c_database is None:
            c_database = client["backend"]
        self.collection = c_database[collection_name]

    async def create_document(self, data: dict) -> dict:
        try:
            new_document = await self.collection.insert_one(data)
        except:
            return None

        created_document = await self.collection.find_one({"_id":new_document.inserted_id})
        created_document["_id"] = str(created_document["_id"])

        return created_document

    async def get_document_by_id(self, document_id: str) -> dict:
        document = await self.collection.find_one({"_id": ObjectId(document_id)})

        return document

    async def get_document(self, data: dict) -> dict:
        document = await self.collection.find_one(data)

        return document
    
    async def get_documents(self,data:dict,sort_value:int, length = 100) -> dict:
        try:
            documents = await self.collection.find(data).sort("createAt", sort_value).to_list(length=length)
            return documents
        except:
            return None
        
    async def get_document_by_id(self,id:str) -> dict:
        try:
            documents = await self.collection.find_one({"_id": ObjectId(id)})
            return documents
        except:
            return None
        

    async def update_document_by_id(self, document_id: str, update_data: dict) -> dict:
        try:
            update_document = await self.collection.find_one_and_update({"_id":ObjectId(document_id)}, {"$set":update_data})
            return update_document
        except:
            return None
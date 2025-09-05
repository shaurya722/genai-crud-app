from bson import ObjectId
from fastapi import HTTPException
from typing import Dict, Any, Optional
from .serializers import serialize_mongodb_doc as serialize
from .config import db

def insert(collection: str, data: Dict[str, Any]):
    result = db[collection].insert_one(data)
    return {"inserted_id": str(result.inserted_id)}

def get_one(collection: str, item_id: str):
    doc = db[collection].find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(404, "Item not found")
    return serialize(doc)

def get_all(collection: str, filter: Optional[Dict] = None, projection: Optional[Dict] = None,
            sort: Optional[list] = None, limit: Optional[int] = None):
    cursor = db[collection].find(filter or {}, projection)
    if sort:
        cursor = cursor.sort(sort)
    if limit:
        cursor = cursor.limit(limit)
    return serialize(list(cursor))


def update(collection: str, item_id: str, data: Dict[str, Any]):
    result = db[collection].replace_one({"_id": ObjectId(item_id)}, data)
    return {"matched_count": result.matched_count, "modified_count": result.modified_count}

def patch(collection: str, item_id: str, data: Dict[str, Any]):
    result = db[collection].update_one({"_id": ObjectId(item_id)}, {"$set": data})
    return {"matched_count": result.matched_count, "modified_count": result.modified_count}

def delete(collection: str, item_id: str):
    result = db[collection].delete_one({"_id": ObjectId(item_id)})
    return {"deleted_count": result.deleted_count}

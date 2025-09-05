from bson import ObjectId
from typing import Any, List, Dict
from fastapi.encoders import jsonable_encoder

class MongoJSONEncoder:
    """Custom encoder for MongoDB documents"""
    @staticmethod
    def encode(obj: Any) -> Any:
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, list):
            return [MongoJSONEncoder.encode(item) for item in obj]
        if isinstance(obj, dict):
            return {key: MongoJSONEncoder.encode(value) for key, value in obj.items()}
        return obj

def serialize_mongodb_doc(doc: Any) -> Any:
    """Convert MongoDB document to JSON-serializable format"""
    # First use our custom encoder
    encoded = MongoJSONEncoder.encode(doc)
    # Then use FastAPI's encoder for any remaining conversions
    return jsonable_encoder(encoded)
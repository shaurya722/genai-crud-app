from bson import ObjectId

# Test data constants
MOCK_OBJECT_ID = "507f1f77bcf86cd799439011"
MOCK_USER = {
    "_id": ObjectId(MOCK_OBJECT_ID),
    "name": "John Doe",
    "email": "john@example.com"
}

# Mock LLM responses
MOCK_LLM_RESPONSES = {
    "get_one": {
        "action": "get_one",
        "schema": "users",
        "item_id": MOCK_OBJECT_ID
    },
    "create": {
        "action": "create",
        "schema": "users",
        "item": {
            "name": "John Doe",
            "email": "john@example.com"
        }
    },
    "update": {
        "action": "update",
        "schema": "users",
        "item_id": MOCK_OBJECT_ID,
        "item": {
            "name": "Jane Doe"
        }
    },
    "delete": {
        "action": "delete",
        "schema": "users",
        "item_id": MOCK_OBJECT_ID
    }
}
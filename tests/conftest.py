import pytest
from unittest.mock import Mock, patch
import os
from dotenv import load_dotenv
from bson import ObjectId

def pytest_configure():
    """Set environment variables before any tests run"""
    os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
    os.environ["MONGODB_DB"] = "test_db"
    os.environ["GOOGLE_API_KEY"] = "test_key"

@pytest.fixture(autouse=True)
def mock_mongodb():
    """Mock MongoDB client and connection"""
    with patch('genai_crud_agent.app.genai_router.MongoClient') as mock_client:
        # Create mock database
        mock_db = Mock()
        
        # Setup mock collections with proper return values
        users_collection = Mock()
        users_collection.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "John Doe",
            "email": "john@example.com"
        }
        users_collection.find.return_value = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "name": "John Doe",
                "email": "john@example.com"
            }
        ]
        users_collection.insert_one.return_value = Mock(
            inserted_id=ObjectId("507f1f77bcf86cd799439011")
        )
        users_collection.replace_one.return_value = Mock(
            matched_count=1,
            modified_count=1
        )
        users_collection.delete_one.return_value = Mock(
            deleted_count=1
        )
        
        mock_db.users = users_collection
        mock_db.contacts = Mock()
        mock_db.categories = Mock()
        
        # Setup client to return our mock db
        mock_client.return_value.__getitem__.return_value = mock_db
        
        yield mock_db

@pytest.fixture(autouse=True)
def mock_llm():
    """Mock Gemini LLM responses"""
    with patch('genai_crud_agent.app.genai_router.ChatGoogleGenerativeAI') as mock_llm:
        mock_response = Mock()
        mock_response.content = '''
        {
            "action": "get_one",
            "schema": "users",
            "item_id": "507f1f77bcf86cd799439011"
        }
        '''
        mock_llm.return_value.invoke.return_value = mock_response
        yield mock_llm

@pytest.fixture
def mock_db_error():
    """Mock MongoDB error scenarios"""
    with patch('genai_crud_agent.app.genai_router.MongoClient') as mock_client:
        mock_db = Mock()
        mock_db.users.find_one.side_effect = Exception("Database error")
        mock_client.return_value.__getitem__.return_value = mock_db
        yield mock_db
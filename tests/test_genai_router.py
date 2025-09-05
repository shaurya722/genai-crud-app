import os
import pytest
from bson import ObjectId
from pydantic import ValidationError
from genai_crud_agent.app.genai_router import (
    process_query,
    extract_json_from_text,
    parse_field_values,
    extract_query_filters,
    decide_crud_action,
    CrudState,
    SCHEMA_MAP,
    db
)

# Use a separate test database
TEST_DB = "test_db_real"

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Setup test database before running tests and clean up after."""
    db.client.drop_database(TEST_DB)
    yield
    db.client.drop_database(TEST_DB)

# -----------------------------
# JSON extraction tests
# -----------------------------
def test_extract_json_from_text():
    text = 'some text {"key": "value"} more text'
    result = extract_json_from_text(text)
    assert result == {"key": "value"}

    with pytest.raises(ValueError):
        extract_json_from_text("no json here")

# -----------------------------
# Field parsing tests
# -----------------------------
def test_parse_field_values():
    inputs = [
        "create user with name John and email john@example.com",
        "set status to active",
        "name: Alice, email = alice@example.com"
    ]
    expected_outputs = [
        {"name": "John", "email": "john@example.com"},
        {"status": "active"},
        {"name": "Alice", "email": "alice@example.com"}
    ]
    for input_text, expected in zip(inputs, expected_outputs):
        result = parse_field_values(input_text)
        assert result == expected

# -----------------------------
# CRUD tests with real DB
# -----------------------------
@pytest.mark.asyncio
def test_process_query_create_valid():
    """Create with all required fields"""
    result = process_query("create user with name John and email john@example.com")
    assert result["success"] is True
    assert "inserted_id" in result

@pytest.mark.asyncio
def test_process_query_create_invalid():
    """Create missing required field should fail"""
    result = process_query("create user with name OnlyName")
    assert result["success"] is False
    assert "error" in result
    assert "ValidationError" in result["error"]  # depending on your error formatting

@pytest.mark.asyncio
def test_process_query_get_one():
    inserted = db.users.insert_one({"name": "Jane", "email": "jane@example.com"})
    item_id = str(inserted.inserted_id)

    result = process_query(f"get user with id {item_id}")
    assert result["success"] is True
    assert result["data"]["_id"] == item_id
    assert result["data"]["name"] == "Jane"

@pytest.mark.asyncio
def test_process_query_update_valid():
    inserted = db.users.insert_one({"name": "Jake", "email": "jake@example.com"})
    item_id = str(inserted.inserted_id)

    result = process_query(f"update user {item_id} set name to Jacob email to jacob@example.com")
    assert result["success"] is True
    assert result["matched_count"] == 1

    updated_user = db.users.find_one({"_id": ObjectId(item_id)})
    assert updated_user["name"] == "Jacob"
    assert updated_user["email"] == "jacob@example.com"

@pytest.mark.asyncio
def test_process_query_update_invalid():
    """Update missing required field should fail"""
    inserted = db.users.insert_one({"name": "Mike", "email": "mike@example.com"})
    item_id = str(inserted.inserted_id)

    result = process_query(f"update user {item_id} set name to OnlyName")
    assert result["success"] is False
    assert "error" in result

@pytest.mark.asyncio
def test_process_query_delete():
    inserted = db.users.insert_one({"name": "DeleteMe", "email": "deleteme@example.com"})
    item_id = str(inserted.inserted_id)

    result = process_query(f"delete user with id {item_id}")
    assert result["success"] is True
    assert result["deleted_count"] == 1

    deleted_user = db.users.find_one({"_id": ObjectId(item_id)})
    assert deleted_user is None

# -----------------------------
# Schema validation tests
# -----------------------------
def test_schema_validation_required_fields():
    for schema_name, schema_class in SCHEMA_MAP.items():
        # Valid data with all required fields
        valid_data = {f.name: "Test" for f in schema_class.__fields__.values() if f.required}
        instance = schema_class(**valid_data)
        for field_name in valid_data:
            assert getattr(instance, field_name) == valid_data[field_name]

        # Invalid data: missing required field
        with pytest.raises(ValidationError):
            schema_class()  # missing all required fields

# -----------------------------
# Edge cases
# -----------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize("query,expected_action", [
    ("", "get_all"),
    ("invalid query", "get_all"),
    ("list all", "get_all"),
    ("show everything", "get_all"),
])
def test_edge_cases(query, expected_action):
    result = process_query(query)
    assert "success" in result
    if result["success"]:
        assert result["action"] == expected_action
    else:
        assert "error" in result

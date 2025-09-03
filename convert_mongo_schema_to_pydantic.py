from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional, Any
import keyword
import re

# === CONFIG ===
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "development"
OUTPUT_FILE = "schemas.py"
SAMPLE_SIZE = 50   # how many documents to sample per collection

# === CONNECT TO MONGO ===
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print(MONGO_URI)

def to_valid_identifier(name: str) -> str:
    """Convert Mongo field name to valid Python identifier."""
    name = re.sub(r"\W|^(?=\d)", "_", name)
    if keyword.iskeyword(name):
        name = name + "_field"
    return name

def guess_type(value):
    """Map Python types to Pydantic annotations."""
    if isinstance(value, str):
        return "str"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, list):
        return "list[Any]"
    if isinstance(value, dict):
        return "dict[str, Any]"
    return "Any"

def infer_schema(collection_name: str):
    """Infer schema by sampling documents from a collection."""
    collection = db[collection_name]
    samples = collection.find().limit(SAMPLE_SIZE)
    field_types = {}

    for doc in samples:
        for field, value in doc.items():
            py_field = to_valid_identifier(field)
            t = guess_type(value)
            if py_field not in field_types:
                field_types[py_field] = t
            else:
                # if different types across docs → fallback to Any
                if field_types[py_field] != t:
                    field_types[py_field] = "Any"

    return field_types

def generate_models():
    """Generate Pydantic models for all collections."""
    code = [
        "from pydantic import BaseModel",
        "from typing import Optional, Any, List, Dict\n"
    ]

    for name in db.list_collection_names():
        fields = infer_schema(name)
        class_name = "".join(word.capitalize() for word in name.split("_"))

        code.append(f"class {class_name}Schema(BaseModel):")
        if not fields:
            code.append("    pass\n")
            continue

        for field, typ in fields.items():
            optional = "Optional[" + typ + "]"
            code.append(f"    {field}: {optional} = None")

        code.append("")  # blank line between classes

    return "\n".join(code)

if __name__ == "__main__":
    code = generate_models()
    with open(OUTPUT_FILE, "w") as f:
        f.write(code)
    print(f"✅ Schema file generated: {OUTPUT_FILE}")

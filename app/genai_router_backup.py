# # genai_router.py

# import os
# import json
# from dotenv import load_dotenv
# from typing import TypedDict, Optional, Any
# from pymongo import MongoClient
# from bson import ObjectId

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.schema import HumanMessage
# from langgraph.graph import StateGraph, START, END

# from .schemas.all_schemas import *  # Import all your Pydantic schemas
# from .serializers import serialize_mongodb_doc

# # Load environment variables
# load_dotenv()
# MONGODB_URI = os.getenv("MONGODB_URI")
# MONGODB_DB = os.getenv("MONGODB_DB")
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# # MongoDB client
# client = MongoClient(MONGODB_URI)
# db = client[MONGODB_DB]

# # Gemini LLM
# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",
#     google_api_key=GOOGLE_API_KEY,
#     temperature=0.1
# )

# # Map schema names to Pydantic classes and MongoDB collections
# SCHEMA_MAP = {
#     cls.__name__.replace("Schema", "").lower(): cls
#     for cls in [
#         CategoriesSchema, ContactsSchema, SettingsSchema, CompaniesSchema, TasksSchema,
#         PermissionsSchema, Chat_listsSchema, LogsSchema, EmailLogsSchema, HelpCenterSchema,
#         FriendsSchema, StaticPagesSchema, NotificationsSchema, ManualLogsSchema, RolesSchema,
#         UsersSchema, ChatsSchema, JobsSchema, EmailTemplatesSchema, AdminsSchema
#     ]
# }

# # State definition
# class CrudState(TypedDict):
#     user_input: str
#     action: str
#     schema: str
#     item_id: Optional[str]
#     item: Optional[dict]
#     result: Optional[Any]
#     query: Optional[dict]

# # Decide CRUD action using Gemini
# # def decide_crud_action(state: CrudState):
# #     prompt = f"""
# #     Analyze the user query and determine:
# #     - action: one of ["insert", "get_one", "get_all", "update", "patch", "delete"]
# #     - schema: which schema/collection to use (e.g., users, companies, contacts)
# #     - item_id: string id if needed (null if not needed)
# #     - item: object with fields if needed (null if not needed)
# #     - query: dictionary for filtering documents (null if not needed)
# #     Respond with a valid JSON object.
# #     """
# #     prompt += f"\nUser Query: {state['user_input']}\n"

# #     try:
# #         response = llm.invoke([HumanMessage(content=prompt)])
# #         response_text = response.content.strip()
# #         start_idx = response_text.find('{')
# #         end_idx = response_text.rfind('}') + 1
# #         arguments = json.loads(response_text[start_idx:end_idx])
# #         # Validate required keys
# #         if "action" not in arguments or "schema" not in arguments:
# #             raise ValueError("Missing keys in Gemini response")
# #         # Ensure query exists for get_all
# #         if arguments["action"] == "get_all" and "query" not in arguments:
# #             arguments["query"] = {}
# #         state.update(arguments)
# #         return state
# #     except Exception as e:
# #         # Fallback naive extraction
# #         state["action"] = "get_all" if "list" in state["user_input"].lower() else "get_one"
# #         state["schema"] = "contacts" if "contact" in state["user_input"].lower() else "users"
# #         state["item_id"] = None
# #         # Extract filter for "having email ..."
# #         import re
# #         email_match = re.search(r'email\s+([\w\.\-]+@[\w\.\-]+)', state["user_input"], re.I)
# #         state["query"] = {"email": email_match.group(1)} if email_match else {}
# #         state["item"] = None
# #         return state


# def decide_crud_action(state: CrudState):
#     prompt = f"""
#     Analyze the user query and determine:
#     - action: one of ["insert", "get_one", "get_all", "update", "patch", "delete"]
#     - schema: which schema/collection to use (e.g., users, companies, contacts, etc.)
#     - item_id: string id if needed (null if not needed)
#     - item: object with fields if needed (null if not needed)
#     - query: dictionary for filtering documents (null if not needed)
#     Respond with a valid JSON object.
#     """
#     prompt += f"\nUser Query: {state['user_input']}\n"

#     try:
#         response = llm.invoke([HumanMessage(content=prompt)])
#         response_text = response.content.strip()
#         start_idx = response_text.find('{')
#         end_idx = response_text.rfind('}') + 1
#         arguments = json.loads(response_text[start_idx:end_idx])
#         if "action" not in arguments or "schema" not in arguments:
#             raise ValueError("Missing keys in Gemini response")
#         if arguments["action"] == "get_all" and "query" not in arguments:
#             arguments["query"] = {}
#         state.update(arguments)
#         return state

#     except Exception:
#         # ❌ Fallback: naive extraction for **all collections**
#         user_input = state["user_input"].lower()

#         # Detect action
#         if any(w in user_input for w in ["add", "create", "insert", "new"]):
#             state["action"] = "insert"
#         elif any(w in user_input for w in ["update", "put"]):
#             state["action"] = "update"
#         elif "patch" in user_input:
#             state["action"] = "patch"
#         elif any(w in user_input for w in ["delete", "remove"]):
#             state["action"] = "delete"
#         elif any(w in user_input for w in ["list", "get all", "show all", "fetch all"]):
#             state["action"] = "get_all"
#         else:
#             state["action"] = "get_one"

#         # Detect schema dynamically from SCHEMA_MAP
#         state["schema"] = None
#         for schema_name in SCHEMA_MAP.keys():
#             if schema_name in user_input:
#                 state["schema"] = schema_name
#                 break
#         if not state["schema"]:
#             state["schema"] = "users"  # default fallback

#         # Extract item_id if mentioned
#         import re
#         id_match = re.search(r'id\s*[:=]?\s*([a-f0-9]{24}|\d+)', user_input)
#         state["item_id"] = id_match.group(1) if id_match else None

#         # Extract item fields for insert/update/patch
#         item = {}
#         field_value_matches = re.findall(
#             r'(?:set|create|add)\s+([\w_]+)\s+(?:to\s+)?([\w@.\-]+)', user_input, re.I
#         )
#         for field, value in field_value_matches:
#             item[field] = value
#         state["item"] = item if item else None

#         # Extract query filters for get_all/get_one
#         query = {}
#         email_match = re.search(r'email\s+([\w\.\-]+@[\w\.\-]+)', user_input, re.I)
#         if email_match:
#             query["email"] = email_match.group(1)
#         # Add more generic filters here if needed
#         state["query"] = query

#         return state

# # Route decision
# def route_decision(state: CrudState):
#     return state["action"]

# # CRUD functions
# def insert_item(state: CrudState):
#     schema = state["schema"]
#     item = state.get("item", {})
#     cls = SCHEMA_MAP[schema]
#     validated = cls(**item).dict(exclude_unset=True)
#     result = db[schema].insert_one(validated)
#     state["result"] = {"inserted_id": str(result.inserted_id)}
#     return state

# def get_one_item(state: CrudState):
#     schema = state["schema"]
#     item_id = state.get("item_id")
#     if not item_id:
#         state["result"] = None
#         return state
#     doc = db[schema].find_one({"_id": ObjectId(item_id)})
#     state["result"] = serialize_mongodb_doc(doc)
#     return state

# def get_all_items(state: CrudState):
#     schema = state["schema"]
#     query = state.get("query") or {}
#     docs = list(db[schema].find(query))
#     for doc in docs:
#         doc["_id"] = str(doc["_id"])
#     state["result"] = docs
#     return state


# def update_item(state: CrudState):
#     schema = state["schema"]
#     item_id = state.get("item_id")
#     item = state.get("item", {})
#     if not item_id or not item:
#         state["result"] = None
#         return state
#     cls = SCHEMA_MAP[schema]
#     validated = cls(**item).dict(exclude_unset=True)
#     result = db[schema].replace_one({"_id": ObjectId(item_id)}, validated)
#     state["result"] = {"matched_count": result.matched_count, "modified_count": result.modified_count}
#     return state

# def patch_item(state: CrudState):
#     schema = state["schema"]
#     item_id = state.get("item_id")
#     item = state.get("item", {})
#     if not item_id or not item:
#         state["result"] = None
#         return state
#     result = db[schema].update_one({"_id": ObjectId(item_id)}, {"$set": item})
#     state["result"] = {"matched_count": result.matched_count, "modified_count": result.modified_count}
#     return state

# def delete_item(state: CrudState):
#     schema = state["schema"]
#     item_id = state.get("item_id")
#     if not item_id:
#         state["result"] = None
#         return state
#     result = db[schema].delete_one({"_id": ObjectId(item_id)})
#     state["result"] = {"deleted_count": result.deleted_count}
#     return state

# # Build the LangGraph router
# def genai_router():
#     graph = StateGraph(CrudState)
#     graph.add_node("decide_crud", decide_crud_action)
#     graph.add_node("insert", insert_item)
#     graph.add_node("get_one", get_one_item)
#     graph.add_node("get_all", get_all_items)
#     graph.add_node("update", update_item)
#     graph.add_node("patch", patch_item)
#     graph.add_node("delete", delete_item)

#     # Connect start -> decision
#     graph.add_edge(START, "decide_crud")

#     # Conditional edges
#     graph.add_conditional_edges(
#         "decide_crud",
#         route_decision,
#         {
#             "insert": "insert",
#             "get_one": "get_one",
#             "get_all": "get_all",
#             "update": "update",
#             "patch": "patch",
#             "delete": "delete",
#         },
#     )

#     # All CRUD nodes -> END
#     for node in ["insert", "get_one", "get_all", "update", "patch", "delete"]:
#         graph.add_edge(node, END)

#     # Compile and return
#     return graph.compile()


import os
import json
import re
from dotenv import load_dotenv
from typing import TypedDict, Optional, Any, Dict, List
from pymongo import MongoClient
from bson import ObjectId

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph, START, END

from .schemas.all_schemas import *  # Import all your Pydantic schemas
from .serializers import serialize_mongodb_doc

# Load environment variables
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# MongoDB client
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]

# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.1
)

# Map schema names to Pydantic classes and MongoDB collections
SCHEMA_MAP = {
    cls.__name__.replace("Schema", "").lower(): cls
    for cls in [
        CategoriesSchema, ContactsSchema, SettingsSchema, CompaniesSchema, TasksSchema,
        PermissionsSchema, Chat_listsSchema, LogsSchema, EmailLogsSchema, HelpCenterSchema,
        FriendsSchema, StaticPagesSchema, NotificationsSchema, ManualLogsSchema, RolesSchema,
        UsersSchema, ChatsSchema, JobsSchema, EmailTemplatesSchema, AdminsSchema
    ]
}

# State definition
class CrudState(TypedDict):
    user_input: str
    action: str
    schema: str
    item_id: Optional[str]
    item: Optional[dict]
    result: Optional[Any]
    query: Optional[dict]
    error: Optional[str]

def extract_json_from_text(text: str) -> dict:
    """Extract JSON object from LLM response text"""
    try:
        # Find JSON boundaries
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in response")
        
        json_str = text[start_idx:end_idx]
        return json.loads(json_str)
    except Exception:
        raise ValueError("Failed to parse JSON from response")

def parse_field_values(user_input: str) -> Dict[str, Any]:
    """Enhanced field value extraction from natural language"""
    item = {}
    
    # Pattern for key-value pairs with various formats
    patterns = [
        r'(?:set|create|add|with)\s+([\w_]+)\s+(?:to\s+|as\s+|=\s*|:\s*)(["\']?[^,\n]+["\']?)',
        r'([\w_]+)\s*[:=]\s*(["\']?[^,\n]+["\']?)',
        r'(name|email|phone|title|description|status)\s+(?:is\s+)?(["\']?[^,\n]+["\']?)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, user_input, re.IGNORECASE)
        for field, value in matches:
            # Clean up the value
            value = value.strip().strip('"\'')
            # Try to convert to appropriate type
            if value.lower() in ['true', 'false']:
                item[field] = value.lower() == 'true'
            elif value.isdigit():
                item[field] = int(value)
            elif re.match(r'^\d+\.\d+$', value):
                item[field] = float(value)
            else:
                item[field] = value
    
    return item

def extract_query_filters(user_input: str) -> Dict[str, Any]:
    """Extract query filters from natural language"""
    query = {}
    
    # Email filter
    email_match = re.search(r'(?:email|mail)\s+(?:is\s+|=\s*)?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', user_input, re.I)
    if email_match:
        query["email"] = email_match.group(1)
    
    # Name filter
    name_match = re.search(r'(?:name|called)\s+(?:is\s+|=\s*)?["\']?([^"\']+)["\']?', user_input, re.I)
    if name_match:
        query["name"] = {"$regex": name_match.group(1), "$options": "i"}
    
    # Status filter
    status_match = re.search(r'status\s+(?:is\s+|=\s*)?([a-zA-Z]+)', user_input, re.I)
    if status_match:
        query["status"] = status_match.group(1)
    
    # ID filter
    id_match = re.search(r'(?:id|_id)\s+(?:is\s+|=\s*)?([a-f0-9]{24})', user_input, re.I)
    if id_match:
        query["_id"] = ObjectId(id_match.group(1))
    
    return query

def decide_crud_action(state: CrudState):
    """Enhanced CRUD action decision with better fallback handling"""
    
    # Enhanced prompt for Gemini
    prompt = f"""
    Analyze the user query and determine the CRUD operation details.
    
    Available actions: ["insert", "get_one", "get_all", "update", "patch", "delete"]
    Available schemas: {list(SCHEMA_MAP.keys())}
    
    Rules:
    - "insert"/"create": Creating new records
    - "get_one": Retrieving single record (usually with ID)
    - "get_all": Retrieving multiple records (with optional filters)
    - "update": Full record replacement (usually with ID + complete data)
    - "patch": Partial record update (usually with ID + specific fields)
    - "delete": Removing records (usually with ID)
    
    Return a JSON object with:
    {{
        "action": "one of the actions above",
        "schema": "collection name from available schemas",
        "item_id": "ObjectId string if targeting specific record, null otherwise",
        "item": "object with fields for insert/update/patch operations, null otherwise",
        "query": "MongoDB query object for filtering (for get_all/get_one without ID), null otherwise"
    }}
    
    User Query: {state['user_input']}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        response_text = response.content.strip()
        arguments = extract_json_from_text(response_text)
        
        # Validate required keys
        if "action" not in arguments or "schema" not in arguments:
            raise ValueError("Missing required keys in Gemini response")
        
        # Ensure valid schema
        if arguments["schema"] not in SCHEMA_MAP:
            # Try to find closest match
            schema_found = False
            for schema_name in SCHEMA_MAP.keys():
                if schema_name in arguments["schema"].lower():
                    arguments["schema"] = schema_name
                    schema_found = True
                    break
            if not schema_found:
                arguments["schema"] = "users"  # Default fallback
        
        # Set defaults for missing optional fields
        if arguments["action"] == "get_all" and "query" not in arguments:
            arguments["query"] = {}
        
        state.update(arguments)
        state["error"] = None
        return state
        
    except Exception as e:
        # Enhanced fallback parsing
        user_input = state["user_input"].lower()
        state["error"] = f"Gemini parsing failed: {str(e)}, using fallback"
        
        # Detect action with better keyword matching
        if any(keyword in user_input for keyword in ["create", "add", "insert", "new", "register"]):
            state["action"] = "insert"
        elif any(keyword in user_input for keyword in ["update all", "replace", "overwrite"]):
            state["action"] = "update"
        elif any(keyword in user_input for keyword in ["update", "modify", "change", "edit", "patch", "set"]):
            state["action"] = "patch"
        elif any(keyword in user_input for keyword in ["delete", "remove", "destroy", "drop"]):
            state["action"] = "delete"
        elif any(keyword in user_input for keyword in ["list", "get all", "show all", "fetch all", "find all"]):
            state["action"] = "get_all"
        elif any(keyword in user_input for keyword in ["get", "find", "show", "fetch"]):
            if "all" in user_input:
                state["action"] = "get_all"
            else:
                state["action"] = "get_one"
        else:
            state["action"] = "get_all"  # Default fallback
        
        # Detect schema with improved matching
        state["schema"] = None
        for schema_name in SCHEMA_MAP.keys():
            # Check for exact match or plural forms
            if (schema_name in user_input or 
                f"{schema_name}s" in user_input or 
                schema_name.rstrip('s') in user_input):
                state["schema"] = schema_name
                break
        
        if not state["schema"]:
            state["schema"] = "users"  # Default fallback
        
        # Extract item_id
        id_patterns = [
            r'(?:id|_id)\s+([a-f0-9]{24})',
            r'with\s+id\s+([a-f0-9]{24})',
            r'([a-f0-9]{24})',  # Standalone ObjectId
        ]
        
        state["item_id"] = None
        for pattern in id_patterns:
            id_match = re.search(pattern, user_input)
            if id_match:
                state["item_id"] = id_match.group(1)
                break
        
        # Extract item data for create/update/patch operations
        if state["action"] in ["insert", "update", "patch"]:
            state["item"] = parse_field_values(state["user_input"])
        else:
            state["item"] = None
        
        # Extract query filters for get operations
        if state["action"] in ["get_all", "get_one"] and not state["item_id"]:
            state["query"] = extract_query_filters(state["user_input"])
        else:
            state["query"] = {}
        
        return state

# Route decision
def route_decision(state: CrudState):
    return state["action"]

# Enhanced CRUD functions with better error handling
def insert_item(state: CrudState):
    """Create new item with validation"""
    try:
        schema = state["schema"]
        item = state.get("item", {})
        
        if not item:
            state["result"] = {"error": "No item data provided for insertion"}
            return state
        
        # Validate against Pydantic schema
        cls = SCHEMA_MAP[schema]
        validated = cls(**item).dict(exclude_unset=True)
        
        # Insert into MongoDB
        result = db[schema].insert_one(validated)
        state["result"] = {
            "success": True,
            "inserted_id": str(result.inserted_id),
            "action": "insert",
            "schema": schema
        }
        
    except Exception as e:
        state["result"] = {
            "success": False,
            "error": f"Insert failed: {str(e)}",
            "action": "insert",
            "schema": state["schema"]
        }
    
    return state

def get_one_item(state: CrudState):
    """Get single item by ID or query"""
    try:
        schema = state["schema"]
        item_id = state.get("item_id")
        query = state.get("query", {})
        
        if item_id:
            doc = db[schema].find_one({"_id": ObjectId(item_id)})
        elif query:
            doc = db[schema].find_one(query)
        else:
            state["result"] = {"error": "No ID or query provided for get_one operation"}
            return state
        
        if doc:
            state["result"] = {
                "success": True,
                "data": serialize_mongodb_doc(doc),
                "action": "get_one",
                "schema": schema
            }
        else:
            state["result"] = {
                "success": False,
                "error": "Document not found",
                "action": "get_one",
                "schema": schema
            }
            
    except Exception as e:
        state["result"] = {
            "success": False,
            "error": f"Get one failed: {str(e)}",
            "action": "get_one",
            "schema": state["schema"]
        }
    
    return state

def get_all_items(state: CrudState):
    """Get multiple items with optional filtering"""
    try:
        schema = state["schema"]
        query = state.get("query", {})
        
        # Add pagination support
        limit = 100  # Default limit
        docs = list(db[schema].find(query).limit(limit))
        
        # Serialize documents
        serialized_docs = [serialize_mongodb_doc(doc) for doc in docs]
        
        state["result"] = {
            "success": True,
            "data": serialized_docs,
            "count": len(serialized_docs),
            "action": "get_all",
            "schema": schema,
            "query": query
        }
        
    except Exception as e:
        state["result"] = {
            "success": False,
            "error": f"Get all failed: {str(e)}",
            "action": "get_all",
            "schema": state["schema"]
        }
    
    return state

def update_item(state: CrudState):
    """Full document replacement"""
    try:
        schema = state["schema"]
        item_id = state.get("item_id")
        item = state.get("item", {})
        
        if not item_id:
            state["result"] = {"error": "No item ID provided for update operation"}
            return state
        
        if not item:
            state["result"] = {"error": "No item data provided for update operation"}
            return state
        
        # Validate against Pydantic schema
        cls = SCHEMA_MAP[schema]
        validated = cls(**item).dict(exclude_unset=True)
        
        # Update in MongoDB
        result = db[schema].replace_one({"_id": ObjectId(item_id)}, validated)
        
        state["result"] = {
            "success": True,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "action": "update",
            "schema": schema
        }
        
    except Exception as e:
        state["result"] = {
            "success": False,
            "error": f"Update failed: {str(e)}",
            "action": "update",
            "schema": state["schema"]
        }
    
    return state

def patch_item(state: CrudState):
    """Partial document update"""
    try:
        schema = state["schema"]
        item_id = state.get("item_id")
        item = state.get("item", {})
        
        if not item_id:
            state["result"] = {"error": "No item ID provided for patch operation"}
            return state
        
        if not item:
            state["result"] = {"error": "No item data provided for patch operation"}
            return state
        
        # Validate individual fields (partial validation)
        # Note: You might want to implement partial validation logic here
        
        # Update in MongoDB
        result = db[schema].update_one({"_id": ObjectId(item_id)}, {"$set": item})
        
        state["result"] = {
            "success": True,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "action": "patch",
            "schema": schema,
            "updated_fields": list(item.keys())
        }
        
    except Exception as e:
        state["result"] = {
            "success": False,
            "error": f"Patch failed: {str(e)}",
            "action": "patch",
            "schema": state["schema"]
        }
    
    return state

def delete_item(state: CrudState):
    """Delete item by ID"""
    try:
        schema = state["schema"]
        item_id = state.get("item_id")
        
        if not item_id:
            state["result"] = {"error": "No item ID provided for delete operation"}
            return state
        
        # Delete from MongoDB
        result = db[schema].delete_one({"_id": ObjectId(item_id)})
        
        state["result"] = {
            "success": True,
            "deleted_count": result.deleted_count,
            "action": "delete",
            "schema": schema
        }
        
    except Exception as e:
        state["result"] = {
            "success": False,
            "error": f"Delete failed: {str(e)}",
            "action": "delete",
            "schema": state["schema"]
        }
    
    return state

# Build the LangGraph router
def genai_router():
    """Build and compile the LangGraph router"""
    graph = StateGraph(CrudState)
    
    # Add nodes
    graph.add_node("decide_crud", decide_crud_action)
    graph.add_node("insert", insert_item)
    graph.add_node("get_one", get_one_item)
    graph.add_node("get_all", get_all_items)
    graph.add_node("update", update_item)
    graph.add_node("patch", patch_item)
    graph.add_node("delete", delete_item)

    # Connect start to decision node
    graph.add_edge(START, "decide_crud")

    # Add conditional edges based on action
    graph.add_conditional_edges(
        "decide_crud",
        route_decision,
        {
            "insert": "insert",
            "get_one": "get_one",
            "get_all": "get_all",
            "update": "update",
            "patch": "patch",
            "delete": "delete",
        },
    )

    # All CRUD nodes connect to END
    for node in ["insert", "get_one", "get_all", "update", "patch", "delete"]:
        graph.add_edge(node, END)

    # Compile and return the graph
    return graph.compile()

# Example usage function
def process_query(user_input: str) -> dict:
    """
    Process a natural language query and return results
    
    Examples:
    - "Create a user with name John and email john@example.com"
    - "Update user 507f1f77bcf86cd799439011 set name to Jane"
    - "Delete contact with id 507f1f77bcf86cd799439012"
    - "Get all users with email containing @example.com"
    """
    router = genai_router()
    
    initial_state = CrudState(
        user_input=user_input,
        action="",
        schema="",
        item_id=None,
        item=None,
        result=None,
        query=None,
        error=None
    )
    
    final_state = router.invoke(initial_state)
    return final_state["result"]
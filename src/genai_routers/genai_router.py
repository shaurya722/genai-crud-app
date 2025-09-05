import os
import json
from dotenv import load_dotenv
from typing import TypedDict, Optional, Any
from pymongo import MongoClient
from bson import ObjectId

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph, START, END

from .schemas import *  # Import all schemas

# Load environment variables
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

# MongoDB connection
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]

# Gemini model
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.1
)

# Map schema names to classes and collection names
SCHEMA_MAP = {
    cls.__name__.replace("Schema", "").lower(): cls
    for cls in [
        CategoriesSchema, ContactsSchema, SettingsSchema, CompaniesSchema, TasksSchema,
        PermissionsSchema, Chat_listsSchema, LogsSchema, EmailLogsSchema, HelpCenterSchema,
        FriendsSchema, StaticPagesSchema, NotificationsSchema, ManualLogsSchema, RolesSchema,
        UsersSchema, ChatsSchema, JobsSchema, EmailTemplatesSchema, AdminsSchema
    ]
}

# Graph State
class CrudState(TypedDict):
    user_input: str
    action: str
    schema: str
    item_id: Optional[str]
    item: Optional[dict]
    result: Optional[Any]

# Gemini decision node
def decide_crud_action(state: CrudState):
    prompt = f"""
    Analyze the user query and determine:
    - action: one of ["insert", "get_one", "get_all", "update", "patch", "delete"]
    - schema: which schema/collection to use (e.g., users, companies, jobs, etc.)
    - item_id: string id if needed (null if not needed)
    - item: object with fields if needed (null if not needed)
    Respond with a JSON object.
    """
    prompt += f"\nUser Query: {state['user_input']}\n"
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        response_text = response.content.strip()
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        arguments = json.loads(response_text[start_idx:end_idx])
        # Validate
        if "action" not in arguments or "schema" not in arguments:
            raise ValueError("Missing keys in Gemini response")
        state.update(arguments)
        return state
    except Exception as e:
        # Fallback: naive keyword mapping
        user_input = state["user_input"].lower()
        for schema in SCHEMA_MAP:
            if schema in user_input:
                state["schema"] = schema
                break
        else:
            state["schema"] = "users"
        if any(w in user_input for w in ["add", "insert", "create", "new", "post"]):
            state["action"] = "insert"
        elif any(w in user_input for w in ["get all", "list", "fetch all", "show all"]):
            state["action"] = "get_all"
        elif any(w in user_input for w in ["get", "fetch", "show", "find"]):
            state["action"] = "get_one"
        elif any(w in user_input for w in ["update", "put"]):
            state["action"] = "update"
        elif "patch" in user_input:
            state["action"] = "patch"
        elif any(w in user_input for w in ["delete", "remove"]):
            state["action"] = "delete"
        else:
            state["action"] = "get_all"
        # Try to extract id
        import re
        id_match = re.search(r'id\s*([a-f0-9]{24}|\d+)', user_input)
        state["item_id"] = id_match.group(1) if id_match else None
        state["item"] = None
        return state

# Routing
def route_decision(state: CrudState):
    return state["action"]

# CRUD implementations
def insert_item(state: CrudState):
    schema = state["schema"]
    item = state.get("item", {})
    cls = SCHEMA_MAP[schema]
    validated = cls(**item).dict(exclude_unset=True)
    result = db[schema].insert_one(validated)
    state["result"] = {"inserted_id": str(result.inserted_id)}
    return state

def get_one_item(state: CrudState):
    schema = state["schema"]
    item_id = state.get("item_id")
    if not item_id:
        state["result"] = None
        return state
    doc = db[schema].find_one({"_id": ObjectId(item_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    state["result"] = doc
    return state

def get_all_items(state: CrudState):
    schema = state["schema"]
    docs = list(db[schema].find())
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    state["result"] = docs
    return state

def update_item(state: CrudState):
    schema = state["schema"]
    item_id = state.get("item_id")
    item = state.get("item", {})
    if not item_id or not item:
        state["result"] = None
        return state
    cls = SCHEMA_MAP[schema]
    validated = cls(**item).dict(exclude_unset=True)
    result = db[schema].replace_one({"_id": ObjectId(item_id)}, validated)
    state["result"] = {"matched_count": result.matched_count, "modified_count": result.modified_count}
    return state

def patch_item(state: CrudState):
    schema = state["schema"]
    item_id = state.get("item_id")
    item = state.get("item", {})
    if not item_id or not item:
        state["result"] = None
        return state
    result = db[schema].update_one({"_id": ObjectId(item_id)}, {"$set": item})
    state["result"] = {"matched_count": result.matched_count, "modified_count": result.modified_count}
    return state

def delete_item(state: CrudState):
    schema = state["schema"]
    item_id = state.get("item_id")
    if not item_id:
        state["result"] = None
        return state
    result = db[schema].delete_one({"_id": ObjectId(item_id)})
    state["result"] = {"deleted_count": result.deleted_count}
    return state

# Build LangGraph Workflow
def genai_router():
    graph = StateGraph(CrudState)
    graph.add_node("decide_crud", decide_crud_action)
    graph.add_node("insert", insert_item)
    graph.add_node("get_one", get_one_item)
    graph.add_node("get_all", get_all_items)
    graph.add_node("update", update_item)
    graph.add_node("patch", patch_item)
    graph.add_node("delete", delete_item)
    graph.add_edge(START, "decide_crud")
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
    for node in ["insert", "get_one", "get_all", "update", "patch", "delete"]:
        graph.add_edge(node, END)
    return graph.compile()
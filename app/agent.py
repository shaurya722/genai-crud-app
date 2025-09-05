import json
import re
from typing import Optional, Any, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph, START, END
from .crud import insert, get_one, get_all, update, patch, delete
from .config import db, GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.1
)

CRUD_MAP = {
    "insert": insert,
    "get_one": get_one,
    "get_all": get_all,
    "update": update,
    "patch": patch,
    "delete": delete
}

from typing import TypedDict, NotRequired

class CrudState(TypedDict):
    user_input: str
    action: NotRequired[Optional[str]]
    collection: NotRequired[Optional[str]]
    item_id: NotRequired[Optional[str]]
    item: NotRequired[Optional[Dict]]
    filter: NotRequired[Optional[Dict]]
    projection: NotRequired[Optional[Dict]]
    sort: NotRequired[Optional[list]]
    limit: NotRequired[Optional[int]]
    result: NotRequired[Optional[Any]]


# Decide which CRUD action and collection
def decide_action(state: CrudState):
    prompt = f"""
    Convert the human query to a MongoDB operation.
    Return JSON with fields:
    - action: insert/get_one/get_all/update/patch/delete
    - collection: collection name
    - item_id: if applicable
    - item: object for insert/update/patch
    - filter: MongoDB filter object
    - projection: fields to include/exclude
    - sort: list of [field, direction] pairs (1=asc, -1=desc)
    - limit: integer limit for results
    Human Query: "{state['user_input']}"
    """
    try:
        resp = llm.invoke([HumanMessage(content=prompt)])
        text = resp.content[0].strip()
        data = json.loads(text[text.find("{"):text.rfind("}")+1])
        state.update(data)
        return state
    except Exception:
        # fallback
        text = state["user_input"].lower()
        state["action"] = next((a for a in CRUD_MAP if a in text), "get_all")
        state["collection"] = next((c for c in db.list_collection_names() if c in text), db.list_collection_names()[0])
        state["item_id"] = re.search(r'id\s*([a-f0-9]{24}|\d+)', text).group(1) if re.search(r'id\s*([a-f0-9]{24}|\d+)', text) else None
        state["item"] = None
        state["filter"] = {}
        state["projection"] = None
        state["sort"] = None
        state["limit"] = None
        return state


def route_decision(state: CrudState):
    return state["action"]

# Build dynamic LangGraph
def build_agent():
    graph = StateGraph(CrudState)
    graph.add_node("decide_action", decide_action)
    for action, func in CRUD_MAP.items():
        def node(state, f=func, a=action):
            if a == "insert":
                return f(state["collection"], state.get("item") or {})
            elif a in ["update", "patch"]:
                return f(state["collection"], state.get("item_id"), state.get("item") or {})
            elif a == "get_one":
                return f(state["collection"], state.get("item_id"))
            elif a == "get_all":
                return f(
                    state["collection"],
                    state.get("filter") or {},
                    state.get("projection"),
                    state.get("sort"),
                    state.get("limit")
                )
            elif a == "delete":
                return f(state["collection"], state.get("item_id"))

        graph.add_node(action, node)
        graph.add_edge(action, END)
    graph.add_edge(START, "decide_action")
    graph.add_conditional_edges("decide_action", route_decision, {k: k for k in CRUD_MAP})
    return graph.compile()

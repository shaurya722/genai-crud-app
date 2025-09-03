import os
import json
from dotenv import load_dotenv
from typing import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, START, END

from ..models import SessionLocal
from ..models.schemas import ItemSchema

from ..utils.crud_function import insert_item, get_all_items, get_one_item, update_item


# Load environment variables
load_dotenv()

# Initialize Gemini model
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.1
)

# Dependency to get the database session
def get_db():
    db = SessionLocal() # create a new session from session local
    try:
        yield db # yield session to the callers
    finally:
        db.close() # closed when it's done

# Define Graph State to store all the data in Dictionary format
class CrudState(TypedDict):
    user_input: str
    action: str
    item_id: int = None
    item: ItemSchema = None
    result: dict = None

# 2. Decision Node: Uses Gemini to determine CRUD action
def decide_crud_action(state: CrudState):
    """Determines CRUD action from user query using Gemini with structured output."""

    print(f"\nUser input state: {state['user_input']}")
    if not state["user_input"]:  # Ensure key exists
        raise ValueError("Missing 'user_input' in state.")
    
    # Create a structured prompt for Gemini
    prompt = f"""
    Analyze the following user query and determine the appropriate CRUD operation.
    
    User Query: {state['user_input']}
    
    Please respond with a JSON object that contains:
    - action: one of ["insert", "get_one", "get_all", "update"]
    - item_id: integer ID if needed (null if not needed)
    - item: object with name and description if needed (null if not needed)
    
    Examples:
    - For "add a new laptop": {{"action": "insert", "item_id": null, "item": {{"name": "laptop", "description": "new laptop"}}}}
    - For "get all items": {{"action": "get_all", "item_id": null, "item": null}}
    - For "get item with id 5": {{"action": "get_one", "item_id": 5, "item": null}}
    - For "update item 3 to gaming laptop": {{"action": "update", "item_id": 3, "item": {{"name": "gaming laptop", "description": "updated gaming laptop"}}}}
    
    Respond only with the JSON object, no additional text.
    """
    
    try:
        # Get response from Gemini
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Parse the response to extract JSON
        response_text = response.content.strip()
        
        # Try to find JSON in the response
        if response_text.startswith('{') and response_text.endswith('}'):
            arguments = json.loads(response_text)
        else:
            # If response doesn't start with JSON, try to extract it
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                arguments = json.loads(json_str)
            else:
                raise ValueError("Could not parse JSON response from Gemini")
        
        # Validate the response structure
        if "action" not in arguments:
            raise ValueError("Missing 'action' in Gemini response")
        
        # Update state with the parsed arguments
        state.update(arguments)
        print(f"\nUpdated state after Gemini call: {state}")
        return state
        
    except Exception as e:
        print(f"Error in Gemini processing: {e}")
        # Fallback: try to determine action from keywords
        user_input_lower = state["user_input"].lower()
        
        if any(word in user_input_lower for word in ["add", "insert", "create", "new"]):
            state["action"] = "insert"
            state["item_id"] = None
            # Try to extract name and description from input
            if "laptop" in user_input_lower:
                state["item"] = {"name": "laptop", "description": "new laptop"}
            elif "phone" in user_input_lower or "smartphone" in user_input_lower:
                state["item"] = {"name": "smartphone", "description": "new smartphone"}
            else:
                state["item"] = {"name": "item", "description": "new item"}
        elif any(word in user_input_lower for word in ["get", "fetch", "retrieve", "show"]):
            if "all" in user_input_lower:
                state["action"] = "get_all"
                state["item_id"] = None
                state["item"] = None
            else:
                state["action"] = "get_one"
                # Try to extract ID
                import re
                id_match = re.search(r'id\s*(\d+)', user_input_lower)
                state["item_id"] = int(id_match.group(1)) if id_match else 1
                state["item"] = None
        elif any(word in user_input_lower for word in ["update", "modify", "change"]):
            state["action"] = "update"
            # Try to extract ID
            import re
            id_match = re.search(r'id\s*(\d+)', user_input_lower)
            state["item_id"] = int(id_match.group(1)) if id_match else 1
            state["item"] = {"name": "updated item", "description": "updated description"}
        else:
            state["action"] = "get_all"
            state["item_id"] = None
            state["item"] = None
        
        print(f"\nFallback state: {state}")
        return state


# 3. Conditional edge function to route to the appropriate node
def route_decision(state: CrudState):
    # Return the node name you want to visit next
    if state["action"] == "insert":
        return "insert"
    elif state["action"] == "get_one":
        return "get_one"
    elif state["action"] == "get_all":
        return "get_all"
    elif state["action"] == "update":
        return "update"
        
# 4. Build LangGraph Workflow
def genai_router():
    graph = StateGraph(CrudState)

    # Decision node
    graph.add_node("decide_crud", decide_crud_action)

    # CRUD nodes
    # calling next(get_db()) will start the generator function get_db(), 
    # which will yield the database session (db). 
    # The next() function then retrieves that session object and hands it to the caller.
    graph.add_node("insert", lambda state: insert_item(state, next(get_db())))
    graph.add_node("get_one", lambda state: get_one_item(state, next(get_db())))
    graph.add_node("get_all", lambda state: get_all_items(state, next(get_db())))
    graph.add_node("update", lambda state: update_item(state, next(get_db())))

    # Routing based on decision
    graph.add_edge(START, "decide_crud")
    graph.add_conditional_edges(
    "decide_crud",
    route_decision,
        {  # Name returned by route_decision : Name of next node to visit
            "insert": "insert",
            "get_one": "get_one",
            "get_all": "get_all",
            "update": "update",
        },
    )
    
    # All nodes lead to END
    graph.add_edge("insert", END)
    graph.add_edge("get_one", END)
    graph.add_edge("get_all", END)
    graph.add_edge("update", END)

    return graph.compile()

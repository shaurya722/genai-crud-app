from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .genai_router import genai_router, CrudState
from .serializers import serialize_mongodb_doc
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from datetime import datetime
from .serializers import serialize_mongodb_doc as serialize_doc
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


agent = genai_router()  # Build the agent

class QueryRequest(BaseModel):
    query: str


# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["development"]   # replace with your db name
contacts_collection = db["contacts"]

def save_response_to_file(response: dict, filename="crud_history.json"):
    """
    Append a CRUD response to a JSON file for tracking history.
    """
    try:
        # Load existing history if file exists
        try:
            with open(filename, "r") as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []

        # Add timestamp to response
        response["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Append the new response
        history.append(response)

        # Save back to file
        with open(filename, "w") as f:
            json.dump(history, f, indent=4)

        print(f"Response saved to {filename}")

    except Exception as e:
        print(f"Failed to save response: {e}")


@app.get("/contacts")
def get_contacts():
    contacts = list(contacts_collection.find())
    data = [serialize_doc(c) for c in contacts]

    response = {
        "result": {
            "success": True,
            "data": data,
            "count": len(data),
            "action": "get_all",
            "schema": "contacts",
            "query": None
        }
    }
    return JSONResponse(content=response)

# @app.post("/query")
# async def query(req: QueryRequest):
#     try:
#         # Initialize state as a dictionary
#         state: CrudState = {
#             "user_input": req.query,
#             "query": req.query ,  # Add required query field
#             "action": "",
#             "schema": "",
#             "item_id": "",
#             "item": None,
#             "result": None,
#             "error": None,  # Add required error field
#         }
        
#         # Run the LangGraph agent asynchronously
#         result_state = await agent.ainvoke(state)
#         if not result_state or "result" not in result_state:
#             raise HTTPException(status_code=400, detail="Invalid query result")
        
#         # Serialize the result before returning
#         serialized_result = serialize_mongodb_doc(result_state.get("result"))
#         return {"result": serialized_result}
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query(req: QueryRequest):
    try:
        # Initialize state as a dictionary
        state: CrudState = {
            "user_input": req.query,
            "query": req.query,   # raw query string from user
            "action": "",
            "schema": "",
            "item_id": "",
            "item": None,
            "result": None,
            "error": None,
        }
        
        # Run the LangGraph agent asynchronously
        result_state = await agent.ainvoke(state)
        if not result_state or "result" not in result_state:
            raise HTTPException(status_code=400, detail="Invalid query result")
        
        # Serialize the MongoDB result
        serialized_result = serialize_mongodb_doc(result_state.get("result"))

        # Add the query as a new key
        serialized_result["query"] = req.query
        serialized_result["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # # ✅ Return full response with query info
        # return {
        #     "result": {
        #         "data": serialized_result,
        #         "query": req.query
        #     }
        # }
        save_response_to_file(serialized_result)  # Save to file for history tracking
        return serialized_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

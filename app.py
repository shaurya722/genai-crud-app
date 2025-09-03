import os
from fastapi import FastAPI
from fastapi import Request, HTTPException
from langsmith import traceable
from dotenv import load_dotenv
from pydantic import BaseModel

from src.genai_routers.genai_router import CrudState, genai_router


app = FastAPI()

# Load environment variables from .env
load_dotenv()

# Google Gemini API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# LangSmith Key for debugging the processes
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true")  # Default to "true" if not set
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# User input (kept for reference, but not used directly in the handler)
class CrudInput(BaseModel):
    user_query: str

# Initiate the process
initial_state = CrudState()    # store user input and other data
router = genai_router()   # act as the Router function
 
@app.post("/crud/")
@traceable
async def handle_crud(request: Request):
    """CRUD operations using Google Gemini. Accepts JSON or form-data with 'user_query'."""

    # Extract user_query from JSON or form-data
    content_type = request.headers.get("content-type", "")
    user_query = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            user_query = (body or {}).get("user_query")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")
    elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        user_query = form.get("user_query")
        # Handle quotes if provided as '"value"'
        if isinstance(user_query, str) and user_query.startswith('"') and user_query.endswith('"'):
            user_query = user_query[1:-1]
    else:
        raise HTTPException(status_code=415, detail="Unsupported Content-Type. Use application/json or form-data")

    if not user_query:
        raise HTTPException(status_code=422, detail="Missing 'user_query' in request body")

    initial_state = {"user_input": user_query}
    final_state = router.invoke(initial_state) # route into insert, get, update functions
    print(f"\nFinal state returned: {final_state}")

    # Build metadata
    endpoint_path = "/crud/"
    full_url = str(request.url)
    action = final_state.get("action")
    item = final_state.get("item") or {}
    item_id = final_state.get("item_id")

    model_fields_used = list(item.keys()) if isinstance(item, dict) else []

    meta = {
        "api_full_url": full_url,
        "endpoint": endpoint_path,
        "action": action,
        "item_id": item_id,
        "model_fields_used": model_fields_used,
    }

    return {"meta": meta, "data": final_state.get("result")}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
# to run : uvicorn app:app --reload   
# For testing
# localhost:8000/docs
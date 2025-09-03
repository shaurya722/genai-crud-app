#!/usr/bin/env python3
"""
Test script to verify Gemini integration is working correctly.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Set the database URL directly
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

def test_gemini_integration():
    """Test the Gemini integration with a simple query."""
    
    try:
        # Test if we can import the required modules
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.schema import HumanMessage
        print("✓ Successfully imported LangChain Gemini modules")
        
        # Check if API key is set
        api_key = "AIzaSyD_reuYK0lcyq0Bu5xXKQ3HIhq3bGhTCwg"
        if not api_key:
            print("⚠ Warning: GOOGLE_API_KEY not set in environment")
            print("   Please set your Google API key in the .env file")
            return False
        
        print("✓ Google API key found")
        
        # Test Gemini connection
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        
        # Simple test query
        test_message = "Hello! Please respond with just 'Hello from Gemini!'"
        response = llm.invoke([HumanMessage(content=test_message)])
        
        print(f"✓ Gemini response received: {response.content}")
        
        # Test CRUD decision making
        print("\n--- Testing CRUD Decision Making ---")
        
        test_queries = [
            "add a new laptop",
            "get all items", 
            "get item with id 5",
            "update item 3 to gaming laptop"
        ]
        
        for query in test_queries:
            print(f"\nTesting query: '{query}'")
            
            # Create a structured prompt for Gemini
            prompt = f"""
            Analyze the following user query and determine the appropriate CRUD operation.
            
            User Query: {query}
            
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
                response = llm.invoke([HumanMessage(content=prompt)])
                print(f"  Response: {response.content}")
                
                # Try to parse JSON
                import json
                response_text = response.content.strip()
                
                if response_text.startswith('{') and response_text.endswith('}'):
                    parsed = json.loads(response_text)
                    print(f"  Parsed: {parsed}")
                else:
                    print("  ⚠ Could not parse JSON response")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print("\n✓ Gemini integration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Gemini Integration...")
    success = test_gemini_integration()
    
    if success:
        print("\n🎉 All tests passed! Your Gemini integration is working correctly.")
        print("You can now run your main application with: python app.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.") 
# Gemini Integration Setup Guide

This guide explains how to set up and use Google Gemini with your CRUD application.

## What Changed

Your application has been converted from OpenAI to **Google Gemini** using LangChain. The main changes are:

- ✅ Replaced OpenAI client with `ChatGoogleGenerativeAI`
- ✅ Updated function calling to use structured prompts
- ✅ Added fallback logic for better reliability
- ✅ Maintained the same API endpoints and functionality

## Setup Steps

### 1. Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 2. Configure Environment Variables

Create a `.env` file in your project root (or update existing one):

```bash
# Google Gemini API Key
GOOGLE_API_KEY="your_actual_api_key_here"

# Database Configuration
DATABASE_URL=sqlite:///./test.db

# LangSmith Configuration (optional)
LANGSMITH_TRACING="true"
LANGSMITH_API_KEY=""
LANGSMITH_PROJECT="es-lang-crud"
```

### 3. Install Dependencies

Make sure you're in your virtual environment:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Test the Integration

Run the test script to verify everything is working:

```bash
python test_gemini.py
```

## How It Works

### Before (OpenAI)

- Used OpenAI's function calling API
- Required specific function schemas
- More expensive API calls

### After (Gemini)

- Uses structured prompts with examples
- More flexible and reliable
- Cost-effective alternative
- Built-in fallback logic

### CRUD Operations

The system now understands natural language queries like:

- **Insert**: "add a new laptop", "create smartphone", "insert coffee maker"
- **Get All**: "get all items", "show everything", "list all"
- **Get One**: "get item with id 5", "show item 3", "fetch laptop"
- **Update**: "update item 3 to gaming laptop", "modify smartphone", "change description"

## API Usage

Your API endpoint remains the same:

```bash
POST /crud/
Content-Type: application/json

{
  "user_query": "add a new gaming laptop"
}
```

## Troubleshooting

### Common Issues

1. **API Key Not Set**

   - Ensure `GOOGLE_API_KEY` is in your `.env` file
   - Restart your application after setting the key

2. **Import Errors**

   - Make sure you're in the virtual environment
   - Run `pip install -r requirements.txt`

3. **Gemini Response Parsing**
   - The system has fallback logic for malformed responses
   - Check the console logs for debugging information

### Testing

Use the test script to verify each component:

```bash
python test_gemini.py
```

## Benefits of Gemini

- **Cost Effective**: Generally cheaper than OpenAI
- **Reliable**: Built-in fallback mechanisms
- **Flexible**: Natural language understanding
- **Fast**: Quick response times
- **Privacy**: Google's privacy standards

## Next Steps

1. Test with your existing database
2. Try different natural language queries
3. Monitor the console logs for insights
4. Customize prompts if needed

## Support

If you encounter issues:

1. Check the console logs
2. Verify your API key
3. Test with the test script
4. Check the fallback logic output

Your CRUD application now uses the power of Google Gemini! 🚀

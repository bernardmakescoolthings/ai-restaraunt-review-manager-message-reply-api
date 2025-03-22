# Message Response API

A FastAPI service that generates AI responses based on a given personality profile and message using OpenAI's GPT models. This service allows you to get contextual responses while controlling the AI's personality through a profile description.

## Features

- Generate responses using OpenAI's GPT-3.5-turbo model
- Customize AI personality through profile descriptions
- RESTful API with FastAPI
- Comprehensive test suite
- Environment-based configuration

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   └── main.py          # Main FastAPI application
├── tests/
│   ├── __init__.py
│   └── test_main.py     # Test suite
├── requirements.txt     # Project dependencies
├── pytest.ini          # Pytest configuration
├── .env.example        # Environment variables template
└── README.md
```

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (get one at https://platform.openai.com/api-keys)
- Virtual environment (recommended)

## Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd message-response-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Running the Service

Start the service using uvicorn:
```bash
uvicorn src.main:app --reload
```

The service will be available at `http://localhost:8000`

## Local Deployment

### Method 1: Using uvicorn directly

1. Make sure you're in the project directory and your virtual environment is activated:
   ```bash
   cd message-response-api
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Start the service:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Options explained:
   - `--reload`: Auto-reloads the server when code changes (development only)
   - `--host 0.0.0.0`: Makes the server accessible from other devices on the network
   - `--port 8000`: Specifies the port number (default is 8000)

3. The service will be available at:
   - Local access: `http://localhost:8000`
   - Network access: `http://<your-ip-address>:8000`

### Method 2: Using the test script

1. Make the test script executable:
   ```bash
   chmod +x test_api.sh
   ```

2. Start the service in one terminal:
   ```bash
   uvicorn src.main:app --reload
   ```

3. In another terminal, run the test script:
   ```bash
   ./test_api.sh
   ```

### Method 3: Using Docker (Optional)

1. Create a Dockerfile:
   ```dockerfile
   FROM python:3.10-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. Build and run the Docker container:
   ```bash
   docker build -t message-response-api .
   docker run -p 8000:8000 --env-file .env message-response-api
   ```

### Verifying the Deployment

1. Check if the service is running:
   ```bash
   curl http://localhost:8000/
   ```
   Expected response:
   ```json
   {
       "message": "Welcome to the Message Response API"
   }
   ```

2. Access the API documentation:
   - Open `http://localhost:8000/docs` in your browser
   - You should see the Swagger UI with all available endpoints

3. Test the API endpoint:
   ```bash
   curl -X POST "http://localhost:8000/get_message_response" \
   -H "Content-Type: application/json" \
   -d '{
       "profile": "You are a friendly assistant",
       "message": "Hello!"
   }'
   ```

### Troubleshooting Local Deployment

1. Port already in use:
   ```bash
   # Find the process using port 8000
   lsof -i :8000
   # Kill the process
   kill -9 <PID>
   ```

2. Permission issues:
   ```bash
   # Make sure you have the right permissions
   chmod +x test_api.sh
   ```

3. Virtual environment issues:
   ```bash
   # Deactivate and reactivate the virtual environment
   deactivate
   source venv/bin/activate
   ```

4. Environment variables:
   ```bash
   # Check if environment variables are loaded
   cat .env
   ```

## Testing Locally with Real API Calls

1. Ensure your OpenAI API key is set in the `.env` file

2. Start the service:
   ```bash
   uvicorn src.main:app --reload
   ```

3. Test using curl:
   ```bash
   curl -X POST "http://localhost:8000/get_message_response" \
   -H "Content-Type: application/json" \
   -d '{
       "profile": "You are a friendly restaurant critic who loves to give detailed reviews",
       "message": "What did you think of the pasta carbonara?"
   }'
   ```

4. Or use the Swagger UI:
   - Open `http://localhost:8000/docs` in your browser
   - Click on the POST `/get_message_response` endpoint
   - Click "Try it out"
   - Edit the request body
   - Click "Execute"

Example Profiles to Try:
```json
{
    "profile": "You are a witty comedian who loves puns",
    "message": "Tell me a joke about programming"
}
```

```json
{
    "profile": "You are a formal business consultant",
    "message": "What do you think about remote work?"
}
```

```json
{
    "profile": "You are a friendly tech support agent",
    "message": "My computer is running slowly"
}
```

Troubleshooting:
- If you get a 500 error, check that your API key is correctly set in the `.env` file
- If you get a 422 error, check your request body format
- Make sure your OpenAI API key has sufficient credits
- Check the server logs for detailed error messages

## API Endpoints

### GET /
Welcome endpoint that returns a simple message.

**Response:**
```json
{
    "message": "Welcome to the Message Response API"
}
```

### POST /get_message_response

Generate an AI response based on a personality profile and message.

**Request Body:**
```json
{
    "profile": "A friendly and professional customer service representative",
    "message": "Hello, I have a question about your services"
}
```

**Response:**
```json
{
    "response": "Generated response from the AI"
}
```

**Parameters:**
- `profile` (string): Description of the AI assistant's personality
- `message` (string): The message to get a response for

**Error Responses:**
- 422: Validation Error (missing required fields)
- 500: Server Error (OpenAI API issues or missing API key)

## Testing

The project includes a comprehensive test suite using pytest. The tests cover:
- Basic endpoint functionality
- Successful message response generation
- Error handling
- Input validation
- Edge cases

To run the tests:
```bash
pytest
```

For verbose output:
```bash
pytest -v
```

The tests use mocking to avoid making actual API calls to OpenAI, ensuring reliable and fast test execution.

## API Documentation

Once the service is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The service includes robust error handling for:
- Missing OpenAI API key
- Invalid requests
- OpenAI API errors
- Missing required fields

## Development

The service is built with:
- FastAPI for the web framework
- Pydantic for data validation
- OpenAI's Python client for AI integration
- Pytest for testing

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required for actual API calls)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests
5. Submit a pull request

## License

[Add your license information here] 
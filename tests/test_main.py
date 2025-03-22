import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns correct welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Message Response API"}

def test_get_message_response_success():
    """Test successful message response generation"""
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="This is a test response"
            )
        )
    ]

    with patch("src.main.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = client.post(
            "/get_message_response",
            json={
                "profile": "A friendly assistant",
                "message": "Hello, how are you?"
            }
        )
        
        assert response.status_code == 200
        assert response.json() == {"response": "This is a test response"}

def test_get_message_response_invalid_input():
    """Test message response with invalid input"""
    with patch("src.main.client") as mock_client:
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Empty profile response"))]
        )
        response = client.post(
            "/get_message_response",
            json={
                "profile": "",  # Empty profile
                "message": "Hello"
            }
        )
        
        assert response.status_code == 200
        assert response.json() == {"response": "Empty profile response"}

def test_get_message_response_openai_error():
    """Test message response when OpenAI API fails"""
    with patch("src.main.client") as mock_client:
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        response = client.post(
            "/get_message_response",
            json={
                "profile": "A friendly assistant",
                "message": "Hello"
            }
        )
        
        assert response.status_code == 500
        assert "API Error" in response.json()["detail"]

def test_get_message_response_missing_fields():
    """Test message response with missing required fields"""
    response = client.post(
        "/get_message_response",
        json={
            "profile": "A friendly assistant"
            # Missing message field
        }
    )
    
    assert response.status_code == 422  # Validation error 
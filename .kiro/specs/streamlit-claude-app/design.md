# Design Document

## Overview

The Streamlit Claude App is a web application that provides secure user authentication and AI-powered prompt generation using Claude 3 Sonnet via OpenRouter API. The application features a clean, modern interface with session management, user activity logging, and API key rotation for reliability.

## Architecture

The application follows a simple client-server architecture using Streamlit as the web framework:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  Application     │────│  External APIs  │
│   (Frontend)    │    │  Logic           │    │  (OpenRouter)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Local Storage   │
                       │  (user_log.csv)  │
                       └──────────────────┘
```

## Components and Interfaces

### 1. Authentication Module
- **Purpose**: Handle user login/logout functionality
- **Functions**:
  - `authenticate_user(username, password)`: Validates user credentials against predefined users
  - `logout_user()`: Clears session state and redirects to login
- **Session Management**: Uses Streamlit session state to track authentication status
- **Login Criteria**: Simple username/password validation (can be hardcoded or from config)

### 2. User Logging Module
- **Purpose**: Track and store user login activities in CSV format
- **Functions**:
  - `log_user_activity(username)`: Appends user login data to user_log.csv file
  - `create_log_file()`: Creates user_log.csv with headers if it doesn't exist
  - `ensure_csv_exists()`: Checks and creates CSV file before logging
- **File Structure**: CSV with columns: username, login_timestamp, session_id
- **Storage Location**: user_log.csv in the application root directory
- **Data Persistence**: All login activities are permanently stored and accumulated

### 3. API Integration Module
- **Purpose**: Handle Claude 3 Sonnet API interactions via OpenRouter
- **Functions**:
  - `load_api_keys()`: Loads 4 API keys from .env file
  - `get_random_api_key()`: Returns a randomly selected API key
  - `generate_response(prompt, api_key)`: Sends request to Claude API
- **API Endpoint**: OpenRouter API for Claude 3 Sonnet
- **Rate Limiting**: Random key rotation across 4 keys

### 4. UI Components
- **Login Page**: Username/password form with error handling
- **Main App Page**: Prompt input, generate button, response display
- **Layout**: Clean design using Streamlit columns and containers

## Data Models

### User Log Entry
```python
{
    "username": str,
    "login_timestamp": datetime,
    "session_id": str,
}
```

### API Request/Response
```python
# Request
{
    "model": "anthropic/claude-3-sonnet",
    "messages": [{"role": "user", "content": str}],
    "headers": {"Authorization": f"Bearer {api_key}"}
}

# Response
{
    "choices": [{"message": {"content": str}}]
}
```

### Session State
```python
{
    "authenticated": bool,
    "username": str,
    "api_keys": list[str]
}
```

## Error Handling

### Authentication Errors
- Invalid credentials: Display user-friendly error message
- Session timeout: Redirect to login page

### API Errors
- Invalid API key: Try next available key, log error
- Rate limiting: Implement exponential backoff
- Network errors: Display connection error message
- Missing .env file: Show configuration error

### File I/O Errors
- CSV creation failure: Log error and continue without logging
- Permission errors: Display appropriate error message

## Testing Strategy

### Unit Tests
- Authentication functions with valid/invalid credentials
- API key loading and rotation logic
- CSV file creation and writing operations
- Response parsing and error handling

### Integration Tests
- End-to-end login flow
- Complete prompt generation workflow
- File logging functionality
- API integration with mock responses

### UI Tests
- Form validation and submission
- Session state management
- Error message display
- Responsive layout testing

## Security Considerations

### API Key Management
- Store keys in .env file (not in code)
- Use environment variables for production
- Implement key rotation to prevent abuse

### User Data Protection
- No sensitive data stored in logs
- Session state cleared on logout
- Input validation for all user inputs

### Deployment Security
- .env file excluded from version control
- Secure environment variable handling in Hugging Face Spaces
- Input sanitization for prompts

## Deployment Configuration

### File Structure
```
streamlit-claude-app/
├── app.py                 # Main Streamlit application
├── auth.py               # Authentication utilities
├── api_client.py         # API integration functions
├── utils.py              # Helper functions
├── user_log.csv          # User login activity log (auto-created)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (API keys)
├── .env.example         # Example environment file
└── README.md            # Deployment instructions
```

### Dependencies
- streamlit
- python-dotenv
- requests
- pandas
- datetime

### Environment Variables
```
OPENROUTER_API_KEY_1=your_key_1
OPENROUTER_API_KEY_2=your_key_2
OPENROUTER_API_KEY_3=your_key_3
OPENROUTER_API_KEY_4=your_key_4
```
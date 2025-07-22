"""
Authentication module for the Streamlit Claude App
"""
import streamlit as st
import csv
import os
from typing import Dict, Optional
from utils import log_user_activity, clear_session_state


# Simple user credentials (in production, this would be in a database)
VALID_USERS = {
    "admin": "password123",
    "user": "user123",
    "demo": "demo123",
    "test": "test123"
}

USERS_CSV_FILE = "users.csv"


def ensure_users_csv_exists() -> None:
    """
    Ensures that the users.csv file exists with proper headers.
    Creates the file if it doesn't exist.
    """
    if not os.path.exists(USERS_CSV_FILE):
        create_users_csv()


def create_users_csv() -> None:
    """
    Creates the users.csv file with appropriate headers.
    """
    headers = ["username", "password", "registration_date", "email"]
    
    try:
        with open(USERS_CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    except Exception as e:
        st.error(f"Error creating users CSV file: {str(e)}")


def load_users_from_csv() -> Dict[str, str]:
    """
    Loads users from CSV file and returns username:password dictionary.
    
    Returns:
        Dict[str, str]: Dictionary of username: password pairs
    """
    users = VALID_USERS.copy()  # Start with default users
    
    ensure_users_csv_exists()
    
    try:
        with open(USERS_CSV_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users[row['username']] = row['password']
    except Exception as e:
        st.error(f"Error loading users from CSV: {str(e)}")
    
    return users


def save_user_to_csv(username: str, password: str, email: str = "") -> bool:
    """
    Saves a new user to the CSV file.
    
    Args:
        username (str): Username
        password (str): Password
        email (str): Email address (optional)
        
    Returns:
        bool: True if successful, False otherwise
    """
    ensure_users_csv_exists()
    
    from datetime import datetime
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(USERS_CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, password, registration_date, email])
        return True
    except Exception as e:
        st.error(f"Error saving user to CSV: {str(e)}")
        return False


def user_exists(username: str) -> bool:
    """
    Checks if a username already exists.
    
    Args:
        username (str): Username to check
        
    Returns:
        bool: True if user exists, False otherwise
    """
    users = load_users_from_csv()
    return username in users


def register_user(username: str, password: str, email: str = "") -> Dict[str, any]:
    """
    Registers a new user.
    
    Args:
        username (str): Username
        password (str): Password
        email (str): Email address (optional)
        
    Returns:
        Dict[str, any]: Registration result with success status and message
    """
    # Validate inputs
    validation_error = validate_registration_form(username, password, email)
    if validation_error:
        return {
            "success": False,
            "message": validation_error
        }
    
    # Check if user already exists
    if user_exists(username):
        return {
            "success": False,
            "message": "❌ Username already exists. Please choose a different username."
        }
    
    # Save user to CSV
    if save_user_to_csv(username, password, email):
        return {
            "success": True,
            "message": f"✅ Registration successful! Welcome, {username}! You can now log in."
        }
    else:
        return {
            "success": False,
            "message": "❌ Registration failed. Please try again."
        }


def validate_registration_form(username: str, password: str, email: str = "") -> Optional[str]:
    """
    Validates registration form inputs.
    
    Args:
        username (str): Username input
        password (str): Password input
        email (str): Email input (optional)
        
    Returns:
        Optional[str]: Error message if validation fails, None if valid
    """
    if not username.strip():
        return "Username cannot be empty"
    
    if not password.strip():
        return "Password cannot be empty"
    
    if len(username.strip()) < 3:
        return "Username must be at least 3 characters long"
    
    if len(password.strip()) < 6:
        return "Password must be at least 6 characters long"
    
    # Check for invalid characters in username
    if not username.replace('_', '').replace('-', '').isalnum():
        return "Username can only contain letters, numbers, hyphens, and underscores"
    
    # Basic email validation if provided
    if email and '@' not in email:
        return "Please enter a valid email address"
    
    return None


def get_user_count() -> int:
    """
    Returns the total number of registered users.
    
    Returns:
        int: Number of registered users
    """
    users = load_users_from_csv()
    return len(users)


def authenticate_user(username: str, password: str) -> bool:
    """
    Validates user credentials against both default and CSV users.
    
    Args:
        username (str): The username to validate
        password (str): The password to validate
        
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    if not username or not password:
        return False
    
    users = load_users_from_csv()
    return users.get(username) == password


def login_user(username: str, password: str) -> Dict[str, any]:
    """
    Handles user login process including validation and session setup.
    
    Args:
        username (str): The username
        password (str): The password
        
    Returns:
        Dict[str, any]: Login result with success status and message
    """
    if authenticate_user(username, password):
        # Set session state
        st.session_state.authenticated = True
        st.session_state.username = username
        
        # Log user activity
        log_user_activity(username)
        
        return {
            "success": True,
            "message": f"Welcome, {username}! Login successful.",
            "username": username
        }
    else:
        return {
            "success": False,
            "message": "❌ Invalid username or password. Please try again.",
            "username": None
        }


def logout_user() -> None:
    """
    Handles user logout by clearing session state.
    """
    username = st.session_state.get('username', 'Unknown')
    clear_session_state()
    st.success(f"👋 Goodbye, {username}! You have been logged out successfully.")
    st.rerun()


def is_authenticated() -> bool:
    """
    Checks if the current user is authenticated.
    
    Returns:
        bool: True if user is authenticated, False otherwise
    """
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[str]:
    """
    Gets the current authenticated username.
    
    Returns:
        Optional[str]: Username if authenticated, None otherwise
    """
    if is_authenticated():
        return st.session_state.get('username')
    return None


def require_authentication() -> bool:
    """
    Decorator-like function to require authentication for a page.
    Redirects to login if not authenticated.
    
    Returns:
        bool: True if authenticated, False if redirected to login
    """
    if not is_authenticated():
        st.warning("🔒 Please log in to access this page.")
        return False
    return True


def get_available_users() -> Dict[str, str]:
    """
    Returns available demo users for testing purposes.
    
    Returns:
        Dict[str, str]: Dictionary of username: password pairs
    """
    return VALID_USERS.copy()


def validate_login_form(username: str, password: str) -> Optional[str]:
    """
    Validates login form inputs and returns error message if invalid.
    
    Args:
        username (str): Username input
        password (str): Password input
        
    Returns:
        Optional[str]: Error message if validation fails, None if valid
    """
    if not username.strip():
        return "Username cannot be empty"
    
    if not password.strip():
        return "Password cannot be empty"
    
    if len(username.strip()) < 2:
        return "Username must be at least 2 characters long"
    
    if len(password.strip()) < 3:
        return "Password must be at least 3 characters long"
    
    return None
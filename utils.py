"""
Utility functions for the Streamlit Claude App
"""
import csv
import os
import uuid
from datetime import datetime
from typing import Optional
import streamlit as st
from fpdf import FPDF
import io


def ensure_csv_exists() -> None:
    """
    Ensures that the user_log.csv file exists with proper headers.
    Creates the file if it doesn't exist.
    """
    csv_file = "user_log.csv"
    
    if not os.path.exists(csv_file):
        create_log_file()


def create_log_file() -> None:
    """
    Creates the user_log.csv file with appropriate headers.
    """
    csv_file = "user_log.csv"
    headers = ["username", "login_timestamp", "session_id"]
    
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    except Exception as e:
        st.error(f"Error creating log file: {str(e)}")


def log_user_activity(username: str) -> None:
    """
    Logs user login activity to the CSV file.
    
    Args:
        username (str): The username of the logged-in user
    """
    ensure_csv_exists()
    
    csv_file = "user_log.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_id = str(uuid.uuid4())[:8]  # Short session ID
    
    try:
        with open(csv_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, timestamp, session_id])
        
        # Store session ID in session state for reference
        st.session_state.session_id = session_id
        
    except Exception as e:
        st.error(f"Error logging user activity: {str(e)}")


def get_user_log_stats() -> dict:
    """
    Returns statistics about user login activities.
    
    Returns:
        dict: Statistics including total logins, unique users, etc.
    """
    csv_file = "user_log.csv"
    
    if not os.path.exists(csv_file):
        return {
            "total_logins": 0,
            "unique_users": 0,
            "recent_logins": []
        }
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        total_logins = len(rows)
        unique_users = len(set(row['username'] for row in rows))
        recent_logins = rows[-5:] if rows else []  # Last 5 logins
        
        return {
            "total_logins": total_logins,
            "unique_users": unique_users,
            "recent_logins": recent_logins
        }
    
    except Exception as e:
        st.error(f"Error reading user log stats: {str(e)}")
        return {
            "total_logins": 0,
            "unique_users": 0,
            "recent_logins": []
        }


def initialize_session_state() -> None:
    """
    Initializes the Streamlit session state with default values.
    """
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'username' not in st.session_state:
        st.session_state.username = ""
    
    if 'api_keys' not in st.session_state:
        st.session_state.api_keys = []


def clear_session_state() -> None:
    """
    Clears the session state for logout functionality.
    """
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.api_keys = []


def get_session_info() -> dict:
    """
    Returns current session information.
    
    Returns:
        dict: Session information including authentication status and username
    """
    return {
        'authenticated': st.session_state.get('authenticated', False),
        'username': st.session_state.get('username', ''),
        'api_keys_loaded': len(st.session_state.get('api_keys', [])) > 0
    }

def create_pdf_from_conversation(prompt: str, response: str, username: str, model_used: str) -> bytes:
    """
    Creates a PDF from the conversation between user and AI.
    
    Args:
        prompt (str): User's prompt
        response (str): AI's response
        username (str): Username
        model_used (str): Model that generated the response
        
    Returns:
        bytes: PDF file as bytes
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Set font
        pdf.set_font('Arial', 'B', 16)
        
        # Title
        pdf.cell(0, 10, 'Swayam Sites - Conversation Export', 0, 1, 'C')
        pdf.ln(10)
        
        # User info
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'User: {username}', 0, 1)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
        pdf.cell(0, 10, f'Model: {model_used}', 0, 1)
        pdf.ln(5)
        
        # Prompt section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Your Prompt:', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        # Add prompt text with safe encoding
        safe_prompt = prompt.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, safe_prompt)
        pdf.ln(5)
        
        # Response section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'AI Response:', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        # Add response text with safe encoding
        safe_response = response.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, safe_response)
        
        # Convert to bytes - handle different FPDF versions
        try:
            # Method 1: For fpdf2
            return pdf.output()
        except:
            try:
                # Method 2: For older fpdf
                pdf_output = io.BytesIO()
                pdf_string = pdf.output(dest='S')
                if isinstance(pdf_string, str):
                    pdf_output.write(pdf_string.encode('latin-1'))
                else:
                    pdf_output.write(pdf_string)
                pdf_output.seek(0)
                return pdf_output.getvalue()
            except:
                # Method 3: Last resort
                return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        # Return a simple text file as fallback
        text_content = f"""CONVERSATION EXPORT
User: {username}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Model: {model_used}

YOUR PROMPT:
{prompt}

AI RESPONSE:
{response}
"""
        return text_content.encode('utf-8')


def get_model_display_name(model: str) -> str:
    """
    Returns a user-friendly display name for the model.
    
    Args:
        model (str): Technical model name
        
    Returns:
        str: User-friendly model name
    """
    model_names = {
        "deepseek/deepseek-chat": "DeepSeek Chat",
        "google/gemini-2.0-flash-exp:free": "Gemini 2.5 Pro",
        "01-ai/yi-large": "Yi Large (Kimi K2)",
        "qwen/qwen-2.5-72b-instruct": "Qwen 2.5 72B"
    }
    
    return model_names.get(model, model)
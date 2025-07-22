"""
Analytics module for tracking conversation history and usage statistics
"""
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st


# File paths
HISTORY_DIR = "conversation_history"
ANALYTICS_FILE = "analytics_data.json"


def ensure_history_dir() -> None:
    """
    Ensures that the conversation history directory exists.
    Creates it if it doesn't exist.
    """
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)


def save_conversation(
    username: str,
    prompt: str,
    response: str,
    model: str,
    response_time: float,
    prompt_tokens: int,
    response_tokens: int
) -> str:
    """
    Saves a conversation to the history directory.
    
    Args:
        username (str): Username
        prompt (str): User's prompt
        response (str): AI's response
        model (str): Model used
        response_time (float): Response time in seconds
        prompt_tokens (int): Number of tokens in prompt
        response_tokens (int): Number of tokens in response
        
    Returns:
        str: Filename of saved conversation
    """
    ensure_history_dir()
    
    # Create conversation data
    conversation_data = {
        "username": username,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "response": response,
        "model": model,
        "response_time": response_time,
        "prompt_tokens": prompt_tokens,
        "response_tokens": response_tokens,
        "total_tokens": prompt_tokens + response_tokens
    }
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{HISTORY_DIR}/{username}_{timestamp}.json"
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, indent=2)
    
    # Update analytics
    update_analytics(conversation_data)
    
    return filename


def update_analytics(conversation_data: Dict[str, Any]) -> None:
    """
    Updates analytics data with new conversation.
    
    Args:
        conversation_data (Dict[str, Any]): Conversation data
    """
    analytics = load_analytics()
    
    # Update model usage count
    model = conversation_data["model"]
    if model in analytics["model_usage"]:
        analytics["model_usage"][model] += 1
    else:
        analytics["model_usage"][model] = 1
    
    # Update total conversations
    analytics["total_conversations"] += 1
    
    # Update total tokens
    analytics["total_tokens"] += conversation_data["total_tokens"]
    
    # Update average response time
    new_count = analytics["total_conversations"]
    old_avg = analytics["avg_response_time"]
    new_time = conversation_data["response_time"]
    analytics["avg_response_time"] = ((old_avg * (new_count - 1)) + new_time) / new_count
    
    # Update user stats
    username = conversation_data["username"]
    if username in analytics["user_activity"]:
        analytics["user_activity"][username] += 1
    else:
        analytics["user_activity"][username] = 1
    
    # Save updated analytics
    save_analytics(analytics)


def load_analytics() -> Dict[str, Any]:
    """
    Loads analytics data from file.
    
    Returns:
        Dict[str, Any]: Analytics data
    """
    if not os.path.exists(ANALYTICS_FILE):
        # Create default analytics data
        return {
            "total_conversations": 0,
            "total_tokens": 0,
            "avg_response_time": 0,
            "model_usage": {},
            "user_activity": {}
        }
    
    try:
        with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
        return {
            "total_conversations": 0,
            "total_tokens": 0,
            "avg_response_time": 0,
            "model_usage": {},
            "user_activity": {}
        }


def save_analytics(analytics_data: Dict[str, Any]) -> None:
    """
    Saves analytics data to file.
    
    Args:
        analytics_data (Dict[str, Any]): Analytics data
    """
    try:
        with open(ANALYTICS_FILE, 'w', encoding='utf-8') as f:
            json.dump(analytics_data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving analytics: {str(e)}")


def get_user_conversations(username: str) -> List[Dict[str, Any]]:
    """
    Gets all conversations for a specific user.
    
    Args:
        username (str): Username
        
    Returns:
        List[Dict[str, Any]]: List of conversation data
    """
    ensure_history_dir()
    
    conversations = []
    
    # Get all files in history directory
    for filename in os.listdir(HISTORY_DIR):
        if filename.startswith(f"{username}_") and filename.endswith(".json"):
            try:
                with open(f"{HISTORY_DIR}/{filename}", 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
                    conversations.append(conversation)
            except Exception as e:
                st.error(f"Error loading conversation {filename}: {str(e)}")
    
    # Sort by timestamp (newest first)
    conversations.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return conversations


def get_analytics_summary() -> Dict[str, Any]:
    """
    Gets a summary of analytics data.
    
    Returns:
        Dict[str, Any]: Analytics summary
    """
    analytics = load_analytics()
    
    # Get top models
    model_usage = analytics["model_usage"]
    top_models = sorted(model_usage.items(), key=lambda x: x[1], reverse=True)
    
    # Get top users
    user_activity = analytics["user_activity"]
    top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "total_conversations": analytics["total_conversations"],
        "total_tokens": analytics["total_tokens"],
        "avg_response_time": round(analytics["avg_response_time"], 2),
        "top_models": top_models[:5],  # Top 5 models
        "top_users": top_users[:5],    # Top 5 users
    }


def export_user_history_json(username: str) -> Optional[bytes]:
    """
    Exports all user conversations as a single JSON file.
    
    Args:
        username (str): Username
        
    Returns:
        Optional[bytes]: JSON file as bytes or None if error
    """
    conversations = get_user_conversations(username)
    
    if not conversations:
        return None
    
    try:
        # Create export data
        export_data = {
            "username": username,
            "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "conversation_count": len(conversations),
            "conversations": conversations
        }
        
        # Convert to JSON string
        json_str = json.dumps(export_data, indent=2)
        
        # Convert to bytes
        return json_str.encode('utf-8')
    
    except Exception as e:
        st.error(f"Error exporting history: {str(e)}")
        return None


def count_tokens(text: str) -> int:
    """
    Counts the approximate number of tokens in text.
    This is a simple approximation (4 chars = ~1 token).
    
    Args:
        text (str): Text to count tokens for
        
    Returns:
        int: Approximate token count
    """
    return len(text) // 4  # Simple approximation


def show_analytics_dashboard():
    """
    Displays the analytics dashboard.
    """
    st.markdown("## 📊 Analytics Dashboard")
    
    # Get analytics summary
    summary = get_analytics_summary()
    
    # Display summary metrics without using st.metric
    st.markdown(f"""
    | Metric | Value |
    |--------|-------|
    | **Total Conversations** | {summary["total_conversations"]} |
    | **Total Tokens Used** | {summary["total_tokens"]:,} |
    | **Avg. Response Time** | {summary["avg_response_time"]} sec |
    """)
    
    # Display model usage
    st.markdown("### 🤖 Model Usage")
    
    if summary["top_models"]:
        # Display visual representation using markdown
        st.markdown("#### Model Usage Visualization")
        
        # Find the maximum count for scaling
        max_count = max([count for _, count in summary["top_models"]])
        
        # Create a visual bar using emoji
        for model, count in summary["top_models"]:
            # Scale to max 20 characters
            bar_length = int((count / max_count) * 20) if max_count > 0 else 0
            bar = "🟦" * bar_length
            
            # Display as markdown
            st.markdown(f"**{model}**: {bar} ({count} conversations)")
        
        st.markdown("---")
    else:
        st.info("No model usage data available yet.")
    
    # Display user activity
    st.markdown("### 👥 User Activity")
    
    if summary["top_users"]:
        # Display visual representation using markdown
        st.markdown("#### User Activity Visualization")
        
        # Find the maximum count for scaling
        max_count = max([count for _, count in summary["top_users"]])
        
        # Create a visual bar using emoji
        for user, count in summary["top_users"]:
            # Scale to max 20 characters
            bar_length = int((count / max_count) * 20) if max_count > 0 else 0
            bar = "🟩" * bar_length
            
            # Display as markdown
            st.markdown(f"**{user}**: {bar} ({count} conversations)")
    else:
        st.info("No user activity data available yet.")


def show_conversation_history(username: str):
    """
    Displays conversation history for a user.
    
    Args:
        username (str): Username
    """
    st.markdown("## 📜 Your Conversation History")
    
    # Get user conversations
    conversations = get_user_conversations(username)
    
    if not conversations:
        st.info("You don't have any conversations yet. Start chatting to build your history!")
        return
    
    # Display conversation count
    st.caption(f"Found {len(conversations)} conversations")
    
    # Export button
    export_col1, export_col2 = st.columns([3, 1])
    
    with export_col2:
        json_data = export_user_history_json(username)
        if json_data:
            st.download_button(
                label="📥 Export All (JSON)",
                data=json_data,
                file_name=f"{username}_conversation_history.json",
                mime="application/json",
                use_container_width=True
            )
    
    # Display conversations
    for i, conv in enumerate(conversations):
        with st.expander(f"**{conv['timestamp']}** - {conv['model']} ({len(conv['prompt'])} chars → {len(conv['response'])} chars)"):
            # Conversation details
            st.markdown("### 🙋 Your Prompt")
            st.text_area("", value=conv["prompt"], height=100, disabled=True, key=f"prompt_{i}")
            
            st.markdown("### 🤖 AI Response")
            st.text_area("", value=conv["response"], height=200, disabled=True, key=f"response_{i}")
            
            # Metadata as simple text
            st.markdown(f"""
            | Metric | Value |
            |--------|-------|
            | **Response Time** | {conv['response_time']:.2f} sec |
            | **Prompt Tokens** | {conv['prompt_tokens']} |
            | **Response Tokens** | {conv['response_tokens']} |
            """)
"""
Streamlit Claude App - Main Application
"""

import streamlit as st
import time
from datetime import datetime
from auth import (
    login_user,
    logout_user,
    is_authenticated,
    get_current_user,
    validate_login_form,
    get_available_users,
    register_user,
    validate_registration_form,
    get_user_count,
)
from api_client import (
    initialize_api_keys,
    get_random_api_key,
    generate_response,
    get_model_for_api_key,
)
from utils import (
    initialize_session_state,
    get_user_log_stats,
    create_pdf_from_conversation,
    get_model_display_name,
)
from analytics import (
    save_conversation,
    get_user_conversations,
    show_analytics_dashboard,
    show_conversation_history,
    count_tokens,
    export_user_history_json,
)
from resume_generator import show_resume_generator
from ai_features import (
    show_model_comparison,
    show_conversation_interface,
)


def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Swayam Sites",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def show_login_page():
    """Display the login page"""
    st.markdown(
        """
    <div style="text-align: center; padding: 2rem 0;">
        <h1>🤖 Swayam Sites</h1>
        <p style="font-size: 1.2rem; color: #666;">
            Welcome! Please log in or register to access the AI-powered prompt generation.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Create centered login/register form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Tab selection for Login/Register
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            # Login form
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username",
                    help="Use one of the demo accounts below or register a new account",
                )

                password = st.text_input(
                    "Password", type="password", placeholder="Enter your password"
                )

                login_button = st.form_submit_button(
                    "🚀 Login", use_container_width=True, type="primary"
                )

                if login_button:
                    # Validate form inputs
                    validation_error = validate_login_form(username, password)

                    if validation_error:
                        st.error(validation_error)
                    else:
                        # Attempt login
                        result = login_user(username, password)

                        if result["success"]:
                            st.success(result["message"])
                            st.rerun()
                        else:
                            st.error(result["message"])

        with tab2:
            # Registration form
            with st.form("register_form", clear_on_submit=True):
                reg_username = st.text_input(
                    "Choose Username",
                    placeholder="Enter a unique username (min 3 characters)",
                    help="Username must be at least 3 characters long",
                )

                reg_password = st.text_input(
                    "Choose Password",
                    type="password",
                    placeholder="Enter a secure password (min 6 characters)",
                    help="Password must be at least 6 characters long",
                )

                reg_email = st.text_input(
                    "Email (Optional)",
                    placeholder="Enter your email address",
                    help="Email is optional but recommended for account recovery",
                )

                register_button = st.form_submit_button(
                    "✨ Create Account", use_container_width=True, type="secondary"
                )

                if register_button:
                    # Attempt registration
                    result = register_user(reg_username, reg_password, reg_email)

                    if result["success"]:
                        st.success(result["message"])
                        st.info(
                            "🔄 Please switch to the Login tab to sign in with your new account."
                        )
                    else:
                        st.error(result["message"])

        # User statistics
        st.markdown("---")
        col_stats1, col_stats2 = st.columns(2)

        with col_stats1:
            total_users = get_user_count()
            st.markdown(f"**👥 Total Users:** {total_users}")

        with col_stats2:
            stats = get_user_log_stats()
            st.markdown(f"**🔄 Total Logins:** {stats['total_logins']}")

        # Demo accounts info
        st.markdown("### 👥 Demo Accounts")

        demo_users = get_available_users()

        cols = st.columns(2)
        for i, (user, pwd) in enumerate(demo_users.items()):
            with cols[i % 2]:
                st.code(f"Username: {user}\nPassword: {pwd}")

        st.info("💡 **Tip:** Use demo accounts above or create your own account!")


def show_main_app():
    """Display the main application interface"""
    # Header with user info and logout
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"""
        <div style="padding: 1rem 0;">
            <h1>🤖 Swayam Sites</h1>
            <p style="color: #666;">Welcome back, <strong>{get_current_user()}</strong>! 
            Generate AI responses using multiple models.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()

    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "💬 Chat",
            "🧠 Conversation",
            "🔄 Compare Models",
            "📜 History",
            "📊 Analytics",
            "📄 Resume",
        ]
    )

    # Chat tab
    with tab1:
        # Prompt input section
        st.markdown("### 💭 Enter Your Prompt")

        prompt = st.text_area(
            "What would you like to ask?",
            placeholder="Type your question or prompt here...\n\nExample: 'Explain quantum computing in simple terms' or 'Write a Python function to sort a list'",
            height=150,
            help="Enter any question or request for the AI",
        )

        # Generate button and response area
        col1, col2, col3 = st.columns([2, 1, 2])

        with col2:
            generate_button = st.button(
                "✨ Generate Response",
                use_container_width=True,
                type="primary",
                disabled=not prompt.strip(),
            )

    # Conversation tab with context memory
    with tab2:
        show_conversation_interface(get_current_user())

    # Model comparison tab
    with tab3:
        show_model_comparison(get_current_user())

    # History tab
    with tab4:
        show_conversation_history(get_current_user())

    # Analytics tab
    with tab5:
        show_analytics_dashboard()

    # Resume Generator tab
    with tab6:
        show_resume_generator()

    # Response section
    if generate_button and prompt.strip():
        with tab1:  # Make sure response appears in Chat tab
            with st.spinner("🤔 AI is thinking..."):
                # Get random API key
                api_keys = st.session_state.get("api_keys", [])
                if not api_keys:
                    st.error("❌ No API keys available. Please check configuration.")
                    return

                selected_key = get_random_api_key(api_keys)

                # Start timing the response
                start_time = time.time()

                try:
                    # Generate response (ensure streaming is False)
                    result = generate_response(prompt, selected_key, streaming=False)

                    # Calculate response time
                    response_time = time.time() - start_time

                    if result["success"]:
                        st.markdown("### 🎯 AI Response")

                        # Display response with black text
                        with st.container():
                            # Fix for Hugging Face Spaces - avoid backslash in f-string
                            content_with_breaks = result["content"].replace(
                                "\n", "<br>"
                            )
                            st.markdown(
                                f"""
                            <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #007bff; color: #000000;">
                                <div style="color: #000000; line-height: 1.6; font-size: 16px;">
                                    {content_with_breaks}
                                </div>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        # Get model info for display
                        model_used = get_model_for_api_key(selected_key)
                        model_display = get_model_display_name(model_used)

                        # Metadata and download section
                        col1, col2, col3 = st.columns([2, 1, 1])

                        with col1:
                            st.caption(f"🤖 Generated using: {model_display}")
                            st.caption(f"🔑 API key ending in: ...{selected_key[-8:]}")

                        with col3:
                            # PDF Download button
                            try:
                                pdf_data = create_pdf_from_conversation(
                                    prompt,
                                    result["content"],
                                    get_current_user(),
                                    model_display,
                                )

                                st.download_button(
                                    label="📄 Download PDF",
                                    data=pdf_data,
                                    file_name=f"ai_conversation_{get_current_user()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True,
                                )
                            except Exception as e:
                                st.error(f"PDF generation error: {str(e)}")

                        # Calculate token counts
                        prompt_tokens = count_tokens(prompt)
                        response_tokens = count_tokens(result["content"])

                        # Store conversation in session state for potential re-download
                        if "conversations" not in st.session_state:
                            st.session_state.conversations = []

                        conversation_data = {
                            "prompt": prompt,
                            "response": result["content"],
                            "model": model_display,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "response_time": response_time,
                            "prompt_tokens": prompt_tokens,
                            "response_tokens": response_tokens,
                        }

                        st.session_state.conversations.append(conversation_data)

                        # Save conversation to history
                        save_conversation(
                            username=get_current_user(),
                            prompt=prompt,
                            response=result["content"],
                            model=model_used,
                            response_time=response_time,
                            prompt_tokens=prompt_tokens,
                            response_tokens=response_tokens,
                        )

                        # Display analytics for this conversation
                        st.markdown("### 📊 Conversation Analytics")

                        # Display metrics as simple markdown text instead of using st.metric
                        st.markdown(f"""
                        | Metric | Value |
                        |--------|-------|
                        | **Response Time** | {response_time:.2f} sec |
                        | **Prompt Tokens** | {prompt_tokens} |
                        | **Response Tokens** | {response_tokens} |
                        | **Total Tokens** | {prompt_tokens + response_tokens} |
                        """)

                    else:
                        error_msg = result["error"]

                        # Handle specific error types
                        if "402" in error_msg or "Payment Required" in error_msg:
                            st.error(
                                "💳 **Payment Required**: The API key has insufficient credits."
                            )
                            st.warning("""
                            **To fix this issue:**
                            1. Go to [OpenRouter](https://openrouter.ai/credits) 
                            2. Add credits to your account
                            3. Or replace the API keys in your .env file with keys that have credits
                            """)
                        elif "401" in error_msg or "Unauthorized" in error_msg:
                            st.error("🔑 **Authentication Error**: Invalid API key.")
                            st.info("Please check your API keys in the .env file.")
                        elif "429" in error_msg or "rate limit" in error_msg.lower():
                            st.error("⏱️ **Rate Limited**: Too many requests.")
                            st.info("Please wait a moment and try again.")
                        else:
                            st.error(f"❌ Error generating response: {error_msg}")

                        # Try with different API key suggestion
                        if len(api_keys) > 1:
                            st.info(
                                "💡 The app will automatically try different API keys on your next request."
                            )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info(
                        "This might be due to an issue with the API or the response format. Try again with a different prompt."
                    )

    # Sidebar with stats (optional)
    with st.sidebar:
        st.markdown("### 📊 Session Info")

        stats = get_user_log_stats()
        st.markdown(f"**Total Logins:** {stats['total_logins']}")
        st.markdown(f"**Unique Users:** {stats['unique_users']}")

        if stats["recent_logins"]:
            st.markdown("### 🕒 Recent Activity")
            for login in stats["recent_logins"][-3:]:
                st.caption(f"👤 {login['username']} - {login['login_timestamp']}")


def main():
    """Main application function"""
    configure_page()
    initialize_session_state()

    # Initialize API keys on startup
    if not st.session_state.get("api_keys"):
        if not initialize_api_keys():
            st.stop()

    # Route to appropriate page based on authentication
    if is_authenticated():
        show_main_app()
    else:
        show_login_page()


if __name__ == "__main__":
    main()

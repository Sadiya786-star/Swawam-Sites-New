"""
Advanced AI Features module for enhanced AI interactions
"""
import streamlit as st
import time
import json
from typing import Dict, Any, List, Optional
from api_client import generate_response, get_model_for_api_key
from analytics import count_tokens, save_conversation


def initialize_conversation_context():
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are a helpful AI assistant."


def add_message_to_context(role: str, content: str):
    if "conversation_history" not in st.session_state:
        initialize_conversation_context()
    st.session_state.conversation_history.append({"role": role, "content": content})


def get_conversation_context() -> List[Dict[str, str]]:
    if "conversation_history" not in st.session_state:
        initialize_conversation_context()
    return st.session_state.conversation_history


def clear_conversation_context():
    st.session_state.conversation_history = []


def set_system_prompt(prompt: str):
    st.session_state.system_prompt = prompt


def get_system_prompt() -> str:
    if "system_prompt" not in st.session_state:
        initialize_conversation_context()
    return st.session_state.system_prompt


def generate_response_with_context(prompt: str, api_key: str, include_context: bool = True, streaming: bool = False) -> Dict[str, Any]:
    add_message_to_context("user", prompt)
    model = get_model_for_api_key(api_key)
    start_time = time.time()

    if streaming:
        return {
            "success": False,
            "content": None,
            "error": "Streaming is not supported in generate_response_with_context",
            "response_time": 0,
            "prompt_tokens": count_tokens(prompt),
            "response_tokens": 0,
            "model": model
        }

    if include_context:
        context = get_conversation_context()
        system_prompt = get_system_prompt()
        result = generate_response(
            prompt=prompt,
            api_key=api_key,
            conversation_history=context[:-1],
            system_prompt=system_prompt,
            streaming=False
        )
    else:
        result = generate_response(
            prompt=prompt,
            api_key=api_key,
            streaming=False
        )

    response_time = time.time() - start_time

    if result["success"] and result["content"]:
        add_message_to_context("assistant", result["content"])

    result["response_time"] = response_time
    result["prompt_tokens"] = count_tokens(prompt)
    result["response_tokens"] = count_tokens(result.get("content", ""))
    result["model"] = model

    return result


def compare_models(prompt: str, api_keys: List[str]) -> List[Dict[str, Any]]:
    results = []
    for api_key in api_keys:
        try:
            model = get_model_for_api_key(api_key)
            start_time = time.time()
            result = generate_response(prompt=prompt, api_key=api_key, streaming=False)
            response_time = time.time() - start_time
            if result["success"]:
                result.update({
                    "response_time": response_time,
                    "prompt_tokens": count_tokens(prompt),
                    "response_tokens": count_tokens(result.get("content", "")),
                    "model": model
                })
            else:
                result.update({
                    "response_time": 0,
                    "prompt_tokens": count_tokens(prompt),
                    "response_tokens": 0,
                    "model": model
                })
            results.append(result)
        except Exception as e:
            results.append({
                "success": False,
                "content": None,
                "error": f"Error: {str(e)}",
                "response_time": 0,
                "prompt_tokens": count_tokens(prompt),
                "response_tokens": 0,
                "model": get_model_for_api_key(api_key)
            })
    return results


def show_model_comparison(username: str):
    st.markdown("## 🧠 Model Comparison")
    st.markdown("Compare responses from different AI models for the same prompt.")
    prompt = st.text_area("Enter your prompt", placeholder="Type your question or prompt here to compare responses from different models...", height=150)
    api_keys = st.session_state.get('api_keys', [])

    if not api_keys:
        st.error("❌ No API keys available. Please check configuration.")
        return

    st.markdown("### Select Models to Compare")
    selected_models = {}
    cols = st.columns(len(api_keys))
    for i, api_key in enumerate(api_keys):
        model = get_model_for_api_key(api_key)
        model_name = model.split('/')[-1] if '/' in model else model
        with cols[i]:
            selected = st.checkbox(f"{model_name}", value=True, key=f"model_select_{i}")
            selected_models[api_key] = selected

    compare_button = st.button("🔄 Compare Models", use_container_width=True, type="primary", disabled=not prompt.strip() or not any(selected_models.values()))

    if compare_button and prompt.strip():
        selected_keys = [key for key, selected in selected_models.items() if selected]
        if not selected_keys:
            st.warning("Please select at least one model to compare.")
            return
        with st.spinner("Generating responses from multiple models..."):
            results = compare_models(prompt, selected_keys)
        st.markdown("### 📊 Comparison Results")
        tabs = st.tabs([f"Model {i+1}" for i in range(len(results))])

        for i, (result, tab) in enumerate(zip(results, tabs)):
            with tab:
                model = result["model"]
                model_display = model.split('/')[-1] if '/' in model else model
                st.markdown(f"#### {model_display}")
                if result["success"]:
                    st.markdown("**Response:**")
                    content_with_breaks = result["content"].replace('\n', '<br>')
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #007bff; color: #000000;">
                        <div style="color: #000000; line-height: 1.6; font-size: 16px;">
                            {content_with_breaks}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"""
                    **Response Time:** {result['response_time']:.2f} sec | 
                    **Prompt Tokens:** {result["prompt_tokens"]} | 
                    **Response Tokens:** {result["response_tokens"]}
                    """)
                    save_conversation(username, prompt, result["content"], model, result["response_time"], result["prompt_tokens"], result["response_tokens"])
                else:
                    st.error(f"Error: {result['error']}")

        st.markdown("### 📊 Metrics Comparison")
        st.markdown("| Model | Response Time | Response Tokens | Total Tokens |")
        st.markdown("|-------|--------------|----------------|--------------|")
        for result in results:
            if result["success"]:
                model = result["model"]
                model_display = model.split('/')[-1] if '/' in model else model
                response_time = f"{result['response_time']:.2f} sec"
                response_tokens = result["response_tokens"]
                total_tokens = result["prompt_tokens"] + result["response_tokens"]
                st.markdown(f"| {model_display} | {response_time} | {response_tokens} | {total_tokens} |")


def show_conversation_interface(username: str):
    st.markdown("## 💬 Conversation with Context")
    st.markdown("Have a multi-turn conversation with memory of previous exchanges.")
    initialize_conversation_context()
    with st.expander("⚙️ Configure System Prompt"):
        system_prompt = st.text_area("System Prompt (sets AI behavior)", value=get_system_prompt(), height=100, help="This prompt tells the AI how to behave.")
        if st.button("Update System Prompt", use_container_width=True):
            set_system_prompt(system_prompt)
            st.success("System prompt updated!")
        if st.button("Reset Conversation", use_container_width=True):
            clear_conversation_context()
            st.success("Conversation history cleared!")

    st.markdown("### Conversation History")
    conversation = get_conversation_context()
    if not conversation:
        st.info("No conversation history yet. Start chatting below!")
    else:
        for message in conversation:
            content_html = message["content"].replace('\n', '<br>')
            if message["role"] == "user":
                st.markdown(f"""
                <div style="background-color: #e9f7fe; padding: 1rem; border-radius: 10px; margin-bottom: 10px;">
                    <strong>You:</strong><br>
                    {content_html}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 10px; border-left: 4px solid #007bff; margin-bottom: 10px; color: #000000;">
                    <strong>AI:</strong><br>
                    <div style="color: #000000; line-height: 1.6;">
                        {content_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("### Your Message")
    prompt = st.text_area("Enter your message", placeholder="Type your message here...", height=100)
    col1, col2 = st.columns(2)
    with col1:
        use_context = st.checkbox("Use conversation history", value=True)
    with col2:
        use_streaming = st.checkbox("Stream response", value=False)
    send_button = st.button("📤 Send Message", use_container_width=True, type="primary", disabled=not prompt.strip())
    api_keys = st.session_state.get('api_keys', [])

    if not api_keys:
        st.error("❌ No API keys available. Please check configuration.")
        return

    if send_button and prompt.strip():
        from api_client import get_random_api_key
        selected_key = get_random_api_key(api_keys)
        with st.spinner("Generating response..."):
            result = generate_response_with_context(prompt=prompt, api_key=selected_key, include_context=use_context, streaming=False)
        if result["success"]:
            content_html = result["content"].replace('\n', '<br>')
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 10px; border-left: 4px solid #007bff; color: #000000;">
                <strong>AI:</strong><br>
                <div style="color: #000000; line-height: 1.6;">
                    {content_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("### 📊 Response Metrics")
            model_display = result["model"].split('/')[-1] if '/' in result["model"] else result["model"]
            response_time = f"{result['response_time']:.2f} sec"
            prompt_tokens = result["prompt_tokens"]
            response_tokens = result["response_tokens"]
            st.markdown(f"""
            - **Model:** {model_display}
            - **Response Time:** {response_time}
            - **Prompt Tokens:** {prompt_tokens}
            - **Response Tokens:** {response_tokens}
            - **Total Tokens:** {prompt_tokens + response_tokens}
            """)
            save_conversation(username, prompt, result["content"], result["model"], result["response_time"], result["prompt_tokens"], result["response_tokens"])
        else:
            st.error(f"Error: {result['error']}")
        st.rerun()

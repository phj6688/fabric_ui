import streamlit as st
from streamlit_option_menu import option_menu
import shlex
import requests
import db_handler
import time

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None

def handle_login(username, password):
    user = db_handler.get_user(username)
    if user and user.verify_password(password):
        st.session_state.authenticated = True
        st.session_state.username = username
        db_handler.log_action(username, "User logged in")
        st.success("Login successful!")
        st.rerun()
    else:
        st.error("Invalid credentials")

def handle_logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()


def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None

def switch_to_login():
    st.session_state.show_login = True
    st.rerun()

def show_auth_page():
    st.title("Fabric UI - Authentication")
    
    st.header("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Login", use_container_width=True):
            handle_login(username, password)


def show_main_app():
    st.title("Fabric UI")
    
    # Add logout button in the top right
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Logout"):
            handle_logout()
    with col1:
        st.write(f"Welcome, {st.session_state.username}!")

    # Dictionary containing explanations for each pattern
    pattern_explanations = {
        "summarize": "Generates a concise overview of the content.",
        "summarize_micro": "Produces an ultra-short summary highlighting only the essentials.",
        "extract_wisdom": "Pulls out key insights, quotes, and actionable takeaways.",
        "extract_main_idea": "Isolates the central theme or message of the content.",
        "extract_instructions": "Identifies and lists actionable steps or guidelines mentioned.",
        "improve_prompt": "Refines a prompt to enhance clarity and effectiveness.",
        "improve_writing": "Edits the text for better style, coherence, and readability.",
        "other": "Allows you to define a custom query or task."
    }

    # Language selection
    lang_selected = option_menu(
        menu_title="Select a language",
        options=["English", "Deutsch"],
        icons=["flag-usa", "flag-de"],
        default_index=0,
        orientation="horizontal"
    )
    language = "en" if lang_selected == "English" else "de"

    # Function selection menu
    func_selected = option_menu(
        menu_title="Select a function",
        options=["YouTube", "Text"],
        icons=["youtube", "file-text"],
        default_index=0,
        orientation="horizontal"
    )

    if func_selected == "YouTube":
        pattern = st.selectbox(
            "Select a pattern for YouTube",
            options=["summarize", "summarize_micro", "extract_wisdom", "extract_main_idea", "extract_instructions", "other"],
            format_func=lambda x: f"{x} - {pattern_explanations.get(x, '')}"
        )
        url = st.text_input("Enter the URL:")
        quoted_url = shlex.quote(url)
        if pattern == "other":
            custom_query = st.text_input("Enter your question:")
            cmd = f"fabric -y {quoted_url} {custom_query} -g {language}"
        else:
            cmd = f"fabric -y {quoted_url} -p {pattern} -g {language}"
    else:
        pattern = st.selectbox(
            "Select a pattern for Text",
            options=["summarize", "summarize_micro", "extract_wisdom", "extract_main_idea", "improve_prompt", "improve_writing", "extract_instructions", "other"],
            format_func=lambda x: f"{x} - {pattern_explanations.get(x, '')}"
        )
        text = st.text_area("Enter text here", height=200)
        quoted_text = shlex.quote(text)
        if pattern == "other":
            custom_query = st.text_input("Enter your question:")
            cmd = f'echo {quoted_text} | fabric -p "{custom_query} -g {language}"'
        else:
            cmd = f'echo {quoted_text} | fabric -p {pattern} -g {language}'

    if st.button("Submit"):
        try:
            response = requests.post("http://127.0.0.1:7070/execute/", json={"command": cmd})
            if response.status_code == 200:
                result = response.json()
                st.markdown("**_Output:_**")
                st.markdown(result.get("stdout", ""))
                if result.get("stderr"):
                    st.subheader("Errors:")
                    st.text(result.get("stderr"))
            else:
                st.error(f"Error: Received status code {response.status_code}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def main():
    st.set_page_config(
        page_title="Fabric UI",
        page_icon=":thread:",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    init_session_state()
    
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
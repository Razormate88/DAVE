import streamlit as st
import json
import requests
import time
import os
from openai import AzureOpenAI

# Azure OpenAI Configuration
endpoint = os.getenv("ENDPOINT_URL", "https://dcai-datamyte-01.openai.azure.com/")
model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
deployment = os.getenv("DEPLOYMENT_NAME", "datamyte-kb")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "Ef2xSd5l55RSviazg3sEsnRSBGQ2S3BxhUadt7tCw1IIip3VVBd1JQQJ99BCACHYHv6XJ3w3AAABACOGHCb3")
api = "2024-05-01-preview"

# Initialize Azure OpenAI Client
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version=api
)

# UI Configuration
st.set_page_config(page_title="D.A.V.E.")

# Display Logo (Centered)
#IMAGE_PATH =   # Replace with actual image path
# left_co, cent_co,last_co = st.columns(3)
# with cent_co:
    # st.image(IMAGE_PATH)

# Title with Centered Styling
st.markdown("""<h1 style="text-align: center; font-size: 50px; font-weight: bold;">D.A.V.E.</h1>""", unsafe_allow_html=True)
st.markdown("""<h2 style="text-align: center; font-size: 30px; font-weight: bold;">Datamyte AI Virtual Expert</h2>""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hello! How can I assist you today?"})

# Scrollable Chat History Box
chat_history = st.container()
with chat_history:
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "🧑‍💻"):
            st.markdown(message["content"])

# User Input
user_input = st.chat_input("Ask Me Anything")

if user_input:
    # Add user message to session state and refresh UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with chat_history:
        last_message = st.session_state.messages[-1]
        with st.chat_message(last_message["role"], avatar="🧑‍💻" if last_message["role"] == "user" else "🤖"):
            st.markdown(last_message["content"])
            
    # Create a new thread
    thread = client.beta.threads.create()

    # Add user input to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # Run the assistant's response
    try:
        with st.spinner("Thinking...", show_time=True):
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id="asst_RMz3XgPKqH3Bgno8RkSppKZd"
            )

            while run.status in ['queued', 'in_progress', 'cancelling']:
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

            if run.status == 'failed':
                st.error(f"🚨 Run failed! Check your assistant settings.")
                st.error(f"Error Details: {run}")
            elif run.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                for msg in messages.data:
                    if msg.role == "assistant":
                        response_text = msg.content[0].text.value
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        st.rerun()
                        break
            elif run.status == 'requires_action':
                st.warning("The assistant requires an action before responding.")
            else:
                st.error(f"Unexpected run status: {run.status}")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
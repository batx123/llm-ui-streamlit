import streamlit as st
import requests

st.title("Local LLM Chat UI")

# Replace with your local LLM endpoint
default_llm_url = "http://localhost:8001/v1/chat/completions"
llm_url = st.text_input("LLM API Endpoint", value=default_llm_url)

user_input = st.text_area("Your message:")

if st.button("Send"):
    if user_input.strip():
        with st.spinner("Waiting for LLM response..."):
            try:
                # Example for OpenAI-compatible API (adjust as needed)
                payload = {
                    "model": "deepseek-ai/deepseek-r1-distill-llama-8b",
                    "messages": [
                        {"role": "user", "content": user_input}
                    ]
                }
                response = requests.post(llm_url, json=payload)
                try:
                    data = response.json()
                except Exception:
                    st.error(f"Non-JSON response: {response.text}")
                    raise
                if response.status_code != 200:
                    st.error(f"API Error {response.status_code}: {data}")
                else:
                    # Adjust this extraction based on your LLM's response format
                    try:
                        llm_reply = data["choices"][0]["message"]["content"]
                        st.markdown(f"**LLM:** {llm_reply}")
                    except Exception as e:
                        st.error(f"Unexpected response format: {data}\nError: {e}")
            except Exception as e:
                st.error(f"Request failed: {e}")
    else:
        st.warning("Please enter a message.")

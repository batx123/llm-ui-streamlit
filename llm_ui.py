import streamlit as st
import requests

st.title("Deepseek-R1-Distill-Llama-8B")

# Replace with your local LLM endpoint
default_llm_url = "http://localhost:8001/v1/chat/completions"
llm_url = st.text_input("LLM API Endpoint", value=default_llm_url)

user_input = st.text_area("Your message:")

# Temperature slider (0.5-0.7, default 0.6)
temperature = st.slider("Temperature (controls randomness)", min_value=0.5, max_value=0.7, value=0.6, step=0.01)

# Max tokens input (default 64)
max_tokens = st.number_input("Max tokens", min_value=1, max_value=4096, value=64, step=1)

if st.button("Send"):
    if user_input.strip():
        with st.spinner("Waiting for LLM response..."):
            try:
                # Example for OpenAI-compatible API (adjust as needed)
                payload = {
                    "model": "deepseek-ai/deepseek-r1-distill-llama-8b",
                    "messages": [
                        {"role": "user", "content": user_input}
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens
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

import streamlit as st
import requests
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import tempfile

import time

st.title("Deepseek-R1-Distill-Llama-8B")

# --- RAG: File Upload and Ingestion ---
st.sidebar.header("RAG: Document Ingestion")
rag_file = st.sidebar.file_uploader("Upload a text file for RAG", type=["txt"])
rag_folder = st.sidebar.text_input("Or enter a folder path for .txt files")

rag_docs = []
if rag_file is not None:
    rag_docs.append((rag_file.name, rag_file.read().decode("utf-8")))
elif rag_folder:
    for fname in os.listdir(rag_folder):
        if fname.endswith(".txt"):
            with open(os.path.join(rag_folder, fname), "r", encoding="utf-8") as f:
                rag_docs.append((fname, f.read()))

rag_context = ""
if rag_docs:
    # Split and embed docs
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    all_chunks = []
    for fname, text in rag_docs:
        for chunk in splitter.split_text(text):
            all_chunks.append({"text": chunk, "source": fname})
    # Use a temp dir for Chroma
    with tempfile.TemporaryDirectory() as persist_dir:
        vectordb = Chroma.from_texts([c["text"] for c in all_chunks], HuggingFaceEmbeddings(), persist_directory=persist_dir)
        # On each query, search for relevant chunks
        def get_rag_context(query, k=2):
            docs = vectordb.similarity_search(query, k=k)
            return "\n".join([d.page_content for d in docs])
        st.sidebar.success(f"Indexed {len(all_chunks)} chunks from {len(rag_docs)} file(s)")
else:
    def get_rag_context(query, k=2):
        return ""

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
                # RAG: retrieve context if docs are loaded
                rag_context_str = get_rag_context(user_input, k=2)
                messages = []
                if rag_context_str:
                    messages.append({"role": "system", "content": f"Use the following context to answer: {rag_context_str}"})
                messages.append({"role": "user", "content": user_input})
                payload = {
                    "model": "deepseek-ai/deepseek-r1-distill-llama-8b",
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                start_time = time.time()
                response = requests.post(llm_url, json=payload)
                latency = time.time() - start_time
                try:
                    data = response.json()
                except Exception:
                    st.error(f"Non-JSON response: {response.text}")
                    raise
                if response.status_code != 200:
                    st.error(f"API Error {response.status_code}: {data}")
                else:
                    try:
                        llm_reply = data["choices"][0]["message"]["content"]
                        token_count = len(llm_reply.split())
                        tokens_per_sec = token_count / latency if latency > 0 else 0
                        st.markdown(f"**LLM:** {llm_reply}")
                        st.info(f"Latency: {latency:.2f} seconds | Tokens (approx): {token_count} | Tokens/sec (approx): {tokens_per_sec:.2f}")
                        if rag_context_str:
                            with st.expander("RAG Context Used", expanded=False):
                                st.write(rag_context_str)
                    except Exception as e:
                        st.error(f"Unexpected response format: {data}\nError: {e}")
            except Exception as e:
                st.error(f"Request failed: {e}")
    else:
        st.warning("Please enter a message.")

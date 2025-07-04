import streamlit as st
import requests
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import tempfile

import pdfplumber

import time

st.title("Deepseek-R1-Distill-Llama-8B")


# --- RAG: File Upload and Ingestion ---

st.sidebar.header("RAG: Document Ingestion")
rfile_types = ["txt", "pdf"]
rag_file = st.sidebar.file_uploader("Upload a text or PDF file for RAG", type=rfile_types)
rag_folder = st.sidebar.text_input("Or enter a folder path for .txt/.pdf files")

# Max context length slider (default 4000, up to 65000 for Deepseek)
max_context_length = st.sidebar.number_input(
    "Max context length (characters)", min_value=1000, max_value=65000, value=4000, step=500,
    help="Controls how much context is sent to the LLM. The model's max is 16,384 tokens (~65,000 chars)."
)
st.sidebar.info("Model max context: 16,384 tokens (~65,000 chars). This UI limits by characters for safety.")

rag_docs = []
def extract_text_from_pdf(file_bytes):
    with pdfplumber.open(file_bytes) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

if rag_file is not None:
    if rag_file.name.lower().endswith(".pdf"):
        text = extract_text_from_pdf(rag_file)
        rag_docs.append((rag_file.name, text))
    else:
        rag_docs.append((rag_file.name, rag_file.read().decode("utf-8")))
elif rag_folder:
    for fname in os.listdir(rag_folder):
        fpath = os.path.join(rag_folder, fname)
        if fname.lower().endswith(".txt"):
            with open(fpath, "r", encoding="utf-8") as f:
                rag_docs.append((fname, f.read()))
        elif fname.lower().endswith(".pdf"):
            with open(fpath, "rb") as f:
                text = extract_text_from_pdf(f)
                rag_docs.append((fname, text))

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
        def get_rag_context(query, k=2, max_context_chars=4000):
            docs = vectordb.similarity_search(query, k=k)
            context = "\n".join([d.page_content for d in docs])
            # Truncate context to avoid exceeding model limits
            if len(context) > max_context_chars:
                context = context[:max_context_chars] + "\n...[truncated]"
            return context
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
                rag_context_str = get_rag_context(user_input, k=2, max_context_chars=max_context_length)
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

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
        # Return a list of (page_num, text) tuples
        return [(i+1, page.extract_text() or "") for i, page in enumerate(pdf.pages)]

if rag_file is not None:
    if rag_file.name.lower().endswith(".pdf"):
        page_texts = extract_text_from_pdf(rag_file)
        for page_num, text in page_texts:
            rag_docs.append((rag_file.name, text, page_num))
    else:
        rag_docs.append((rag_file.name, rag_file.read().decode("utf-8"), None))
elif rag_folder:
    for fname in os.listdir(rag_folder):
        fpath = os.path.join(rag_folder, fname)
        if fname.lower().endswith(".txt"):
            with open(fpath, "r", encoding="utf-8") as f:
                rag_docs.append((fname, f.read(), None))
        elif fname.lower().endswith(".pdf"):
            with open(fpath, "rb") as f:
                page_texts = extract_text_from_pdf(f)
                for page_num, text in page_texts:
                    rag_docs.append((fname, text, page_num))

rag_context = ""
if rag_docs:
    # Split and embed docs
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    all_chunks = []
    for fname, text, page_num in rag_docs:
        for chunk in splitter.split_text(text):
            all_chunks.append({"text": chunk, "source": fname, "page": page_num})
    # User choice: run embeddings on CPU (safe, default) or GPU (faster, may OOM)
    use_gpu = st.sidebar.checkbox("Use GPU for embeddings (advanced, may cause CUDA OOM)", value=False, help="If unchecked, embeddings run on CPU (recommended if your LLM is using the GPU). If checked, embeddings run on GPU, which is faster but may cause out-of-memory errors if your GPU is full.")
    device = "cuda" if use_gpu else "cpu"
    embedding_model = HuggingFaceEmbeddings(encode_kwargs={"batch_size": 4}, model_kwargs={"device": device})
    # User control for number of RAG references
    num_refs = st.sidebar.number_input("Number of RAG references to show", min_value=1, max_value=10, value=3, step=1, help="How many source document references to display with each answer.")
    with tempfile.TemporaryDirectory() as persist_dir:
        vectordb = Chroma.from_texts(
            [c["text"] for c in all_chunks],
            embedding_model,
            persist_directory=persist_dir,
            metadatas=[{"source": c["source"], "text": c["text"], "page": c["page"]} for c in all_chunks]
        )
        # On each query, search for relevant chunks
        def get_rag_context(query, k=None, max_context_chars=4000):
            k = num_refs if k is None else k
            docs = vectordb.similarity_search(query, k=k)
            context = "\n".join([d.page_content for d in docs])
            # Truncate context to avoid exceeding model limits
            if len(context) > max_context_chars:
                context = context[:max_context_chars] + "\n...[truncated]"
            # Collect references: document name and page number if possible
            references = []
            for d in docs:
                meta = getattr(d, 'metadata', {})
                source = meta.get('source', 'Unknown')
                page = meta.get('page', None)
                # If the source is a file path, try to build a clickable file:// link
                file_link = None
                if os.path.exists(source):
                    file_link = f"file://{os.path.abspath(source)}"
                ref_label = source
                if page:
                    ref_label += f", page {page}"
                references.append({"label": ref_label, "file_link": file_link, "page": page, "source": source})
            return context, references
        st.sidebar.success(f"Indexed {len(all_chunks)} chunks from {len(rag_docs)} file(s)")
else:
    def get_rag_context(query, k=2, max_context_chars=4000):
        return "", []

# Replace with your local LLM endpoint
default_llm_url = "http://localhost:8001/v1/chat/completions"
llm_url = st.text_input("LLM API Endpoint", value=default_llm_url)


# Option to enable/disable RAG for each question
use_rag = st.checkbox("Use RAG (document retrieval) for this question", value=True, help="If unchecked, your question will be sent to the LLM without any document context.")
user_input = st.text_area("Your message:")

# Temperature slider (0.5-0.7, default 0.6)
temperature = st.slider("Temperature (controls randomness)", min_value=0.5, max_value=0.7, value=0.6, step=0.01)

# Max tokens input (default 512)
max_tokens = st.number_input("Max tokens", min_value=1, max_value=4096, value=512, step=1)

if st.button("Send"):
    if user_input.strip():
        with st.spinner("Waiting for LLM response..."):
            try:
                # RAG: retrieve context and references if enabled and docs are loaded
                rag_context_str, rag_references = ("", [])
                if use_rag:
                    rag_context_str, rag_references = get_rag_context(user_input, k=None, max_context_chars=max_context_length)
                messages = []
                if use_rag and rag_context_str:
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
                        if use_rag and rag_context_str:
                            with st.expander("RAG Context Used", expanded=False):
                                st.write(rag_context_str)
                        if use_rag and rag_references:
                            with st.expander("RAG Source References", expanded=False):
                                for ref in rag_references:
                                    # If file_link is available, make the source clickable
                                    if ref.get("file_link"):
                                        st.markdown(f"- [{ref['label']}]({ref['file_link']})")
                                    else:
                                        st.write(f"- {ref['label']}")
                    except Exception as e:
                        st.error(f"Unexpected response format: {data}\nError: {e}")
            except Exception as e:
                st.error(f"Request failed: {e}")
    else:
        st.warning("Please enter a message.")

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Local LLM Streamlit UI

A simple Streamlit-based web UI for chatting with a local Large Language Model (LLM) server.

## Features
- Enter your message and get responses from a local LLM
- Configurable LLM API endpoint (default: OpenAI-compatible)
- Model name set to `deepseek-ai/deepseek-r1-distill-llama-8b` (can be changed in code)
- Error handling and response format debugging

## Requirements
- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [requests](https://docs.python-requests.org/)
- A local LLM server with an OpenAI-compatible API (e.g., LM Studio, OpenRouter, etc.)

## Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/batx123/llm-ui-streamlit.git
   cd llm-ui-streamlit
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install streamlit requests
   ```
4. Start your local LLM server (ensure the endpoint and model name match your setup).
5. Run the Streamlit app:
   ```bash
   streamlit run llm_ui.py
   ```
6. Open your browser to [http://localhost:8501](http://localhost:8501)

## Configuration
- Change the API endpoint in the UI or edit the `default_llm_url` in `llm_ui.py`.
- Change the model name in the payload as needed.

## Example LLM API Compatibility
- OpenAI-compatible endpoints: `/v1/chat/completions`
- LM Studio, OpenRouter, Ollama, etc. (adjust endpoint and payload as needed)

## License
MIT

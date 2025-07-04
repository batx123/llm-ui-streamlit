# Deepseek-R1-Distill-Llama-8B Streamlit UI

A simple Streamlit-based web UI for chatting with the Deepseek-R1-Distill-Llama-8B model (or any local LLM server with an OpenAI-compatible API).

**Model Card:** [Deepseek-R1-Distill-Llama-8B on build.nvidia.com](https://build.nvidia.com/deepseek-ai/deepseek-r1-distill-llama-8b/deploy)

> **Note:** This model is running in a local Docker container.

![Streamlit LLM UI Screenshot](screenshot.png)

## Features
- Enter your message and get responses from a local LLM
- Configurable LLM API endpoint (default: OpenAI-compatible)
- Model name set to `deepseek-ai/deepseek-r1-distill-llama-8b` (can be changed in code)
- Set temperature (0.5–0.7, default 0.6) in the UI
- Set max tokens (default 64) in the UI
- Error handling and response format debugging
- **RAG (Retrieval-Augmented Generation):** Upload or point to a folder of `.txt` files and chat with your documents! Relevant context is retrieved and sent to the LLM for more informed answers.

## Requirements
- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [requests](https://docs.python-requests.org/)
- [pyautogui](https://pyautogui.readthedocs.io/en/latest/) (for screenshots)
- gnome-screenshot (Linux utility for screenshots)
- [langchain](https://python.langchain.com/), [langchain-community](https://github.com/langchain-ai/langchain), [chromadb](https://www.trychroma.com/), [sentence-transformers](https://www.sbert.net/)
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
   pip install streamlit requests pyautogui langchain langchain-community chromadb sentence-transformers
   sudo apt-get install gnome-screenshot
   ```
4. Start your local LLM server (ensure the endpoint and model name match your setup).
5. Run the Streamlit app:
   ```bash
   streamlit run llm_ui.py
   ```
6. Open your browser to [http://localhost:8501](http://localhost:8501)

## Screenshot
To take a screenshot of the UI, run:
```bash
python take_screenshot.py
```
This will save a screenshot as `screenshot.png` in the project directory.

## Configuration
- Change the API endpoint in the UI or edit the `default_llm_url` in `llm_ui.py`.
- Change the model name, temperature, and max tokens in the UI or code as needed.
- Use the sidebar to upload or point to a folder of `.txt` files for RAG.

## Example LLM API Compatibility
- OpenAI-compatible endpoints: `/v1/chat/completions`
- LM Studio, OpenRouter, Ollama, etc. (adjust endpoint and payload as needed)

## Documentation
- See [FAQ.md](FAQ.md) for common questions.
- See [SCREENSHOT.md](SCREENSHOT.md) for a screenshot reference.

## License
MIT

## FAQ

### Q: What is this project?
A: This is a simple Streamlit-based web UI for chatting with a local LLM (Large Language Model) server using an OpenAI-compatible API.

### Q: What LLMs are supported?
A: Any LLM server that exposes an OpenAI-compatible `/v1/chat/completions` endpoint, such as LM Studio, OpenRouter, or similar. You can adjust the endpoint and payload for other APIs.

### Q: How do I change the model?
A: Edit the `model` field in the payload inside `llm_ui.py`.

### Q: How do I change the API endpoint?
A: Use the input box at the top of the UI, or change the `default_llm_url` variable in `llm_ui.py`.

### Q: How do I install dependencies?
A: Run `pip install streamlit requests pyautogui langchain langchain-community chromadb sentence-transformers` in your project directory (preferably in a virtual environment). On Linux, also run `sudo apt-get install gnome-screenshot`.

### Q: How do I run the app?
A: Start your LLM server, then run `streamlit run llm_ui.py` and open [http://localhost:8501](http://localhost:8501) in your browser.

### Q: I get an error or no response from the LLM.
A: Check that your LLM server is running, the endpoint is correct, and the model name matches one available on your server. The UI will show error details to help debug.

### Q: Can I use this with cloud LLMs?
A: Yes, if they provide an OpenAI-compatible API. Update the endpoint and authentication as needed.

### Q: How do I contribute?
A: Fork the repo, make your changes, and submit a pull request!

### Q: What is RAG (Retrieval-Augmented Generation) in this app?
A: You can upload `.txt` files or point to a folder of `.txt` files in the sidebar. The app will index and embed the text, and when you chat, it will retrieve relevant document chunks and send them as context to the LLM for more informed answers.

### Q: What file types are supported for RAG?
A: Currently, only plain text (`.txt`) files are supported for ingestion.

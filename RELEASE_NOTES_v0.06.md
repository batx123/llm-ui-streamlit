# Release Notes v0.06

## Features & Improvements
- Added sidebar option to choose CPU (default, safe) or GPU (advanced, may OOM) for document embedding during RAG.
- Updated FAQ with troubleshooting and usage info for CUDA out-of-memory errors and embedding device selection.
- Embedding batch size remains low (4) for stability.

## Bug Fixes
- Prevents CUDA OOM by default by running embeddings on CPU unless user opts in for GPU.

## Versioning
- Tagged as v0.06

---
See README.md and FAQ.md for full details.

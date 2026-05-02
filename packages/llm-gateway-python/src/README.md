# Source

Source files for the Python SDK live in `llm_gateway/`.

Boundary rules:

- keep this package generic
- do not import app-owned or command-line modules from the repository root
- keep runtime HTTP behavior in the `llm_gateway` package
- keep LangChain Core imports isolated to `llm_gateway.langchain_adapter`

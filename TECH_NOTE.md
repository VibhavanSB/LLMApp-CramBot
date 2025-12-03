# 📝 Tech Note: OmniStudy Architecture & Evaluation

### 1. System Architecture
OmniStudy follows a **RAG (Retrieval Augmented Generation)** pattern combined with **Tool Use** (YouTube Search). It allows users to dynamically swap the knowledge base via the `/learn` endpoint.

```ascii
[ User Browser ]
      |
      | (JSON/HTTP)
      v
[ Flask Server (app.py) ]
      |
      +---< Route: /learn >-----------------------------+
      |   | 1. Clears existing DB                       |
      |   | 2. Chunks text (Paragraph split)            |
      |   | 3. Embeds via SentenceTransformer           |
      |   v                                             |
      | [ ChromaDB (Vector Store) ] <-------------------+
      |
      +---< Route: /generate >--------------------------+
          |                                             |
          +--(Mode: Video)---> [ YouTube Search Lib ]   |
          |                             |               |
          +--(Mode: Notes/Quiz)         v               |
                  |                [ Video ID ]         |
                  v                                     |
           [ Retrieve Context ]                         |
           (Query ChromaDB for Top-2 Chunks)            |
                  |                                     |
                  v                                     |
            [ Gemini API ] (1.5 Flash)                  |
            (Prompt + Context + strict JSON rules)      |
                  |                                     |
                  v                                     |
           [ Response ] (Markdown or JSON)              |
```

### 2. Guardrails & Safety
To ensure robustness and prevent abuse, the following layers of protection are implemented:

*   **Input Sanitization:**
    *   **Ingestion:** Text must be between 50 and 50,000 characters to prevent empty DBs or memory overflows.
    *   **Queries:** User prompts > 300 characters are rejected to prevent token exhaustion.
*   **Prompt Injection Defense:** A "Blacklist" checks for adversarial patterns (e.g., *"ignore previous instructions"*, *"system prompt"*). If detected, the request is blocked immediately with a 400 error.
*   **Output Validation:**
    *   **JSON Enforcement:** In "Quiz Mode", the app wraps the LLM call in a `try/catch` block. If the model returns invalid JSON (hallucinated formatting), the app catches the `JSONDecodeError` gracefully instead of crashing the UI.
*   **Privacy:** YouTube embeds use `youtube-nocookie.com` to restrict tracking cookies within the iframe.

### 3. Evaluation Strategy
We utilize an **Offline Evaluation Script** (`tests/evaluate.py`) running against a static test set (`tests/tests.json`).

*   **Dataset:** 15+ inputs covering standard queries, edge cases, and adversarial attacks.
*   **Metrics:**
    1.  **Recall (Keyword):** For "Notes", response must contain specific high-importance terms derived from the source text.
    2.  **Structure (Schema):** For "Quiz", response must be valid JSON and contain keys: `question`, `options`, `answer`.
    3.  **Refusal (Safety):** Adversarial inputs must trigger an HTTP 400 or specific error message.
*   **Target:** Pass rate > 80% on the seed dataset.

### 4. Known Limitations
1.  **Single-Tenant State:** The vector database (`/data/vector_db`) is global. If User A uploads History notes, User B will see History results. This is acceptable for a local demo but not for production.
2.  **Context Window:** RAG retrieves only the **top 2** chunks. If a query requires synthesizing information from the beginning and end of a long document, the model may miss context.
3.  **Concurrency:** SQLite (underlying Chroma) and the Flask dev server are not thread-safe for high concurrent loads.
4.  **Data Persistence:** The database persists on disk, but the `/learn` function performs a destructive overwrite (wipes previous data) to keep the context clean for the current study session.
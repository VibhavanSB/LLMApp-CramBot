#  CramBot - AI Study Companion

CramBot is a RAG-powered (Retrieval Augmented Generation) study application. It digests course materials and helps students study in three modes:
1.  **📝 Note Taker:** Generates concise bullet-point summaries of specific topics.
2.  **❓ Quiz Generator:** Creates interactive multiple-choice questions to test knowledge.
3.  **🎥 Video Finder:** Retrieves a YouTube video related to the topic for more information.


Built with **Flask**, **ChromaDB**, and **Google Gemini 1.5 Flash**.

---

## 🚀 Features
*   **RAG Architecture:** Retrievals are grounded in the material provided by the user reducing hallucinations.
*   **Dual Modes:** Switches prompts dynamically between text summarization and structured JSON generation for quizzes.
*   **Interactive UI:** Clean interface with immediate feedback on quiz answers.
*   **Safety Guardrails:** Prevents prompt injection and handles input length limits.
*   **Telemetry:** Logs latency and request types to `telemetry.jsonl` for analysis.

---

## 🛠️ Tech Stack
*   **Frontend:** HTML, CSS, Vanilla JavaScript.
*   **Backend:** Python (Flask).
*   **LLM:** Google Gemini 1.5 Flash (via `google-generativeai`).
*   **Vector Store:** ChromaDB (using `all-MiniLM-L6-v2` embeddings).
*   **Testing:** Python `requests` for offline evaluation.

---

## 📦 Installation & Setup

### 1. Prerequisites
*   Python 3.10 or higher.
*   A Google Gemini API Key (Free).

### 2. Clone & Install
```bash

# Install dependencies
pip install -r requirements.txt
```
### 3. Configure API Key

Create a file named .env in the root folder and add your key:
```
GEMINI_API_KEY=your_actual_api_key_here
```
### 4. Ingest Data (Important!)

You must run this once to populate the vector database.

```bash

python ingest.py
```
Output should say: `Stored 5 chunks.`

### ▶️ How to Run
Start the Server
```Bash
 
python app.py
```

Open your browser to http://127.0.0.1:5000.

### Usage

1. Topic: Type a relevant term (e.g., "Layers of the Earth").
2. Make Notes: Click to get a summary.
3. Quiz Me: Click to generate a dynamic multiple-choice question.
4. Video: Watch videos based on the topic that you want more information on.

### 🧪 Evaluation

Run the offline test suite to verify the LLM's accuracy and JSON formatting.

```bash

python tests/evaluate.py
```

📂 Project Structure
```code Text

study-buddy/
├── app.py                  # Main Flask application
├── ingest.py               # RAG Indexing script
├── requirements.txt        # Python dependencies
├── .env                    # API Keys (Not committed to git)
├── data/
│   └── vector_db/          # ChromaDB storage (created after ingest)
├── static/                 # CSS & JS
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html          # Main UI
└── tests/
    ├── evaluate.py         # Automated testing script
    └── tests.json          # Test cases

```
  

🛡️ Safety & Limitations

- Guardrails: Inputs > 300 characters are rejected. Phrases like "ignore previous instructions" trigger a refusal. Context material is limited to character count between 50 and 50,000.

- Limit: The context window is currently limited to the top 2 relevant chunks from the provided chapter.

- JSON Robustness: The app includes error handling to catch malformed JSON responses from the LLM.
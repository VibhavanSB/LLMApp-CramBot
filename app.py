import os, time, json, logging, re

from flask import Flask, request, render_template, jsonify
import ingest
import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from youtube_search import YoutubeSearch

load_dotenv()

app = Flask(__name__)

# --- CONFIG ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./data/vector_db")
collection = chroma_client.get_collection(name="study_docs", embedding_function=emb_fn)

logging.basicConfig(filename='telemetry.jsonl', level=logging.INFO, format='%(message)s')

# --- PROMPTS ---
NOTES_SYSTEM = """
You are a strict study tutor. 
Based on the Context provided, generate concise bullet-point study notes.
If the information is missing, state that clearly.
"""

# We ask for JSON specifically here
QUIZ_SYSTEM = """
You are a quiz generator. Based on the Context provided, generate ONE multiple-choice question.
You MUST output strictly valid JSON in this format:
{
  "question": "The question text?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": "Option A",
  "explanation": "Why A is correct."
}
Do not include markdown formatting like ```json. Just raw JSON.
"""


def is_unsafe(query):
    if len(query) > 300: return True
    if "ignore previous" in query.lower(): return True
    return False


# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/learn', methods=['POST'])
def learn():
    data = request.json
    text = data.get('text' ,'')

    if len(text) > 50000:
        return jsonify({"error": "Text is too long. Please keep it under 50000 characters."}), 400
    if len(text) < 50:
        return jsonify({"error": "Text is too short. Please provide more context."}), 400

    try:
        count = ingest.ingest_data(text)
        return jsonify({"message": f"Successfully learned {count} chunks of data!"})
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to process text."}), 500
@app.route('/generate', methods=['POST'])
def generate():
    start = time.time()
    data = request.json
    topic = data.get('topic', '')
    mode = data.get('mode', 'notes')

    if is_unsafe(topic): return jsonify({"error": "Unsafe input"}), 400

    if mode == 'video':
        results = YoutubeSearch(topic + "astronomy", max_results=5).to_dict()

        if results:
            video_id = results[0]['id']
            title = results[0]['title']

            embed_url = f"https://www.youtube-nocookie.com/embed/{video_id}"

            content = {
                "title": title,
                "id": video_id,
                "url": embed_url
            }

        else:
            return jsonify({"error": "No video found."}), 404

        return jsonify({"content": content})

    try:
        # RAG
        results = collection.query(query_texts=[topic], n_results=2)
        context = "\n\n".join(results['documents'][0])

        if mode == 'notes':
            prompt = f"{NOTES_SYSTEM}\n\nContext:\n{context}\n\nTopic: {topic}"
            resp = model.generate_content(prompt)
            content = resp.text
        else:
            # Quiz Mode
            prompt = f"{QUIZ_SYSTEM}\n\nContext:\n{context}\n\nTopic: {topic}"
            resp = model.generate_content(prompt)
            # Clean up markdown code blocks if LLM adds them
            raw_text = resp.text.replace("```json", "").replace("```", "").strip()
            content = json.loads(raw_text)  # Parse JSON

            return jsonify({"content": content}), 200
        # Telemetry
        logging.info(json.dumps({
            "time": time.time(),
            "latency": round(time.time() - start, 2),
            "mode": mode,
            "topic": topic
        }))

        return jsonify({"content": content})

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to generate valid quiz format. Try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("-----------------------------------------------")
    print("CramBot is starting up...")
    print("Open http://localhost:5000")
    print("-----------------------------------------------")
    app.run(port=5000, debug=True)
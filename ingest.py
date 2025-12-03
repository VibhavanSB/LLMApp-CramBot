import chromadb
from chromadb.utils import embedding_functions

PERSIST_DIR = "./data/vector_db"
client = chromadb.PersistentClient(path=PERSIST_DIR)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(name="study_docs", embedding_function=emb_fn)


def ingest_data(text):
    existing_ids = collection.get()['ids']
    if existing_ids:
        collection.delete(ids=existing_ids)

    # Split by double newlines to get sections
    chunks = [c.strip() for c in text.split('\n\n') if c.strip()]

    if not chunks:
        return 0

    ids = [f"id_{i}" for i in range(len(chunks))]
    metadatas = [{"source": "user_upload"} for _ in chunks]

    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    print(f"Stored {len(chunks)} chunks.")

    return len(chunks)


if __name__ == "__main__":
    ingest_data()


from pathlib import Path
import chromadb

BASE_DIR = Path(__file__).resolve().parents[1]
VECTOR_DB_PATH = BASE_DIR / "vector_db"

client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
collection = client.get_collection("documents")

data = collection.get(include=["metadatas"], limit=1)

print(data["metadatas"][0])

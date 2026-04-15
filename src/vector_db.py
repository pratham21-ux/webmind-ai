import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

class VectorDB:
    def __init__(self, collection_name="webmind_knowledge_base"):
        # STEP 1: Initialize the Embedding Model
        # Using a fast, lightweight model perfect for general web text
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = collection_name
        
        # STEP 2: Initialize Qdrant (In-Memory for easy testing)
        self.client = QdrantClient(":memory:") 
        
        self._setup_collection()

    def _setup_collection(self):
        """Checks and creates a collection using cosine similarity."""
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            print(f"✅ Collection '{self.collection_name}' initialized.")

    def add_to_index(self, chunks, source_url):
        """Generates embeddings and stores them in Qdrant with payload metadata."""
        points = []
        print(f"🧠 Generating embeddings for {len(chunks)} chunks...")
        
        for text in chunks:
            vector = self.model.encode(text).tolist()
            point_id = str(uuid.uuid4())
            points.append(PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "text": text, 
                    "source": source_url
                }
            ))
            
        self.client.upsert(collection_name=self.collection_name, points=points)
        print(f"📥 Successfully indexed {len(chunks)} facts.")

    def query(self, user_text, limit=5):
        """
        Converts the user query to a vector and performs a semantic search.
        """
        query_vector = self.model.encode(user_text).tolist()
        
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        )
        return response.points

# --- UNIVERSAL TEST EXECUTION ---
if __name__ == "__main__":
    db = VectorDB()
    
    # Sample Universal Facts
    facts = [
        "WebMind AI is built using Python and Streamlit for the frontend UI.",
        "Qdrant is utilized as the vector database for high-speed semantic retrieval.",
        "The system processes dynamic React websites by using Playwright instead of basic HTTP requests."
    ]
    
    db.add_to_index(facts, "https://webmind.docs/architecture")
    
    print("\n🔍 Testing Semantic Retrieval...")
    # Semantic search test: 'interface' is not in the facts, but 'UI' is.
    results = db.query("What framework is used for the interface?", limit=1)
    
    for hit in results:
        print(f"Score: {hit.score:.4f} | Data: {hit.payload['text']}")
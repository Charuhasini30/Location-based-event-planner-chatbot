import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer


load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

model = SentenceTransformer("all-mpnet-base-v2")

def save_memory(user_id, user_input, bot_reply):
   
    combined_message = f"{user_input}|||{bot_reply}"

   
    vector = {
        "id": f"{user_id}-{hash(user_input)}",  
        "values": model.encode(user_input).tolist(),  
        "metadata": {
            "user_id": user_id,  
            "message": combined_message  
        }
    }

   
    index.upsert(vectors=[vector])

def retrieve_memory(user_id, query, top_k=5):
   
    query_embedding = model.encode(query).tolist()

    
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    return [match["metadata"]["message"] for match in results["matches"]]


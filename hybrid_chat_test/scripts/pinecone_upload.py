import json
import openai
from pinecone import Pinecone, ServerlessSpec
from tqdm import tqdm
import config

# Initialize clients
openai.api_key = config.OPENAI_API_KEY
pc = Pinecone(api_key=config.PINECONE_API_KEY)

DATA_FILE = "vietnam_travel_dataset.json"

def main():
    # Create index if doesn't exist
    if config.PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating Pinecone index '{config.PINECONE_INDEX_NAME}'...")
        pc.create_index(
            name=config.PINECONE_INDEX_NAME,
            dimension=config.PINECONE_VECTOR_DIM,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region=config.PINECONE_ENV
            )
        )
        print("✓ Index created!")
    else:
        print(f"✓ Index '{config.PINECONE_INDEX_NAME}' already exists")

    # Connect to index
    index = pc.Index(config.PINECONE_INDEX_NAME)

    # Load data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Uploading {len(data)} items to Pinecone...")
    
    # Batch process for efficiency
    batch_size = 100
    vectors_to_upsert = []
    
    for item in tqdm(data, desc="Processing items"):
        # Create text to embed
        text_parts = [
            item.get('name', ''),
            item.get('type', ''),
            item.get('description', ''),
            item.get('semantic_text', ''),
            ' '.join(item.get('tags', []))
        ]
        text = ' '.join(filter(None, text_parts))
        
        # Get embedding from OpenAI
        try:
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embedding = response.data[0].embedding
            
            # Prepare metadata
            metadata = {
                'name': item.get('name', ''),
                'type': item.get('type', ''),
                'description': item.get('description', '')[:500],  # Pinecone metadata limit
                'region': item.get('region', ''),
                'tags': ','.join(item.get('tags', []))
            }
            
            vectors_to_upsert.append((
                item['id'],
                embedding,
                metadata
            ))
            
            # Upload in batches
            if len(vectors_to_upsert) >= batch_size:
                index.upsert(vectors=vectors_to_upsert)
                vectors_to_upsert = []
                
        except Exception as e:
            print(f"Error processing {item['id']}: {e}")
            continue
    
    # Upload remaining vectors
    if vectors_to_upsert:
        index.upsert(vectors=vectors_to_upsert)
    
    # Get stats
    stats = index.describe_index_stats()
    print(f"✓ Done! Total vectors in index: {stats['total_vector_count']}")

if __name__ == "__main__":
    main()
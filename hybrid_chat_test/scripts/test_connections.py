import config
from neo4j import GraphDatabase
from pinecone import Pinecone
import openai

print("Testing connections...\n")

# Test Neo4j
print("1. Testing Neo4j...")
try:
    driver = GraphDatabase.driver(
        config.NEO4J_URI,
        auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    )
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        count = result.single()["count"]
        print(f"   ✓ Neo4j connected! Found {count} nodes")
    driver.close()
except Exception as e:
    print(f"   ✗ Neo4j error: {e}")

# Test Pinecone
print("\n2. Testing Pinecone...")
try:
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    index = pc.Index(config.PINECONE_INDEX_NAME)
    stats = index.describe_index_stats()
    print(f"   ✓ Pinecone connected! Found {stats['total_vector_count']} vectors")
except Exception as e:
    print(f"   ✗ Pinecone error: {e}")

# Test OpenAI
print("\n3. Testing OpenAI...")
try:
    openai.api_key = config.OPENAI_API_KEY
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input="test"
    )
    print(f"   ✓ OpenAI connected! Embedding dimension: {len(response.data[0].embedding)}")
except Exception as e:
    print(f"   ✗ OpenAI error: {e}")

print("\n✓ All systems ready!")
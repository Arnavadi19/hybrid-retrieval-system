import json
from hybrid_chat import HybridChatSystem

# Define test queries covering different scenarios
TEST_QUERIES = [
    # Graph queries (structural/factual)
    {
        "id": "conv_001",
        "category": "graph",
        "complexity": "low",
        "query": "What hotels are in Hanoi?",
        "expected_sources": ["neo4j"]
    },
    {
        "id": "conv_002",
        "category": "graph",
        "complexity": "low",
        "query": "Show me attractions in Hoi An",
        "expected_sources": ["neo4j"]
    },
    {
        "id": "conv_003",
        "category": "graph",
        "complexity": "medium",
        "query": "List restaurants in Da Nang",
        "expected_sources": ["neo4j"]
    },
    
    # Semantic queries (meaning-based)
    {
        "id": "conv_004",
        "category": "semantic",
        "complexity": "medium",
        "query": "Find romantic hotels for honeymoon",
        "expected_sources": ["pinecone"]
    },
    {
        "id": "conv_005",
        "category": "semantic",
        "complexity": "medium",
        "query": "Recommend peaceful mountain retreats",
        "expected_sources": ["pinecone"]
    },
    {
        "id": "conv_006",
        "category": "semantic",
        "complexity": "medium",
        "query": "Best places for traditional Vietnamese culture",
        "expected_sources": ["pinecone"]
    },
    {
        "id": "conv_007",
        "category": "semantic",
        "complexity": "high",
        "query": "Luxury beachside resorts with spa facilities",
        "expected_sources": ["pinecone"]
    },
    
    # Hybrid queries (need both)
    {
        "id": "conv_008",
        "category": "hybrid",
        "complexity": "high",
        "query": "Plan a romantic 3-day trip in Hoi An",
        "expected_sources": ["neo4j", "pinecone"]
    },
    {
        "id": "conv_009",
        "category": "hybrid",
        "complexity": "high",
        "query": "Recommend authentic food experiences in Hanoi",
        "expected_sources": ["neo4j", "pinecone"]
    },
    {
        "id": "conv_010",
        "category": "hybrid",
        "complexity": "high",
        "query": "Find budget-friendly hotels near beaches in Da Nang",
        "expected_sources": ["neo4j", "pinecone"]
    },
    
    # Edge cases
    {
        "id": "conv_011",
        "category": "edge",
        "complexity": "low",
        "query": "Tell me about Vietnam",
        "expected_sources": ["neo4j", "pinecone"]
    },
    {
        "id": "conv_012",
        "category": "edge",
        "complexity": "medium",
        "query": "What's the best time to visit Sapa?",
        "expected_sources": ["neo4j"]
    }
]

def generate_conversations():
    """Generate responses for all test queries"""
    chat = HybridChatSystem()
    conversations = []
    
    print("Generating test conversations...\n")
    
    for test in TEST_QUERIES:
        print(f"Processing: {test['query']}")
        result = chat.query(test['query'])
        
        conversation = {
            **test,
            "response": result["answer"],
            "actual_sources": result["sources"],
            "raw_results": result["raw_results"]
        }
        conversations.append(conversation)
    
    # Save to file
    with open('test_conversations.json', 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Generated {len(conversations)} test conversations")
    print("✓ Saved to test_conversations.json")
    
    chat.close()
    return conversations

if __name__ == "__main__":
    generate_conversations()
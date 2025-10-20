from neo4j import GraphDatabase
from pinecone import Pinecone
import openai
import config
from typing import Dict, List, Tuple

class HybridChatSystem:
    def __init__(self):
        # Connect to Neo4j
        self.neo4j_driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
        
        # Connect to Pinecone
        pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self.pinecone_index = pc.Index(config.PINECONE_INDEX_NAME)
        
        # Set OpenAI key
        openai.api_key = config.OPENAI_API_KEY
        
        self.last_sources_used = []
    
    def query(self, user_question: str, top_k: int = 5) -> Dict:
        """
        Main query method that decides which database(s) to use
        Returns: dict with answer and sources
        """
        query_type = self._classify_query(user_question)
        
        if query_type == "graph":
            results = self._query_neo4j(user_question, top_k)
            self.last_sources_used = ["neo4j"]
            return {
                "answer": self._format_neo4j_results(results),
                "sources": ["neo4j"],
                "raw_results": results
            }
        
        elif query_type == "semantic":
            results = self._query_pinecone(user_question, top_k)
            self.last_sources_used = ["pinecone"]
            return {
                "answer": self._format_pinecone_results(results),
                "sources": ["pinecone"],
                "raw_results": results
            }
        
        else:  # hybrid
            neo4j_results = self._query_neo4j(user_question, top_k)
            pinecone_results = self._query_pinecone(user_question, top_k)
            self.last_sources_used = ["neo4j", "pinecone"]
            return {
                "answer": self._merge_results(neo4j_results, pinecone_results),
                "sources": ["neo4j", "pinecone"],
                "raw_results": {
                    "neo4j": neo4j_results,
                    "pinecone": pinecone_results
                }
            }
    
    def _classify_query(self, question: str) -> str:
        """Classify query type based on keywords"""
        q_lower = question.lower()
        
        # Graph indicators (relationships, structure)
        graph_keywords = ['in', 'near', 'connected to', 'located in', 
                         'from', 'to', 'what are', 'list', 'show me']
        
        # Semantic indicators (meaning, qualities)
        semantic_keywords = ['romantic', 'best', 'recommend', 'like', 
                            'similar', 'peaceful', 'authentic', 'traditional',
                            'budget', 'luxury', 'family-friendly']
        
        # Hybrid indicators (complex queries)
        hybrid_keywords = ['plan', 'itinerary', 'trip', 'visit', 'combination']
        
        graph_score = sum(1 for kw in graph_keywords if kw in q_lower)
        semantic_score = sum(1 for kw in semantic_keywords if kw in q_lower)
        hybrid_score = sum(1 for kw in hybrid_keywords if kw in q_lower)
        
        if hybrid_score > 0:
            return "hybrid"
        elif semantic_score > graph_score:
            return "semantic"
        else:
            return "graph"
    
    def _query_neo4j(self, question: str, limit: int = 5) -> List[Dict]:
        """Query Neo4j graph database"""
        city_name = self._extract_city(question)
        entity_type = self._extract_type(question)
        
        with self.neo4j_driver.session() as session:
            # Try to find entities by city and type
            if city_name and entity_type:
                query = """
                MATCH (e:Entity)-[:Located_In]->(c:City)
                WHERE c.name CONTAINS $city AND e.type = $type
                RETURN e.id as id, e.name as name, e.type as type, 
                       e.description as description, c.name as city
                LIMIT $limit
                """
                result = session.run(query, city=city_name, type=entity_type, limit=limit)
            elif city_name:
                query = """
                MATCH (e:Entity)-[:Located_In]->(c:City)
                WHERE c.name CONTAINS $city
                RETURN e.id as id, e.name as name, e.type as type,
                       e.description as description, c.name as city
                LIMIT $limit
                """
                result = session.run(query, city=city_name, limit=limit)
            elif entity_type:
                query = """
                MATCH (e:Entity)
                WHERE e.type = $type
                RETURN e.id as id, e.name as name, e.type as type,
                       e.description as description
                LIMIT $limit
                """
                result = session.run(query, type=entity_type, limit=limit)
            else:
                # Fallback: return random entities
                query = """
                MATCH (e:Entity)
                RETURN e.id as id, e.name as name, e.type as type,
                       e.description as description
                LIMIT $limit
                """
                result = session.run(query, limit=limit)
            
            return [dict(record) for record in result]
    
    def _query_pinecone(self, question: str, top_k: int = 5) -> List[Dict]:
        """Query Pinecone vector database"""
        # Create embedding for question
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=question
        )
        query_embedding = response.data[0].embedding
        
        # Search Pinecone
        results = self.pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        return [
            {
                "id": match.id,
                "score": match.score,
                "name": match.metadata.get("name", ""),
                "type": match.metadata.get("type", ""),
                "description": match.metadata.get("description", ""),
                "region": match.metadata.get("region", "")
            }
            for match in results.matches
        ]
    
    def _extract_city(self, question: str) -> str:
        """Extract city name from question"""
        cities = ['Hanoi', 'Ha Long', 'Sapa', 'Hue', 'Hoi An', 
                  'Da Nang', 'Nha Trang', 'Da Lat', 'Ho Chi Minh', 'Mekong']
        q_lower = question.lower()
        for city in cities:
            if city.lower() in q_lower:
                return city
        return ""
    
    def _extract_type(self, question: str) -> str:
        """Extract entity type from question"""
        types = {
            'hotel': 'Hotel',
            'hotels': 'Hotel',
            'attraction': 'Attraction',
            'attractions': 'Attraction',
            'restaurant': 'Restaurant',
            'restaurants': 'Restaurant',
            'activity': 'Activity',
            'activities': 'Activity',
            'tour': 'Tour',
            'tours': 'Tour'
        }
        q_lower = question.lower()
        for keyword, entity_type in types.items():
            if keyword in q_lower:
                return entity_type
        return ""
    
    def _format_neo4j_results(self, results: List[Dict]) -> str:
        """Format Neo4j results into readable text"""
        if not results:
            return "No results found in the graph database."
        
        answer = f"Found {len(results)} results:\n\n"
        for i, item in enumerate(results, 1):
            answer += f"{i}. {item.get('name', 'Unknown')}\n"
            answer += f"   Type: {item.get('type', 'N/A')}\n"
            if 'city' in item:
                answer += f"   Location: {item['city']}\n"
            answer += f"   Description: {item.get('description', 'N/A')}\n\n"
        return answer
    
    def _format_pinecone_results(self, results: List[Dict]) -> str:
        """Format Pinecone results into readable text"""
        if not results:
            return "No results found in the semantic search."
        
        answer = f"Found {len(results)} relevant results:\n\n"
        for i, item in enumerate(results, 1):
            answer += f"{i}. {item.get('name', 'Unknown')} (Relevance: {item['score']:.2f})\n"
            answer += f"   Type: {item.get('type', 'N/A')}\n"
            answer += f"   Region: {item.get('region', 'N/A')}\n"
            answer += f"   Description: {item.get('description', 'N/A')}\n\n"
        return answer
    
    def _merge_results(self, neo4j_results: List[Dict], pinecone_results: List[Dict]) -> str:
        """Merge and format results from both databases"""
        answer = "Based on both structured data and semantic search:\n\n"
        
        if neo4j_results:
            answer += "=== From Graph Database ===\n"
            for i, item in enumerate(neo4j_results[:3], 1):
                answer += f"{i}. {item.get('name', 'Unknown')} - {item.get('type', 'N/A')}\n"
        
        answer += "\n"
        
        if pinecone_results:
            answer += "=== Semantically Similar ===\n"
            for i, item in enumerate(pinecone_results[:3], 1):
                answer += f"{i}. {item.get('name', 'Unknown')} (Score: {item['score']:.2f})\n"
        
        return answer
    
    def get_last_sources_used(self) -> List[str]:
        """Return which databases were used in the last query"""
        return self.last_sources_used
    
    def close(self):
        """Close database connections"""
        self.neo4j_driver.close()


if __name__ == "__main__":
    # Test the system
    chat = HybridChatSystem()
    
    print("=== Test 1: Graph Query ===")
    result = chat.query("Show me hotels in Hanoi")
    print(result["answer"])
    print(f"Sources: {result['sources']}\n")
    
    print("=== Test 2: Semantic Query ===")
    result = chat.query("Find romantic places for couples")
    print(result["answer"])
    print(f"Sources: {result['sources']}\n")
    
    print("=== Test 3: Hybrid Query ===")
    result = chat.query("Plan a beach vacation in Da Nang")
    print(result["answer"])
    print(f"Sources: {result['sources']}\n")
    
    chat.close()
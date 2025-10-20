import json
from typing import Dict, List
import statistics

class AutomatedEvaluator:
    def __init__(self):
        self.criteria_weights = {
            "source_correctness": 0.3,
            "response_length": 0.2,
            "entity_count": 0.25,
            "query_match": 0.25
        }
    
    def evaluate_conversation(self, conv: Dict) -> Dict:
        """Automatically evaluate a conversation"""
        scores = {}
        
        # 1. Source Correctness (did it use the right database?)
        expected = set(conv['expected_sources'])
        actual = set(conv['actual_sources'])
        scores['source_correctness'] = 5.0 if expected == actual else 2.0
        
        # 2. Response Length (is response substantial?)
        response_length = len(conv['response'])
        if response_length > 500:
            scores['response_length'] = 5.0
        elif response_length > 300:
            scores['response_length'] = 4.0
        elif response_length > 150:
            scores['response_length'] = 3.0
        else:
            scores['response_length'] = 2.0
        
        # 3. Entity Count (did it return results?)
        entity_count = self._count_entities(conv)
        if entity_count >= 5:
            scores['entity_count'] = 5.0
        elif entity_count >= 3:
            scores['entity_count'] = 4.0
        elif entity_count >= 1:
            scores['entity_count'] = 3.0
        else:
            scores['entity_count'] = 1.0
        
        # 4. Query Match (does response relate to query?)
        scores['query_match'] = self._calculate_query_match(conv)
        
        # Calculate weighted overall score
        overall = sum(
            scores[metric] * self.criteria_weights[metric]
            for metric in scores
        )
        
        return {
            "conversation_id": conv['id'],
            "category": conv['category'],
            "scores": {**scores, "overall": overall},
            "analysis": self._generate_analysis(conv, scores)
        }
    
    def _count_entities(self, conv: Dict) -> int:
        """Count entities in response"""
        response = conv['response'].lower()
        # Count numbered items (1., 2., 3., etc.)
        import re
        matches = re.findall(r'^\d+\.', response, re.MULTILINE)
        return len(matches)
    
    def _calculate_query_match(self, conv: Dict) -> float:
        """Check if response addresses query keywords"""
        query_words = set(conv['query'].lower().split())
        response_words = set(conv['response'].lower().split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'what', 'show', 'find'}
        query_words -= common_words
        
        if not query_words:
            return 4.0
        
        # Calculate overlap
        overlap = len(query_words.intersection(response_words))
        match_rate = overlap / len(query_words)
        
        if match_rate >= 0.7:
            return 5.0
        elif match_rate >= 0.5:
            return 4.0
        elif match_rate >= 0.3:
            return 3.0
        else:
            return 2.0
    
    def _generate_analysis(self, conv: Dict, scores: Dict) -> str:
        """Generate automated feedback"""
        issues = []
        strengths = []
        
        if scores['source_correctness'] < 5.0:
            expected = conv['expected_sources']
            actual = conv['actual_sources']
            issues.append(f"Used {actual} instead of expected {expected}")
        else:
            strengths.append("Correct source selection")
        
        if scores['entity_count'] < 3.0:
            issues.append("Returned few or no results")
        elif scores['entity_count'] >= 4.0:
            strengths.append("Comprehensive results provided")
        
        if scores['query_match'] < 3.0:
            issues.append("Response may not fully address query")
        
        analysis = []
        if strengths:
            analysis.append("Strengths: " + ", ".join(strengths))
        if issues:
            analysis.append("Issues: " + ", ".join(issues))
        
        return " | ".join(analysis) if analysis else "Good performance"


def run_automated_evaluation():
    """Run automated evaluation on all test conversations"""
    # Load conversations
    with open('test_conversations.json', 'r') as f:
        conversations = json.load(f)
    
    evaluator = AutomatedEvaluator()
    evaluations = []
    
    print("Running automated evaluation...\n")
    
    for conv in conversations:
        eval_result = evaluator.evaluate_conversation(conv)
        evaluations.append(eval_result)
        
        print(f"{conv['id']}: {conv['query']}")
        print(f"  Overall Score: {eval_result['scores']['overall']:.2f}/5.0")
        print(f"  Analysis: {eval_result['analysis']}\n")
    
    # Save results
    with open('evaluation_results.json', 'w') as f:
        json.dump(evaluations, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    
    avg_overall = statistics.mean(e['scores']['overall'] for e in evaluations)
    print(f"Average Overall Score: {avg_overall:.2f}/5.0")
    
    # By category
    categories = {}
    for eval in evaluations:
        cat = eval['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(eval['scores']['overall'])
    
    print("\nBy Category:")
    for cat, scores in categories.items():
        print(f"  {cat}: {statistics.mean(scores):.2f}/5.0")
    
    print("\n✓ Results saved to evaluation_results.json")
    return evaluations


if __name__ == "__main__":
    run_automated_evaluation()
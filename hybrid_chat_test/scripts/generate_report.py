import json
import statistics
from datetime import datetime

# Load data
with open('evaluation_results.json', 'r') as f:
    evaluations = json.load(f)

with open('test_conversations.json', 'r') as f:
    conversations = json.load(f)

conv_map = {c['id']: c for c in conversations}

# Calculate statistics - updated for automated evaluation format
all_scores = {
    'source_correctness': [],
    'response_length': [],
    'entity_count': [],
    'query_match': [],
    'overall': []
}

for eval in evaluations:
    for metric, value in eval['scores'].items():
        if metric in all_scores:
            all_scores[metric].append(value)

# Generate Markdown Report
report = f"""# AI Hybrid Chat System Evaluation Report

**Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Total Conversations Evaluated**: {len(evaluations)}  
**Evaluation Method**: Automated

---

## Executive Summary

This report evaluates a hybrid chatbot system that combines Neo4j graph database for structured queries and Pinecone vector database for semantic search. The system was tested on {len(evaluations)} diverse queries spanning factual lookups, semantic searches, and complex hybrid queries.

### Key Findings

- **Overall Performance**: {statistics.mean(all_scores['overall']):.2f}/5.0
- **Source Correctness**: {statistics.mean(all_scores['source_correctness']):.2f}/5.0
- **Response Quality**: {statistics.mean(all_scores['response_length']):.2f}/5.0
- **Entity Coverage**: {statistics.mean(all_scores['entity_count']):.2f}/5.0
- **Query Relevance**: {statistics.mean(all_scores['query_match']):.2f}/5.0

---

## Methodology

### System Architecture

The hybrid chat system integrates:
1. **Neo4j Graph Database**: Stores entities (cities, hotels, attractions, restaurants) and their relationships
2. **Pinecone Vector Database**: Stores semantic embeddings for meaning-based search
3. **Query Classifier**: Determines which database(s) to use based on query characteristics

### Test Dataset

- **Graph Queries**: {len([c for c in conversations if c['category'] == 'graph'])} queries testing structured data retrieval
- **Semantic Queries**: {len([c for c in conversations if c['category'] == 'semantic'])} queries testing meaning-based search
- **Hybrid Queries**: {len([c for c in conversations if c['category'] == 'hybrid'])} queries requiring both databases
- **Edge Cases**: {len([c for c in conversations if c['category'] == 'edge'])} queries testing boundary conditions

### Evaluation Criteria

The automated evaluation system assessed each conversation across four dimensions:

1. **Source Correctness** (30% weight): Whether the system correctly identified which database(s) to query
2. **Response Length** (20% weight): Whether the response provided substantial information
3. **Entity Count** (25% weight): Number of relevant entities returned in the response
4. **Query Match** (25% weight): Semantic relevance of the response to the original query

Each metric was scored on a 1-5 scale, with a weighted average producing the overall score.

---

## Results by Category

"""

# Add category breakdown
categories = {}
for eval in evaluations:
    cat = eval['category']
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(eval['scores']['overall'])

for category, scores in sorted(categories.items()):
    avg = statistics.mean(scores)
    report += f"### {category.upper()} Queries\n\n"
    report += f"- Average Score: **{avg:.2f}/5.0**\n"
    report += f"- Query Count: {len(scores)}\n"
    
    # Get sample queries from this category
    cat_evals = [e for e in evaluations if e['category'] == category]
    if cat_evals:
        best = max(cat_evals, key=lambda x: x['scores']['overall'])
        conv = conv_map[best['conversation_id']]
        report += f"- Best Performing: \"{conv['query']}\" ({best['scores']['overall']:.2f}/5)\n"
    report += "\n"

# Source usage analysis
report += "---\n\n## Source Selection Analysis\n\n"

correct_sources = 0
source_issues = []

for eval in evaluations:
    conv = conv_map[eval['conversation_id']]
    expected = set(conv['expected_sources'])
    actual = set(conv['actual_sources'])
    
    if expected == actual:
        correct_sources += 1
    else:
        source_issues.append({
            'id': conv['id'],
            'query': conv['query'],
            'expected': list(expected),
            'actual': list(actual),
            'score': eval['scores']['source_correctness']
        })

report += f"**Correct Source Selection**: {correct_sources}/{len(evaluations)} ({correct_sources/len(evaluations)*100:.1f}%)\n\n"

if source_issues:
    report += "### Source Selection Issues\n\n"
    report += "| Query | Expected | Actual | Impact |\n"
    report += "|-------|----------|--------|--------|\n"
    for issue in source_issues:
        report += f"| {issue['query'][:40]}... | {', '.join(issue['expected'])} | {', '.join(issue['actual'])} | {issue['score']:.1f}/5 |\n"
    report += "\n"

# Performance metrics breakdown
report += "---\n\n## Performance Metrics Breakdown\n\n"

metrics_table = """| Metric | Average Score | Min | Max | Std Dev |
|--------|---------------|-----|-----|---------|
"""

for metric in ['source_correctness', 'response_length', 'entity_count', 'query_match']:
    scores = all_scores[metric]
    metrics_table += f"| {metric.replace('_', ' ').title()} | {statistics.mean(scores):.2f} | {min(scores):.2f} | {max(scores):.2f} | {statistics.stdev(scores):.2f} |\n"

report += metrics_table + "\n"

# Detailed conversation analysis
report += "---\n\n## Detailed Conversation Analysis\n\n"

for eval in evaluations:
    conv = conv_map[eval['conversation_id']]
    report += f"### {conv['id']}: {conv['query']}\n\n"
    report += f"**Category**: {conv['category']} | **Complexity**: {conv['complexity']}\n\n"
    report += f"**Scores**:\n"
    report += f"- Source Correctness: {eval['scores']['source_correctness']:.1f}/5\n"
    report += f"- Response Length: {eval['scores']['response_length']:.1f}/5\n"
    report += f"- Entity Count: {eval['scores']['entity_count']:.1f}/5\n"
    report += f"- Query Match: {eval['scores']['query_match']:.1f}/5\n"
    report += f"- **Overall: {eval['scores']['overall']:.2f}/5**\n\n"
    
    report += f"**Analysis**: {eval['analysis']}\n\n"
    report += f"**Expected Sources**: {', '.join(conv['expected_sources'])}\n\n"
    report += f"**Actual Sources**: {', '.join(conv['actual_sources'])}\n\n"
    
    # Show truncated response
    response_preview = conv['response'][:200] + "..." if len(conv['response']) > 200 else conv['response']
    report += f"**Response Preview**: {response_preview}\n\n"
    report += "---\n\n"

# Strengths and weaknesses
report += "## Key Strengths\n\n"

top_performers = sorted(evaluations, key=lambda x: x['scores']['overall'], reverse=True)[:3]
for i, eval in enumerate(top_performers, 1):
    conv = conv_map[eval['conversation_id']]
    report += f"{i}. **{conv['query']}** (Score: {eval['scores']['overall']:.2f}/5)\n"
    report += f"   - Category: {conv['category']}\n"
    report += f"   - {eval['analysis']}\n\n"

report += "## Areas for Improvement\n\n"

low_performers = sorted(evaluations, key=lambda x: x['scores']['overall'])[:3]
for i, eval in enumerate(low_performers, 1):
    conv = conv_map[eval['conversation_id']]
    report += f"{i}. **{conv['query']}** (Score: {eval['scores']['overall']:.2f}/5)\n"
    report += f"   - Category: {conv['category']}\n"
    report += f"   - {eval['analysis']}\n\n"

# Recommendations
report += """---

## Recommendations

### Query Classification Improvements
1. Enhance keyword detection for better source selection
2. Implement multi-word phrase matching for location names
3. Add context awareness for ambiguous queries
4. Consider query intent beyond simple pattern matching

### Neo4j Integration Enhancements
1. Expand relationship types in the graph schema
2. Implement fuzzy matching for city/location names
3. Add more sophisticated Cypher query templates
4. Include distance-based queries for proximity searches

### Pinecone Integration Enhancements
1. Fine-tune similarity score thresholds
2. Implement metadata filtering (price, ratings, region)
3. Add result re-ranking based on relevance
4. Consider hybrid scoring combining semantic and metadata

### Response Generation
1. Improve natural language formatting of results
2. Add context-aware explanations
3. Implement result summarization for large result sets
4. Include confidence scores in responses

### System Architecture
1. Add caching layer for frequently asked queries
2. Implement fallback mechanisms when primary source fails
3. Add query preprocessing and normalization
4. Consider feedback loop for continuous improvement

---

## Conclusion

The hybrid chat system demonstrates effective integration of graph and vector databases with an average performance of **{statistics.mean(all_scores['overall']):.2f}/5.0**. 

**Key Insights:**
- Source selection accuracy: {correct_sources/len(evaluations)*100:.1f}%
- Best performing category: {max(categories.items(), key=lambda x: statistics.mean(x[1]))[0]}
- Primary improvement area: Query classification and source routing

The system successfully handles structured queries through Neo4j and semantic queries through Pinecone, with room for enhancement in hybrid query processing and result integration.

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

# Save report
with open('EVALUATION_REPORT.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("✓ Report generated: EVALUATION_REPORT.md")

# Also create a summary JSON
summary = {
    "evaluation_date": datetime.now().isoformat(),
    "evaluation_method": "automated",
    "total_conversations": len(evaluations),
    "average_scores": {k: round(statistics.mean(v), 2) for k, v in all_scores.items()},
    "category_scores": {cat: round(statistics.mean(scores), 2) for cat, scores in categories.items()},
    "source_accuracy": round(correct_sources / len(evaluations), 2),
    "top_performers": [
        {
            "id": conv_map[e['conversation_id']]['id'],
            "query": conv_map[e['conversation_id']]['query'],
            "category": e['category'],
            "score": round(e['scores']['overall'], 2)
        }
        for e in sorted(evaluations, key=lambda x: x['scores']['overall'], reverse=True)[:3]
    ],
    "low_performers": [
        {
            "id": conv_map[e['conversation_id']]['id'],
            "query": conv_map[e['conversation_id']]['query'],
            "category": e['category'],
            "score": round(e['scores']['overall'], 2),
            "analysis": e['analysis']
        }
        for e in sorted(evaluations, key=lambda x: x['scores']['overall'])[:3]
    ]
}

with open('evaluation_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("✓ Summary saved: evaluation_summary.json")
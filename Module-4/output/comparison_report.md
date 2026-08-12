# Module-4 Retrieval Evaluation Report

## Objective

Evaluate different retrieval strategies and compare their effectiveness for enterprise document search.

---

# Evaluation Queries

The following queries were used:

1. What is Routing?
2. What is Orchestration?
3. Economic Scaffolding
4. Mixture of Agents
5. RouterBench

---

# Strategy Comparison

## 1. Semantic Search

Description:
Uses sentence embeddings to understand the meaning of the query.

Advantages:

- Understands semantic meaning.
- Retrieves conceptually similar text.
- Handles paraphrased queries.

Limitations:

- May miss exact keyword matches.
- Depends on embedding quality.

---

## 2. Keyword Search

Description:
Searches document chunks using exact keyword matching.

Advantages:

- Very fast.
- Finds exact words.
- Simple implementation.

Limitations:

- Cannot understand synonyms.
- Sensitive to wording.

---

## 3. Hybrid Search

Description:
Combines Semantic Search and Keyword Search.

Advantages:

- Higher retrieval accuracy.
- Better recall.
- Better precision.
- More robust than either approach alone.

Limitations:

- Slightly slower than individual search methods.

---

# Query Normalization

Examples:

Input:
What is Routing???

Normalized:
what is routing

Input:
Mixture-of-Agents

Normalized:
mixture of agents

Benefits:

- Removes punctuation.
- Standardizes casing.
- Improves keyword matching.

---

# Query Expansion

Examples:

Input:
routing

Expanded:
routing router route orchestration

Benefits:

- Improves recall.
- Retrieves related concepts.
- Handles aliases and synonyms.

Limitations:

- May retrieve additional unrelated results.

---

# Evaluation Summary

| Strategy        | Precision | Recall    | Semantic Understanding |
| --------------- | --------- | --------- | ---------------------- |
| Semantic Search | High      | High      | Excellent              |
| Keyword Search  | Medium    | Medium    | None                   |
| Hybrid Search   | Very High | Very High | Excellent              |

---

# Charts Generated

The following charts were generated:

- similarity_comparison.png
- retrieval_comparison.png
- pipeline_flow.png

---

# Final Conclusion

The implemented Hybrid Retrieval System combines semantic search, keyword search, query normalization, query expansion, and result re-ranking.

Among all retrieval strategies, Hybrid Search produced the most reliable and relevant results for enterprise document retrieval.

This implementation satisfies all objectives of Module-4:

- Structure-aware chunking
- Embedding generation
- Vector database storage
- Semantic retrieval
- Keyword retrieval
- Hybrid retrieval
- Query normalization
- Query expansion
- Result re-ranking
- Retrieval evaluation
- Visualization using charts
